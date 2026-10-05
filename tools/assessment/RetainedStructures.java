import com.github.demidko.aot.WordformMeaning;
import java.lang.reflect.Field;
import java.util.Arrays;
import java.util.HashMap;
import java.util.ArrayList;

/** Separate diagnostic run. Sizes assume HotSpot compressed references, CompactStrings enabled and 8-byte alignment.
 * temporary_char_arrays_bytes estimates baseline allocation, not retained memory. */
public class RetainedStructures {
  static long aligned(long n) { return (n+7)&~7L; }
  static Object field(Class<?> type,Object instance,String name)throws Exception {
    Field f=type.getDeclaredField(name);f.setAccessible(true);return f.get(instance);
  }
  public static void main(String[] args)throws Exception {
    WordformMeaning.lookupForMeanings("замок");
    Class<?> c=WordformMeaning.class;
    String[] strings=(String[])field(c,null,"allFlexionStrings");
    int[][] lemmas=(int[][])field(c,null,"lemmas");
    Object[][] tags=(Object[][])field(c,null,"allMorphologyTags");
    long payload=0,scratch=0,characters=0,lemmaBytes=0,forms=0,tagBytes=0,duplicateBytes=0;
    int maxLength=0,duplicates=0;
    for(String s:strings) {
      boolean latin=true;for(int i=0;i<s.length();i++)if(s.charAt(i)>255){latin=false;break;}
      payload+=aligned(16L+s.length()*(latin?1:2));scratch+=aligned(16L+2L*s.length());
      characters+=s.length();maxLength=Math.max(maxLength,s.length());
    }
    var groups=new HashMap<Integer,ArrayList<int[]>>();
    for(int[] a:lemmas) {
      long bytes=aligned(16L+4L*a.length);lemmaBytes+=bytes;forms+=a.length/2;
      var bucket=groups.computeIfAbsent(Arrays.hashCode(a),k->new ArrayList<>());
      boolean duplicate=false;for(int[] b:bucket)if(Arrays.equals(a,b)){duplicate=true;break;}
      if(duplicate){duplicates++;duplicateBytes+=bytes;}else bucket.add(a);
    }
    for(Object[] a:tags)tagBytes+=aligned(16L+4L*a.length);
    System.out.printf("{\"strings\":%d,\"characters\":%d,\"max_string_length\":%d,\"string_objects_bytes\":%d,\"string_payload_bytes\":%d,\"string_reference_array_bytes\":%d,\"temporary_char_arrays_bytes\":%d,\"lemmas\":%d,\"forms\":%d,\"lemma_arrays_bytes\":%d,\"lemma_reference_array_bytes\":%d,\"duplicate_lemma_arrays\":%d,\"duplicate_lemma_bytes\":%d,\"tag_arrays_bytes\":%d,\"tag_reference_array_bytes\":%d}%n",
      strings.length,characters,maxLength,24L*strings.length,payload,aligned(16L+4L*strings.length),scratch,
      lemmas.length,forms,lemmaBytes,aligned(16L+4L*lemmas.length),duplicates,duplicateBytes,tagBytes,aligned(16L+4L*tags.length));
  }
}
