"""Write the first three experimental wire blocks from a local assessment DB."""
import argparse,sqlite3,struct
from pathlib import Path
from readers import require,normalize

def paradigms(db,table,policy):
    import itertools
    def rows(name):
        for lid,values in itertools.groupby(db.execute(f'SELECT lid,tid,surface,tags FROM {name} ORDER BY lid,tid'),lambda r:r[0]):
            yield lid,list(values)
    if policy=='sequential':
        yield from rows(table);return
    require(table=='new','stable-slot experiments require table new')
    from collections import defaultdict
    old={};new={}
    for name,out in [('old',old),('new',new)]:
        for lid,key in db.execute(f'SELECT lid,ordered FROM {name}_lemmas'):
            out.setdefault(key,[]).append(lid)
    matched_old=set();matched_new=set()
    for key,ids in old.items():
        if len(ids)==1 and len(new.get(key,[]))==1:
            matched_old.add(ids[0]);matched_new.add(new[key][0])
    next_id=0
    for lid,row in rows('old'):
        yield lid,row if policy=='retain-legacy' or lid in matched_old else []
        next_id=lid+1
    for lid,row in rows('new'):
        if lid not in matched_new:
            yield next_id,row;next_id+=1

def write_prefix(database,table,output,policy='sequential'):
    require(table in ('old','new'),'table must be old or new')
    require(policy in ('sequential','retain-legacy','tombstone'),'unknown stable-slot policy')
    require(not Path(output).exists(),'refusing to overwrite output')
    db=sqlite3.connect(f'file:{database}?mode=ro',uri=True)
    strings={};morphs={};morph_order=[];lemma_bytes=bytearray();count=0
    for lid,row in paradigms(db,table,policy):
        require(lid==count,'nonsequential lemma ID');lemma_bytes.extend(struct.pack('>i',len(row)))
        for tid,(_,actual_tid,word,tags) in enumerate(row):
            require(tid==actual_tid,'nonsequential transformation ID')
            key=frozenset(tags)
            if key not in morphs:morphs[key]=len(morphs);morph_order.append(tags)
            if word not in strings:normalize(word);strings[word]=len(strings)
            lemma_bytes.extend(struct.pack('>ii',strings[word],morphs[key]))
        count+=1
    with open(output,'xb') as f:
        def block(n,b):f.write(struct.pack('>ii',n,len(b)));f.write(b)
        block(len(morphs),b''.join(tags+b'd' for tags in morph_order))
        block(len(strings),b''.join(w.encode('cp1251')+b'd' for w in strings))
        block(count,lemma_bytes)
    return dict(morphologies=len(morphs),strings=len(strings),lemmas=count,prefix_bytes=Path(output).stat().st_size)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--database',required=True);p.add_argument('--table',choices=('old','new'),required=True);p.add_argument('--output',required=True);p.add_argument('--policy',choices=('sequential','retain-legacy','tombstone'),default='sequential')
    a=p.parse_args();print(write_prefix(a.database,a.table,a.output,a.policy))
