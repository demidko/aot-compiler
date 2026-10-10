"""Strict experimental readers. No input corpora or generated dictionaries are bundled."""
import gzip
import json
import re
import struct
from dataclasses import dataclass
from pathlib import Path

class FormatError(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise FormatError(message)

def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f'duplicate JSON key: {key}')
        result[key] = value
    return result

def load_json(path):
    with open(path, encoding='utf-8-sig') as stream:
        return json.load(stream, object_pairs_hook=unique_object)

def fields(obj, required, optional=()):
    require(isinstance(obj, dict), 'expected object')
    require(set(required) <= obj.keys(), f'missing fields: {set(required)-obj.keys()}')
    require(obj.keys() <= set(required) | set(optional), f'unknown fields: {obj.keys()-set(required)-set(optional)}')

def index(value, size, name):
    require(type(value) is int and 0 <= value < size, f'invalid {name} index: {value}')
    return value

@dataclass(frozen=True)
class Ending:
    suffix: str
    code: str
    prefix: str = ''

@dataclass(frozen=True)
class Lemma:
    stem: str
    model: int
    accent: int
    session: int
    common: str = ''
    prefix_set: int | None = None

@dataclass
class Source:
    models: list
    lemmas: list
    accents: list
    sessions: list
    prefixes: list

    def validate(self):
        for i, model in enumerate(self.models):
            require(bool(model), f'empty model {i}')
            require(not model[0].prefix, f'unsupported first-ending prefix in model {i}')
            for e in model:
                require(all(isinstance(v, str) for v in (e.suffix,e.code,e.prefix)), 'non-text ending')
                require(len(e.code) == 2, f'unsupported compound gramcode: {e.code!r}')
        for l in self.lemmas:
            index(l.model,len(self.models),'model')
            index(l.accent,len(self.accents),'accent')
            # MRD uses -1/65535 for unknown session; neither affects generated forms.
            if l.session not in (-1,65535): index(l.session,len(self.sessions),'session')
            if l.prefix_set is not None: index(l.prefix_set,len(self.prefixes),'prefix set')
            require(len(l.common) in (0,2), f'invalid common code: {l.common!r}')
        return self

def read_mrd(path):
    with open(path,encoding='utf-8-sig') as stream:
        def section():
            line=stream.readline(); require(bool(re.fullmatch(r'\d+\s*',line)), 'invalid MRD section count')
            result=[]
            for _ in range(int(line)):
                s=stream.readline(); require(bool(s),'truncated MRD section'); result.append(s.rstrip('\r\n'))
            return result
        model_lines, accent_lines, session_lines, prefix_lines, lemma_lines = (section() for _ in range(5))
        require(not stream.read().strip(),'trailing MRD content')
    models=[]
    for line in model_lines:
        # q//q introduces comments/wiki metadata, not flexions.
        line=line.split('q//q',1)[0]
        if not line.startswith('%'):
            metadata,sep,line=line.partition(';')
            require(bool(metadata) and bool(sep),'invalid wiki model metadata')
        require(line.startswith('%'),'model must start with %')
        model=[]
        for cell in line[1:].split('%'):
            parts=cell.split('*'); require(len(parts) in (2,3),'invalid MRD ending')
            model.append(Ending(*parts))
        models.append(model)
    lemmas=[]
    for line in lemma_lines:
        p=line.split();require(len(p)==6,'expected six MRD lemma fields')
        stem='' if p[0]=='#' else p[0]
        lemmas.append(Lemma(stem,int(p[1]),int(p[2]),int(p[3]),'' if p[4]=='-' else p[4],None if p[5]=='-' else int(p[5])))
    accents=[[int(x) for x in line.rstrip(';').split(';')] for line in accent_lines]
    sessions=[]
    for line in session_lines:
        p=line.split(';');require(len(p)==3,'invalid session');sessions.append(dict(zip(('user','start','last_save'),p)))
    prefixes=[sorted(x.strip() for x in line.split(',')) for line in prefix_lines]
    return Source(models,lemmas,accents,sessions,prefixes).validate()

def read_morph_json(path):
    d=load_json(path);fields(d,('flexia_models','lemmas','accent_models','sessions','prefix_sets'))
    models=[]
    for m in d['flexia_models']:
        fields(m,('endings',),('comments','wiki'))
        model=[]
        for e in m['endings']:
            fields(e,('flexia','gramcode'),('prefix',))
            model.append(Ending(e['flexia'],e['gramcode'],e.get('prefix','')))
        require(model and not model[0].prefix,'empty model or unsupported first-ending prefix')
        models.append(model)
    lemmas=[]
    for l in d['lemmas']:
        fields(l,('l','f','a','s'),('t','p'))
        model=models[index(l['f'],len(models),'model')]
        ending=model[0].suffix
        require(isinstance(l['l'],str) and l['l'].endswith(ending),f'lemma does not end in first flexion: {l["l"]!r}')
        stem=l['l'][:-len(ending)] if ending else l['l']
        lemmas.append(Lemma(stem,l['f'],l['a'],l['s'],l.get('t',''),l.get('p')))
    prefixes=[]
    for p in d['prefix_sets']:
        require(isinstance(p,list) and all(isinstance(x,str) for x in p),'invalid prefix set')
        require(len(p)==len(set(p)),'duplicate prefix');prefixes.append(sorted(p))
    return Source(models,lemmas,d['accent_models'],d['sessions'],prefixes).validate()

# Explicit semantic mapping, checked against sokirko74/morph_dict agramtab/RusGramTab.cpp.
# Preserve the existing Java wire ordinals; unknown labels stop the import.
POS=dict(zip('N A V PRON PA P_PRED NUM ORD_NUM ADV PRED PREP POSL CONJ INT INP COLLOC PARTICLE ADJ_SHORT PARTICIPLE ADV_PARTICIPLE PARTICIPLE_SHORT INFINITIVE'.split(),
             'С П Г МС МС-П МС-ПРЕДК ЧИСЛ ЧИСЛ-П Н ПРЕДК ПРЕДЛ ПОСЛ СОЮЗ МЕЖД ВВОДН ФРАЗ ЧАСТ КР_ПРИЛ ПРИЧАСТИЕ ДЕЕПРИЧАСТИЕ КР_ПРИЧАСТИЕ ИНФИНИТИВ'.split()))
GRAM=dict(zip('pl sg nom gen dat acc ins prp voc mas fem neu mas-fem pres fut past 1p 2p 3p imp anim inanim compar perf imperf intrans trans act pass 0 abbr patr loc org qual sing_tant interrog demon name surname impers jargon misspell conv poss arch 2 superl'.split(),
              'мн ед им рд дт вн тв пр зв мр жр ср мр-жр нст буд прш 1л 2л 3л пвл од но сравн св нс нп пе дст стр 0 аббр отч лок орг кач дфст вопр указат имя фам безл жарг опч разг притяж арх 2 прев'.split()))
WIRE={}
for _line in Path(__file__).with_name('wire-tags.tsv').read_text().splitlines():
    _i,_name,_token=_line.split('\t');require(int(_i)==len(WIRE),'nonsequential wire ordinals');WIRE[_token]=int(_i)

def read_gram_json(path):
    d=load_json(path);fields(d,('gramcodes',),('plug_noun_gram_code','inanim_indecl_noun','mas_abbr_noun'))
    result={}
    for code,row in d['gramcodes'].items():
        fields(row,('p','g'),('f','l','c','comments'))
        require(len(code)==2,'invalid gramcode')
        require(row['p']=='' or row['p'] in POS,f'unmapped POS: {row["p"]}')
        require(isinstance(row['g'],list),'grammems must be a list')
        require(all(g in GRAM for g in row['g']),f'unmapped grammems: {set(row["g"])-GRAM.keys()}')
        # Empty JSON POS is the legacy TAB '*' marker, a public wire tag (30).
        tokens=[POS[row['p']] if row['p'] else '*']+[GRAM[g] for g in row['g']]
        result[code]=tuple(dict.fromkeys(WIRE[t] for t in tokens))
    return result

def read_tab(path, *, duplicate_policy="reject"):
    require(duplicate_policy in ("reject","legacy-last-wins"),"unknown duplicate policy")
    result={}
    for line in Path(path).read_text(encoding='utf-8-sig').splitlines():
        if not line or line.startswith('//'):continue
        require(len(line)>=5,'invalid TAB row')
        code=line[:2];tokens=[x for x in re.split(r'[\[ ,\]]',line[5:]) if x]
        require(code not in result or duplicate_policy=='legacy-last-wins',f'duplicate TAB code {code}')
        require(all(t in WIRE for t in tokens),f'unmapped TAB tags: {tokens}')
        result[code]=tuple(dict.fromkeys(WIRE[t] for t in tokens))
    return result

def normalize(s):
    require(all(c in '-–—0123456789Ёё' or 'А'<=c<='я' for c in s),f'unsupported wire characters: {s!r}')
    return s.lower().replace('ё','е')

def expand(source,tags,*,prefix_policy='reject',filter_meta=True):
    require(prefix_policy in ('reject','legacy-ignore'),'unknown prefix policy')
    if prefix_policy=='reject':
        require(not any(l.prefix_set is not None for l in source.lemmas),'prefix-set expansion unsupported; explicit legacy-ignore policy required for compatibility assessment')
    # Validate even unused models/codes: never drop unknown morphology silently.
    for model in source.models:
        for e in model:require(e.code in tags,f'unknown ending code {e.code}')
    for l in source.lemmas:
        require(not l.common or l.common in tags,f'unknown common code {l.common}')
        if filter_meta and l.stem.startswith('-'):continue
        common=tags[l.common] if l.common else ()
        yield [(normalize(e.prefix+l.stem+e.suffix),tuple(dict.fromkeys(tags[e.code]+common))) for e in source.models[l.model]]

def read_binary(path, *, allow_empty=False):
    """Read the existing four blocks without changing order or wire tag IDs."""
    with gzip.open(path,'rb') as f: raw=f.read()
    blocks=[];p=0
    for _ in range(4):
        require(p+8<=len(raw),'missing block header');n,size=struct.unpack_from('>ii',raw,p);p+=8
        require(n>=0 and 0<=size<=len(raw)-p,'invalid block length');blocks.append((n,raw[p:p+size]));p+=size
    require(p==len(raw),'trailing binary content')
    def lines(block):
        n,b=block;require(b.endswith(b'd'),'missing line terminator');rows=b[:-1].split(b'd');require(len(rows)==n,'line count mismatch');return rows
    tags=[tuple(b) for b in lines(blocks[0])]
    require(all(all(t<len(WIRE) for t in row) for row in tags),'unknown wire ordinal')
    strings=[b.decode('cp1251') for b in lines(blocks[1])]
    for s in strings:normalize(s)
    n,b=blocks[2];p=0;lemmas=[]
    for _ in range(n):
        require(p+4<=len(b),'truncated lemma');k=struct.unpack_from('>i',b,p)[0];p+=4
        require(k>=(0 if allow_empty else 1) and p+8*k<=len(b),'invalid paradigm length');row=[]
        for _ in range(k):
            si,mi=struct.unpack_from('>ii',b,p);p+=8
            row.append((strings[index(si,len(strings),'string')],tags[index(mi,len(tags),'morphology')]))
        lemmas.append(row)
    require(p==len(b),'trailing lemma data')
    return lemmas,blocks[3]
