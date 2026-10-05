"""Build a private deterministic shared-coverage benchmark corpus from the assessment DB."""
import argparse,collections,hashlib,sqlite3
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--database',required=True);p.add_argument('--review-corpus',required=True);p.add_argument('--output',required=True);a=p.parse_args()
db=sqlite3.connect(f'file:{a.database}?mode=ro',uri=True);known=[]
for i,(word,) in enumerate(db.execute('SELECT surface FROM old GROUP BY surface ORDER BY surface')):
    if i%2900:continue
    old=db.execute('SELECT lemma,tags FROM old WHERE surface=?',(word,)).fetchall()
    new=db.execute('SELECT lemma,tags FROM new WHERE surface=?',(word,)).fetchall()
    if collections.Counter(old)==collections.Counter(new):known.append((word,len(old)))
    if len(known)==1024:break
unknown=[]
for line in Path(a.review_corpus).read_text().splitlines():
    _,word,count=line.split('\t')
    if int(count)==0 and not db.execute('SELECT 1 FROM new WHERE surface=? LIMIT 1',(word.lower().replace('ё','е'),)).fetchone():unknown.append((word,0))
for i in range(128):
    word=f'несуществующий_токен_{i}'
    if not db.execute('SELECT 1 FROM new WHERE surface=? LIMIT 1',(word,)).fetchone():unknown.append((word,0))
with open(a.output,'x',encoding='utf8') as f:f.write(''.join(f'{w}\t{n}\n' for w,n in known+unknown))
print(dict(known=len(known),unknown=len(unknown),sha256=hashlib.sha256(Path(a.output).read_bytes()).hexdigest()))
