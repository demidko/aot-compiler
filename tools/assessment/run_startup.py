"""Sequential alternating startup comparison; each variant is NAME=/path/to/runtime.jar."""
import argparse
import json
import re
import statistics
import subprocess
from pathlib import Path


def summarize(directory, names, rounds):
    result={}
    for name in names:
        raw=(Path(directory)/(name+'.txt')).read_text()
        metrics={}
        for key in ('first_lookup_ms','allocated','retained','max_rss_kib'):
            values=[float(n) for n in re.findall(key+r'=(\d+(?:\.\d+)?)',raw)]
            if len(values)!=rounds: raise ValueError(f'{name}: expected {rounds} {key} samples, found {len(values)}')
            metrics[key]=dict(median=statistics.median(values),min=min(values),max=max(values))
        result[name]=metrics
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--java-home',required=True)
    p.add_argument('--classpath',required=True,help='bits/bytecode dependencies; no analyzer classes')
    p.add_argument('--variant',action='append',required=True)
    p.add_argument('--rounds',type=int,default=5)
    p.add_argument('--output',required=True)
    a=p.parse_args()
    variants={}
    for entry in a.variant:
        name,jar=entry.split('=',1)
        if not re.fullmatch(r'[a-zA-Z0-9_-]+',name) or name in variants: raise ValueError('invalid/duplicate variant name')
        variants[name]=str(Path(jar).resolve(strict=True))
    if a.rounds<1: raise ValueError('rounds must be positive')
    out=Path(a.output);out.mkdir(exist_ok=False)
    harness=out/'harness';harness.mkdir()
    source=Path(__file__).parent
    jdk=Path(a.java_home)/'bin'
    subprocess.run([str(jdk/'javac'),'-proc:none','-cp',next(iter(variants.values()))+':'+a.classpath,
                    '-d',str(harness),str(source/'MigrationCold.java')],check=True)
    for i in range(a.rounds):
        names=list(variants)
        if i%2: names.reverse()
        for name in names:
            command=['python3',str(source/'rss_run.py'),str(jdk/'java'),'-Xms1g','-Xmx1g','-XX:+UseG1GC',
                     '-cp',variants[name]+':'+str(harness)+':'+a.classpath,'MigrationCold']
            with (out/(name+'.txt')).open('a') as log:
                subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
    (out/'summary.json').write_text(json.dumps(summarize(out,variants,a.rounds),indent=2)+'\n')

if __name__=='__main__':main()
