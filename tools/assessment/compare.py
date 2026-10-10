"""Reproducible offline morphology comparison; outputs summaries, not a new corpus."""
import argparse
import collections
import gc
import hashlib
import json
import sqlite3
import time
from pathlib import Path
from readers import *

def digest(paradigms):
    h=hashlib.sha256();count=0;forms=0
    for row in paradigms:
        data=json.dumps(row,ensure_ascii=False,separators=(',',':')).encode()
        h.update(struct.pack('>I',len(data)));h.update(data);count+=1;forms+=len(row)
    return dict(lemmas=count,forms=forms,sha256=h.hexdigest())

def intern_tags(rows):
    pool={}
    for row in rows:
        yield [(word,pool.setdefault(frozenset(tags),tags)) for word,tags in row]

def historical(args):
    a=read_mrd(args.mrd);b=read_morph_json(args.morph);tags=read_gram_json(args.gram)
    report={field:dict(old=len(getattr(a,field)),new=len(getattr(b,field)),equal=getattr(a,field)==getattr(b,field)) for field in ('models','lemmas','accents','sessions','prefixes')}
    report['sessions_old_is_prefix']=b.sessions[:len(a.sessions)]==a.sessions
    def raw_expansion(source):
        for l in source.lemmas:
            yield [(e.prefix+l.stem+e.suffix,(e.code,l.common)) for e in source.models[l.model]]
    report['old_raw_expansion']=digest(raw_expansion(a))
    report['new_raw_expansion']=digest(raw_expansion(b))
    def missing_codes(source):
        used=collections.Counter(l.model for l in source.lemmas)
        common=collections.Counter(l.common for l in source.lemmas if l.common)
        # Match expand's strict code checks, including unused models and meta entries.
        return dict(
            missing_ending_codes=[dict(model=i,code=e.code,using_lemmas=used[i]) for i,m in enumerate(source.models) for e in m if e.code not in tags],
            missing_common_codes=[dict(code=code,using_lemmas=count) for code,count in sorted(common.items()) if code not in tags])
    report['semantic_validation']={name:missing_codes(source) for name,source in (('old',a),('new',b))}
    # Preserve the original MRD-only field for existing report consumers.
    report['missing_ending_codes']=report['semantic_validation']['old']['missing_ending_codes']
    report['semantic_import_status']='blocked' if any(codes for source in report['semantic_validation'].values() for codes in source.values()) else 'validated'
    report['prefix_sets_not_expanded']=sum(l.prefix_set is not None for l in a.lemmas)
    return report

def legacy(args):
    import itertools
    binary,_=read_binary(args.binary)
    source=read_mrd(args.mrd)
    tags=read_tab(args.tab,duplicate_policy=args.duplicate_policy)
    actual=intern_tags(expand(source,tags,prefix_policy=args.prefix_policy))
    count=0;different=0;ids=[]
    for lid,(a,b) in enumerate(itertools.zip_longest(binary,actual)):
        count+=1
        if a!=b:
            different+=1
            if len(ids)<20:ids.append(lid)
    return dict(compared_lemmas=count,different_ordered_paradigms=different,first_different_lemma_ids=ids,binary_digest=digest(binary))

def add_corpus(db,name,rows):
    db.execute(f'CREATE TABLE {name}(surface TEXT,lid INT,tid INT,lemma TEXT,tags BLOB,semantic BLOB)')
    db.execute(f'CREATE TABLE {name}_lemmas(lid INTEGER PRIMARY KEY,lemma TEXT,ordered TEXT,semantic TEXT,n INT)')
    n=0;count=0
    for lid,row in enumerate(rows):
        require(bool(row),'empty lemma');lemma=row[0][0]
        values=[(word,lid,tid,lemma,bytes(tags),bytes(sorted(tags))) for tid,(word,tags) in enumerate(row)]
        db.executemany(f'INSERT INTO {name} VALUES(?,?,?,?,?,?)',values)
        ordered=json.dumps(row,ensure_ascii=False,separators=(',',':'))
        semantic=json.dumps([(w,sorted(t)) for w,t in row],ensure_ascii=False,separators=(',',':'))
        db.execute(f'INSERT INTO {name}_lemmas VALUES(?,?,?,?,?)',(lid,lemma,hashlib.sha256(ordered.encode()).hexdigest(),hashlib.sha256(semantic.encode()).hexdigest(),len(row)))
        n+=1;count+=len(row)
        if n%50000==0:print(name,n,count,flush=True)
    db.commit()
    print(name,'indexing',flush=True)
    db.execute(f'CREATE INDEX {name}_surface ON {name}(surface)')
    db.execute(f'CREATE UNIQUE INDEX {name}_id ON {name}(lid,tid)')
    db.execute(f'CREATE INDEX {name}_signature ON {name}_lemmas(semantic)')
    db.commit()
    return dict(lemmas=n,forms=count)

def grouped(db,name):
    import itertools
    for word,rows in itertools.groupby(db.execute(f'SELECT surface,lemma,semantic,tags,lid,tid FROM {name} ORDER BY surface,lid,tid'),lambda r:r[0]):
        yield word,list(rows)

def corpus_diff(args):
    require(not Path(args.database).exists(),'refusing to overwrite existing assessment database')
    db=sqlite3.connect(args.database)
    db.execute('PRAGMA journal_mode=OFF');db.execute('PRAGMA synchronous=OFF');db.execute('PRAGMA cache_size=-131072')
    report={'prefix_policy':args.prefix_policy}
    source=read_morph_json(args.morph);tags=read_gram_json(args.gram)
    if args.prefix_policy=='reject':
        require(not any(l.prefix_set is not None for l in source.lemmas),'prefix sets require explicit --prefix-policy legacy-ignore')
    rows,refs=read_binary(args.binary);report['old']=add_corpus(db,'old',rows);del rows,refs;gc.collect()
    source=read_morph_json(args.morph);tags=read_gram_json(args.gram)
    report['new_source_lemmas']=len(source.lemmas)
    report['prefix_sets_not_expanded']=sum(l.prefix_set is not None for l in source.lemmas)
    report['meta_entries_filtered']=sum(l.stem.startswith('-') for l in source.lemmas)
    report['new']=add_corpus(db,'new',intern_tags(expand(source,tags,prefix_policy=args.prefix_policy)))
    a=iter(grouped(db,'old'));b=iter(grouped(db,'new'));x=next(a,None);y=next(b,None)
    c=collections.Counter();examples={}
    def bump(key,word):
        c[key]+=1
        if len(examples.setdefault(key,[]))<12:examples[key].append(word)
    while x is not None or y is not None:
        if y is None or (x is not None and x[0]<y[0]):bump('lost_forms',x[0]);x=next(a,None);continue
        if x is None or y[0]<x[0]:bump('added_forms',y[0]);y=next(b,None);continue
        word,ar=x;_,br=y;c['shared_forms']+=1
        ac=collections.Counter((r[1],r[2]) for r in ar);bc=collections.Counter((r[1],r[2]) for r in br)
        c['lost_analyses_on_shared_forms']+=sum((ac-bc).values());c['added_analyses_on_shared_forms']+=sum((bc-ac).values())
        if ac!=bc:bump('changed_semantic_analysis_multisets',word)
        elif collections.Counter((r[1],r[3]) for r in ar)!=collections.Counter((r[1],r[3]) for r in br):bump('tag_order_only_multiset_changes',word)
        else:c['same_ordered_tag_analysis_multisets']+=1
        x=next(a,None);y=next(b,None)
    report['forms']=dict(c);report['examples']=examples
    scalar=lambda sql:db.execute(sql).fetchone()[0]
    report['positional_ids']={
      'shared_numeric_ids':scalar('SELECT count(*) FROM old JOIN new USING(lid,tid)'),
      'same_surface_lemma_tag_set':scalar('SELECT count(*) FROM old o JOIN new n USING(lid,tid) WHERE o.surface=n.surface AND o.lemma=n.lemma AND o.semantic=n.semantic'),
      'same_surface_lemma_ordered_tags':scalar('SELECT count(*) FROM old o JOIN new n USING(lid,tid) WHERE o.surface=n.surface AND o.lemma=n.lemma AND o.tags=n.tags')}
    report['positional_ids']['reused_with_different_analysis']=report['positional_ids']['shared_numeric_ids']-report['positional_ids']['same_surface_lemma_tag_set']
    report['lemma_mapping']={
      'same_positional_semantic_paradigm':scalar('SELECT count(*) FROM old_lemmas o JOIN new_lemmas n USING(lid) WHERE o.semantic=n.semantic'),
      'old_paradigms_with_any_exact_semantic_match':scalar('SELECT count(*) FROM old_lemmas o WHERE EXISTS(SELECT 1 FROM new_lemmas n WHERE n.semantic=o.semantic)'),
      'old_paradigms_with_unique_new_match':scalar('SELECT count(*) FROM old_lemmas o WHERE (SELECT count(*) FROM new_lemmas n WHERE n.semantic=o.semantic)=1'),
      'old_paradigms_with_multiple_new_matches':scalar('SELECT count(*) FROM old_lemmas o WHERE (SELECT count(*) FROM new_lemmas n WHERE n.semantic=o.semantic)>1'),
      'bijective_exact_paradigm_matches':scalar('SELECT count(*) FROM old_lemmas o WHERE (SELECT count(*) FROM new_lemmas n WHERE n.semantic=o.semantic)=1 AND (SELECT count(*) FROM old_lemmas x WHERE x.semantic=o.semantic)=1')}
    report['lookup_order']='Not yet compared: lemma-order traversal is not the binary hash-reference order. No order-equivalence claim.'
    if args.queries:
        report['queries']=[]
        for q in Path(args.queries).read_text().splitlines():
            normalized=q.lower().replace('ё','е')
            counts={name:db.execute('SELECT count(*) FROM '+name+' WHERE surface=?',(normalized,)).fetchone()[0] for name in ('old','new')}
            report['queries'].append(dict(query=q,**counts))
    db.close();return report

def main():
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='command',required=True)
    h=sub.add_parser('historical');h.add_argument('--mrd',required=True)
    c=sub.add_parser('diff');c.add_argument('--binary',required=True);c.add_argument('--database',required=True);c.add_argument('--queries');c.add_argument('--prefix-policy',choices=('reject','legacy-ignore'),default='reject')
    for p in (h,c):
        p.add_argument('--morph',required=True);p.add_argument('--gram',required=True);p.add_argument('--output',required=True)
    l=sub.add_parser('legacy')
    for name in ('mrd','tab','binary','output'):l.add_argument('--'+name,required=True)
    l.add_argument('--prefix-policy',choices=('reject','legacy-ignore'),default='reject')
    l.add_argument('--duplicate-policy',choices=('reject','legacy-last-wins'),default='reject')
    args=parser.parse_args();start=time.monotonic()
    report={'historical':historical,'diff':corpus_diff,'legacy':legacy}[args.command](args)
    report['elapsed_seconds']=time.monotonic()-start
    report['inputs']={k:dict(path=str(v),sha256=hashlib.sha256(Path(v).read_bytes()).hexdigest()) for k,v in vars(args).items() if k in ('mrd','tab','morph','gram','binary','queries') and v}
    Path(args.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('Report:',args.output,flush=True)
    if args.command=='legacy' and report['different_ordered_paradigms']:
        raise SystemExit(1)

if __name__=='__main__':main()
