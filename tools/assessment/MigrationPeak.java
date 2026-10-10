import com.github.demidko.aot.WordformMeaning;
import java.lang.management.ManagementFactory;
import java.util.concurrent.atomic.*;
/** Separate 1 ms heap sampling run; excluded from throughput and startup timing. */
public class MigrationPeak {
  public static void main(String[] args)throws Exception {
    AtomicBoolean run=new AtomicBoolean(true);AtomicLong peak=new AtomicLong(),samples=new AtomicLong();
    Thread sampler=new Thread(()->{while(run.get()) {long used=ManagementFactory.getMemoryMXBean().getHeapMemoryUsage().getUsed();peak.accumulateAndGet(used,Math::max);samples.incrementAndGet();try {Thread.sleep(1);}catch(InterruptedException e){return;}}});
    sampler.start();int count=WordformMeaning.lookupForMeanings("замок").size();
    peak.accumulateAndGet(ManagementFactory.getMemoryMXBean().getHeapMemoryUsage().getUsed(),Math::max);run.set(false);sampler.join();
    System.out.printf("sampled_peak_heap=%d samples=%d count=%d%n",peak.get(),samples.get(),count);
  }
}
