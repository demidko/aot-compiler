package assessment;
import com.github.demidko.aot.WordformMeaning;
import org.openjdk.jmh.annotations.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;
@State(Scope.Thread)
@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.NANOSECONDS)
@Warmup(iterations=3,time=1)
@Measurement(iterations=5,time=1)
@Fork(value=3,jvmArgsAppend={"-Xms1g","-Xmx1g"})
public class MigrationBenchmark {
  @Param({"0","10","50","100"}) public int missPercent;
  private String[] inputs; private int cursor;
  @Setup public void setup() throws Exception {
    List<String> known=new ArrayList<>(),unknown=new ArrayList<>();
    for(String line:Files.readAllLines(Path.of(System.getProperty("assessment.corpus")))) {
      String[] p=line.split("\t");int expected=Integer.parseInt(p[1]);
      if(WordformMeaning.lookupForMeanings(p[0]).size()!=expected)throw new AssertionError("Changed fixture: "+p[0]);
      (expected==0?unknown:known).add(p[0]);
    }
    Random random=new Random(0x719a07);List<String> shuffled=new ArrayList<>();
    for(int i=0;i<4096;i++) {List<String> pool=i*100<missPercent*4096?unknown:known;shuffled.add(pool.get(random.nextInt(pool.size())));}
    Collections.shuffle(shuffled,random);inputs=shuffled.toArray(String[]::new);
    System.err.printf("known=%d unknown=%d miss_percent=%d%n",known.size(),unknown.size(),missPercent);
  }
  @Benchmark public Object freshToken(){String word=inputs[cursor++&4095];return WordformMeaning.lookupForMeanings(new String(word.toCharArray()));}
}
