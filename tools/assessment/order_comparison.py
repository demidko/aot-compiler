"""Compare observable result order using each binary's serialized reference order."""
import argparse,collections,gzip,json,struct
from pathlib import Path
from compare import grouped
from readers import require
import sqlite3

def refs(path):
    with gzip.open(path,'rb') as f:
        for _ in range(3):
            n,size=struct.unpack('>ii',f.read(8))
            while size:
                chunk=f.read(min(size,1024*1024));require(bool(chunk),'truncated block');size-=len(chunk)
        count,size=struct.unpack('>ii',f.read(8));b=f.read(size);require(len(b)==size and not f.read(1),'bad reference block')
    offsets={};p=0
    for _ in range(count):
        h,n=struct.unpack_from('>ii',b,p);require(n>=0 and p+8+4*n<=len(b),'bad references');require(h not in offsets,'duplicate hash');offsets[h]=p+4;p+=8+4*n
    require(p==len(b),'trailing references');return b,offsets

def jhash(word):
    h=0
    for c in word:h=(31*h+ord(c))&0xffffffff
    return h if h<2**31 else h-2**32

def ordered(word,rows,ref):
    if len(rows)<2:return [(r[1],r[3]) for r in rows]
    b,offsets=ref;p=offsets[jhash(word)];n=struct.unpack_from('>i',b,p)[0]
    ranks={lid:rank for rank,lid in enumerate(struct.unpack_from('>'+str(n)+'i',b,p+4))}
    return [(r[1],r[3]) for r in sorted(rows,key=lambda r:(ranks[r[4]],r[5]))]

def main():
    p=argparse.ArgumentParser();p.add_argument('--database',required=True);p.add_argument('--old-binary',required=True);p.add_argument('--new-binary',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    old=refs(a.old_binary);new=refs(a.new_binary);db=sqlite3.connect(f'file:{a.database}?mode=ro',uri=True)
    xs=iter(grouped(db,'old'));ys=iter(grouped(db,'new'));x=next(xs,None);y=next(ys,None);count=collections.Counter()
    while x and y:
        if x[0]<y[0]:x=next(xs,None);continue
        if y[0]<x[0]:y=next(ys,None);continue
        word,ar=x;_,br=y
        if collections.Counter((r[1],r[3]) for r in ar)==collections.Counter((r[1],r[3]) for r in br):
            count['same_analysis_multiset']+=1
            if ordered(word,ar,old)==ordered(word,br,new):count['same_result_sequence']+=1
            else:
                count['changed_result_sequence']+=1
        else:count['changed_analysis_multiset']+=1
        x=next(xs,None);y=next(ys,None)
    Path(a.output).write_text(json.dumps(dict(counts=dict(count)),ensure_ascii=False,indent=2)+'\n')
    print(dict(count))

if __name__=='__main__':main()
