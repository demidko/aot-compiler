# Dictionary growth: retained heap and startup

This is a local assessment, not a dictionary migration recommendation. The
baseline remains merged optimized aot `b47f9ab3d4584bd483894c29af3c840f842d32d5`.
Both dictionaries use the identical optimized lookup index and ID implementation.
See MEASUREMENTS.md for input hashes, JVM configuration, original timings and
compatibility blockers. New corpus/resources remain outside version control.

## Retained structures

Separate reflection and live-class-histogram runs identify the dominant costs.
Sizes below are MiB (1,048,576 bytes), estimated from actual array lengths with
compressed references, CompactStrings enabled and 8-byte alignment. Histograms
corroborate the scale; they also include unrelated JVM/application objects.

| Structure | Published dictionary | Current JSON experiment | Growth |
| --- | ---: | ---: | ---: |
| String objects, payloads and String[] | 202.165 | 267.941 | 65.776 |
| Lemma int[][] including reference array | 41.608 | 59.373 | 17.765 |
| Serialized reference byte[] | 35.063 | 47.128 | 12.065 |
| Lookup long[] index | 32.000 | 64.000 | 32.000 |
| Morphology arrays including references | 0.161 | 0.169 | 0.008 |

These structures grow by 133,813,608 bytes; the prior measured retained heap
increase was 134,292,128 bytes. Strings explain about half and index capacity
about one quarter of that increase. The remainder is principally more forms
and lemmas, not duplicate dictionary machinery. String count grows 34.46%,
form count 40.25%, and lemma count 70.85%; retained bytes per form remain near
66.1 versus 65.9. Absolute growth is still significant.

The writer interns each distinct surface once. There are 4,086,452 unique
surface strings in the new resource. Morphology sets are already interned by
the existing compiler semantics. Full primitive-array comparison finds only
747 duplicate lemma arrays, totaling 117,040 potentially removable bytes
(old: 42 arrays / 6,712 bytes). This is less than 0.03% of new retained heap.
Deduplication is therefore not a useful response to the observed growth.
Public morphology lists expose shared mutable arrays, and listAllFlexions()
exposes the shared mutable String[]: changing those sharing relationships is
not a permissible invisible optimization.

The index grows from 4,194,304 to 8,388,608 long entries. Forcing the new
4,076,471 hashes into the smaller table would yield 97.2% occupancy versus
48.6% now, threatening successful and especially unsuccessful probe costs.
Do not trade the established lookup performance for that 32 MiB saving without
a separately designed and measured indexing change.

Reasoned representation limits, not measured optimizations:

- A flat lemma representation with 32-bit string indices, 16-bit morphology
  indices and 32-bit offsets would save roughly 18.8 MB for this corpus. It
  would need an explicit range/overflow strategy and preservation of invalid-ID
  behavior; current public enum/tag-array contracts still apply. This is a
  distinct redesign, not a demonstrated mitigation.
- Compressed or lazy strings cannot simply replace the public mutable String[]
  contract. Its values and mutations are used by later lookups. Unique Cyrillic
  UTF-16 payloads remain a material cost of the current representation.
- A non-power-of-two or different probing index might avoid the capacity cliff,
  but its memory benefit and CPU cost have not been measured. No such change is
  included in the bounded candidate.

## Bounded startup candidate

The baseline allocates one temporary char[] for each decoded string, immediately
copying it into String storage. Maximum dictionary string length is only 37.
A reusable, growing scratch array eliminates nearly all those temporary arrays;
String construction still copies the relevant range into independent immutable
String values. This preserves ordering, IDs, object independence and public
backing arrays. Increasing the gzip input buffer from 512 bytes to 64 KiB is a
second isolated change. No lookup path, dictionary data or format is changed.

Five alternating fresh-JVM runs per cell, same Temurin 21 / G1 / 1 GiB protocol:

| Scratch-only experiment | Old baseline → scratch | New baseline → scratch |
| --- | ---: | ---: |
| Startup allocated bytes | 626,292,384 → 499,404,336 | 858,165,672 → 691,630,200 |
| First lookup median ms | 1,160.787 → 1,159.619 | 1,499.658 → 1,490.439 |
| Max RSS median KiB | 510,592 → 516,996 | 734,244 → 693,052 |

Allocation decreases are deterministic (20.3% old, 19.4% new). Timing ranges
overlap substantially: no scratch-only startup speedup is established. RSS falls
5.6% for new data but rises 1.3% for old data; allocation reduction is not a
universal resident-memory win. Retained heap is unchanged within run variation.

Adding the 64 KiB gzip buffer to the scratch candidate in a separate five-run
comparison changes median first lookup from 1,214.168 to 1,094.827 ms old and
1,520.892 to 1,445.184 ms new. Ranges overlap (old 1,116–1,344 vs 1,065–1,193;
new 1,489–1,613 vs 1,373–1,516), so treat these as preliminary directional results,
not precise percentage guarantees. It adds about 65 KB of startup allocation.
Retained heap remains unchanged.

A final direct baseline-versus-combined comparison (five alternating runs per
variant) gives old medians 1,146.306→1,093.495 ms and new
1,511.341→1,415.056 ms (4.6% and 6.4% lower). Ranges remain overlapping.
Startup allocation drops 626,294,456→499,471,160 bytes old and
858,167,712→691,697,248 bytes new. Retained heap remains about 330.7/464.9 MB.
Maximum RSS medians are 508,668→520,264 KiB old (2.3% higher) and
734,144→695,684 KiB new (5.2% lower). Thus this is an allocation improvement,
a preliminary startup-time improvement, and no retained-heap mitigation.
The candidate is committed locally in aot as
`df1e34bf59272c86475691bd6d1acc3fa6931d32`, branch `profile-startup`; no remote publication was performed.

A separate warmed lookup check on the newer resource uses the same fixed shared
corpus at 50% misses, fresh Strings, three forks, three 1-second warmups and five
1-second measurements. Baseline is 329.48 ± 19.41 ns/op and candidate is
318.36 ± 13.31 ns/op; intervals overlap, so no warmed speedup is claimed.
Normalized allocation is 210.1253 B/op for both. This check finds no regression
on that controlled workload; new-vocabulary workload performance remains outside
its scope. Raw JMH JSON accompanies the report; full console logs remain local.

Full public dictionary digest remains
`1cb85ee3c89098b4419750230bdf2c9fe74798ea383d56bfc7c77933c2eb984a`:
3,039,129 surfaces, 5,017,012 analyses, 174,628 lemmas and 5,017,012
transformations. All 20 analyzer tests pass. Existing tests cover aliases, mutation, ordering and malformed
IDs; an added long→short→empty→long decoding fixture guards scratch-buffer
reuse and distinct equal String instances. No new dictionary has been installed.

## Reproduction and review

`RetainedStructures.java`, `run_startup.py`, `MigrationCold.java`, and the existing
analyzer `HeapProfile` are runnable diagnostics. Use independent process runs;
do not mix reflection/duplicate detection or builds into timings. For example:

```bash
python tools/assessment/run_startup.py \
  --java-home /toolchains/jdk-21.0.12.1+1 \
  --classpath "$ASSESSMENT_DEPENDENCY_CLASSPATH" \
  --variant old-base=/results/old-base.jar \
  --variant old-candidate=/results/old-candidate.jar \
  --variant new-base=/results/new-base.jar \
  --variant new-candidate=/results/new-candidate.jar \
  --output /results/startup-comparison
```

Construct new-resource copies with make_runtime_jar.py. The class entries must
match their corresponding old-resource variant. Output directories must be new.
Raw scratch/buffer cold logs, histograms and structural counts are committed
under reports; they contain no dictionary resource or expanded corpus.

Independent read-only review recalculated the original ID/cold-memory numbers,
verified resource hashes and JAR class equality, and passed all 17 original
assessment tests. Its identified reproduction gap is now fixed by
policy_reports.py; all four policy aggregates regenerate with identical counts.
Published order/history reports omit source-derived lexical examples and group
non-contracted lost surfaces into one aggregate category. The unknown-field claim
is narrowed to interpreted morphology records. The expanded authored suite has
18 tests. Follow-up review found no material correctness blocker and checked
both startup changes for semantic preservation.

## Code-only PR plan

1. Submit the isolated compiler assessment tools, authored tests, aggregate
   reports and reproduction instructions as one ready-for-review tooling PR.
   Its description must clearly say that it neither installs a new dictionary
   nor chooses ID, result-order, gender-tag or prefix-set policy.
2. Keep the bounded analyzer startup candidate separate. Include its unchanged
   dictionary hash, full digest, boundary tests and honest timing/memory evidence
   in a small ready-for-review PR when publication is requested.
3. Do not attach downloaded JSON/MRD/TAB sources, expanded corpora, generated
   SQLite databases, experimental binaries or JARs. Corpus provenance/licensing
   and migration compatibility remain separate unresolved gates.

No retained-memory fix justifies migration yet. Startup allocations can be
reduced without changing behavior, but the roughly 134 MB retained increase
mostly follows unique data growth and the current index capacity rule.
