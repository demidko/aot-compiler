"""Replace only mrd.gz in a local experimental copy; verify every other entry."""
import argparse,zipfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--analyzer-jar',required=True);p.add_argument('--resource',required=True);p.add_argument('--output',required=True);a=p.parse_args()
resource=Path(a.resource).read_bytes()
with zipfile.ZipFile(a.analyzer_jar) as src,zipfile.ZipFile(a.output,'x') as dst:
    if 'mrd.gz' not in src.namelist():raise ValueError('missing dictionary in analyzer jar')
    for info in src.infolist():dst.writestr(info,resource if info.filename=='mrd.gz' else src.read(info.filename))
with zipfile.ZipFile(a.analyzer_jar) as old,zipfile.ZipFile(a.output) as new:
    if old.namelist()!=new.namelist() or any(old.read(n)!=new.read(n) for n in old.namelist() if n!='mrd.gz'):raise ValueError('non-resource entry changed')
print('Verified: only mrd.gz differs')
