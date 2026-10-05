import com.github.demidko.aot.WordformMeaning;
import java.lang.management.*;
public class MigrationCold {
  public static void main(String[] args)throws Exception {
    var bean=(com.sun.management.ThreadMXBean)ManagementFactory.getThreadMXBean();long id=Thread.currentThread().threadId();
    long allocated=bean.getThreadAllocatedBytes(id),start=System.nanoTime();
    int count=WordformMeaning.lookupForMeanings("замок").size();long elapsed=System.nanoTime()-start;
    long bytes=bean.getThreadAllocatedBytes(id)-allocated;
    long peak=0;for(var pool:ManagementFactory.getMemoryPoolMXBeans())if(pool.getType()==MemoryType.HEAP)peak+=pool.getPeakUsage().getUsed();
    System.gc();long retained=ManagementFactory.getMemoryMXBean().getHeapMemoryUsage().getUsed();
    System.out.printf("first_lookup_ms=%.3f allocated=%d retained=%d sum_pool_peaks=%d count=%d class=%s resource=%s java=%s maxheap=%d gc=%s%n",elapsed/1e6,bytes,retained,peak,count,WordformMeaning.class.getProtectionDomain().getCodeSource().getLocation(),WordformMeaning.class.getResource("/mrd.gz"),System.getProperty("java.version"),Runtime.getRuntime().maxMemory(),ManagementFactory.getGarbageCollectorMXBeans().stream().map(GarbageCollectorMXBean::getName).toList());
  }
}
