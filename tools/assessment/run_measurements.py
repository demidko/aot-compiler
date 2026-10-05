"""Sequential same-JVM comparisons. Supply JMH 1.37, annotation processor, and dependency jars."""
import argparse,subprocess
from pathlib import Path
p=argparse.ArgumentParser()
for n in ('java-home','classpath','analyzer-jar','candidate-jar','corpus','output'):p.add_argument('--'+n,required=True)
a=p.parse_args();out=Path(a.output).resolve();out.mkdir(exist_ok=False);src=Path(__file__).resolve().parent;classes=out/'classes';classes.mkdir()
java=str(Path(a.java_home)/'bin/java');javac=str(Path(a.java_home)/'bin/javac');cp=a.analyzer_jar+':'+a.classpath
subprocess.run([javac,'-cp',cp,'-processorpath',cp,'-d',str(classes),*[str(src/n) for n in ('MigrationBenchmark.java','MigrationCold.java','MigrationPeak.java')]],check=True)
versions=[('old',a.analyzer_jar),('new',a.candidate_jar)]
def run(name,jar,main,extra=(),prefix=()):
    with open(out/name,'a') as log:subprocess.run([*prefix,java,'-Xms1g','-Xmx1g','-cp',jar+':'+str(classes)+':'+a.classpath,main,*extra],stdout=log,stderr=subprocess.STDOUT,check=True)
for _ in range(5):
    for label,jar in versions:run(label+'-cold.txt',jar,'MigrationCold',prefix=['python3',str(src/'rss_run.py')])
for _ in range(3):
    for label,jar in versions:run(label+'-peak.txt',jar,'MigrationPeak')
for mode in ('avgt','sample'):
    for label,jar in versions:
        extra=['assessment.MigrationBenchmark','-bm',mode,'-jvmArgsAppend','-Xms1g -Xmx1g -Dassessment.corpus='+str(Path(a.corpus).resolve()),'-rf','json','-rff',str(out/(label+'-'+mode+'.json'))]
        extra+=['-p','missPercent=50'] if mode=='sample' else ['-prof','gc']
        run(label+'-'+mode+'.log',jar,'org.openjdk.jmh.Main',extra)
