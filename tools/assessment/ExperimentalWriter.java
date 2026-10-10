import java.io.*;
import java.nio.charset.Charset;
import java.nio.file.*;
import java.util.*;
import java.util.zip.GZIPOutputStream;

/** Isolated writer: retain the compiler's actual Java HashMap/HashSet order. */
public class ExperimentalWriter {
  public static void main(String[] args) throws Exception {
    if (args.length != 2) throw new IllegalArgumentException("prefix-file output.gz");
    Path target = Path.of(args[1]);
    if (Files.exists(target)) throw new IOException("Refusing to overwrite " + target);
    byte[] prefix = Files.readAllBytes(Path.of(args[0]));
    DataInputStream input = new DataInputStream(new ByteArrayInputStream(prefix));
    int morphCount = input.readInt(), morphSize = input.readInt();
    if (morphCount < 0 || morphSize < 0) throw new IOException("Invalid morphology block");
    input.skipNBytes(morphSize);
    int stringCount = input.readInt(), stringSize = input.readInt();
    byte[] stringBytes = input.readNBytes(stringSize);
    String[] strings = new String[stringCount];
    Charset encoding = Charset.forName("windows-1251");
    int from = 0, next = 0;
    for (int i = 0; i < stringBytes.length; i++) {
      if (stringBytes[i] == 100) {
        if (next >= stringCount) throw new IOException("Too many strings");
        strings[next++] = new String(stringBytes, from, i - from, encoding);
        from = i + 1;
      }
    }
    if (next != stringCount || from != stringBytes.length) throw new IOException("String count mismatch");
    int lemmaCount = input.readInt(), lemmaSize = input.readInt();
    if (lemmaSize != input.available()) throw new IOException("Lemma block length mismatch");
    Map<Integer, Set<Integer>> refs = new HashMap<>();
    for (int lid = 0; lid < lemmaCount; lid++) {
      int count = input.readInt();
      if (count < 0) throw new IOException("Negative paradigm length");
      for (int j = 0; j < count; j++) {
        int si = input.readInt(), mi = input.readInt();
        if (si < 0 || si >= stringCount || mi < 0 || mi >= morphCount) throw new IOException("Bad reference");
        refs.computeIfAbsent(strings[si].hashCode(), key -> new HashSet<>()).add(lid);
      }
    }
    if (input.available() != 0) throw new IOException("Trailing data");
    long size = 0;
    for (Set<Integer> ids : refs.values()) size += 8L + 4L * ids.size();
    if (size > Integer.MAX_VALUE) throw new IOException("Reference block exceeds format");
    try (DataOutputStream out = new DataOutputStream(new GZIPOutputStream(Files.newOutputStream(target, StandardOpenOption.CREATE_NEW)))) {
      out.write(prefix);
      out.writeInt(refs.size()); out.writeInt((int)size);
      for (var entry : refs.entrySet()) {
        out.writeInt(entry.getKey()); out.writeInt(entry.getValue().size());
        for (int id : entry.getValue()) out.writeInt(id);
      }
    }
    System.out.printf("strings=%d lemmas=%d hashes=%d ref_bytes=%d compressed_bytes=%d%n", stringCount, lemmaCount, refs.size(), size, Files.size(target));
  }
}
