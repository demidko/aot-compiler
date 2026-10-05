# Isolated dictionary assessment

These Python 3.10+ tools compare morphology sources without changing the analyzer,
compiler resources, dependencies, public enums, or wire format. No downloaded
Sokirko corpus, expanded corpus, SQLite database, or experimental binary is
included. Tests use small authored fixtures and the existing 71-tag wire contract.

This is an assessment checkpoint, not a production JSON importer. The isolated
writer, serialized-order comparison and performance experiments are documented
in [MEASUREMENTS.md](MEASUREMENTS.md). Retained-heap profiling and a bounded
startup candidate are documented in [PROFILING.md](PROFILING.md). No migration
policy has been selected.

## Pinned inputs

| Component | Commit |
| --- | --- |
| Merged optimized analyzer | `b47f9ab3d4584bd483894c29af3c840f842d32d5` |
| Merged bytecode | `031ee14c28f00a29bea73ffe59c8e7405c19e735` |
| Existing compiler | `12bb2a3cb113d777d1c3a8a95578e73fae2d650e` |
| Current Sokirko source | `0f6e9c6d2aff78bc0b1a2510755f9b082064d38a` |
| Historical MRD | `5f7163661b2afd849d2ba7da50c440002950644e` |
| First historical JSON | `08559224c3dace6fbbb709ce5902f9f8e693f494` |

The JSON reports record exact input SHA-256 values. `wire-tags.tsv` comes from
merged aot-bytecode's compatibility fixture. No enum entries are inserted,
removed, reordered, or reinterpreted.

The upstream README attributes the Russian dictionary to Zaliznyak's grammar
dictionary. `agramtab/RusGramTab.cpp` carries an LGPL notice. These are provenance
observations, not a legal determination about the corpus. New corpus
redistribution remains pending review.

## Mapping and explicit compatibility policies

- JSON `lemmas[].l` is the complete lemma; remove the first flexion's suffix to
  recover the stem, as upstream `CLemmaInfo::GetBase` does. An empty suffix leaves
  the lemma intact. A mismatched suffix or first-ending prefix fails.
- Preserve ordered endings, duplicate forms, and per-ending prefixes. Form =
  ending prefix + recovered stem + ending suffix.
- `f`, `a`, and `s` select model, accent and editing session; optional `t` is the
  common gramcode, and optional `p` selects a lemma-level prefix set.
- Map English POS/grammem identifiers explicitly to existing Russian wire tags.
  Empty JSON POS maps to legacy TAB `*` (ordinal 30). It is publicly observable,
  even though its Java enum name is misleading.
- Merge ending tags before common tags, deduplicate by first occurrence, then
  intern equal tag sets using the first encountered order, matching compiler
  `FlexionFabric` and `Zip`. Common gender `mas-fem` maps to `MaleFemale`; separate
  `mas` and `fem` remain two tags. Do not silently equate those representations.
- Normalize only the existing wire alphabet, lowercase and fold U+0451 to U+0435. Reject
  other characters. A future locale policy needs its own compatibility review.
- Prefix sets fail by default. `--prefix-policy legacy-ignore` explicitly models
  the existing compiler's omission of prefix-set expansion; it does not claim
  complete upstream behavior. Current data has 60 lemma records with prefix sets.
- Leading-hyphen meta entries are explicitly filtered in corpus comparison,
  matching the current compiler (157 records in current data). Historical raw
  equivalence includes them.
- Duplicate TAB codes fail by default. `--duplicate-policy legacy-last-wins`
  reproduces the compiler's map assignment. Its checked-in TAB has one identical
  duplicate; conflicting duplicates are also last-wins only in that mode.
- Unknown fields in interpreted morphology records, JSON duplicate keys, unknown
  tags/codes, malformed references,
  unsupported compound gramcodes, and unsupported prefix behavior fail closed.
  Accent/session data and recognized comment/wiki/example/frequency metadata do
  not affect this analyzer's generated forms. Accent/session payloads are retained
  without full schema validation; only their referenced indices are checked.

## Evidence so far

Historical MRD and JSON have identical ordered 2,804 models, 298,510 lemma
records, 2,012 accent models, and 54 prefix sets. JSON adds one editing session.
All 7,040,634 raw expanded forms match exactly, including order, gramcodes and
common codes: framed SHA-256
`f39d5c0f0b8c00aa2a473e237298031754cd49a2a4509ac7d1b0e98e59048a35`.
This isolates the format conversion from subsequent dictionary edits.

Historical semantic import still reports three absent grammar codes in
three unused models. No actual lemma references those models; the reader does
not silently erase or invent their annotations. Current JSON has no unresolved
ending/common codes under the explicit mapping.

Independent MRD/TAB expansion reproduces all 174,628 published paradigms and
5,017,012 ordered forms with zero differences, including ordered tags and
multiplicity. That validates the comparison reader against the actual published
binary, rather than against its own new output.

Under the explicit legacy prefix policy:

| Metric | Published | Current JSON |
| --- | ---: | ---: |
| Lemmas | 174,628 | 298,353 |
| Paradigm forms including duplicates | 5,017,012 | 7,036,268 |
| Distinct normalized surfaces | 3,039,129 | 4,086,452 |
| Issue #6 queries found, out of 298 | 4 | 288 |

There are 1,051,564 added surfaces and 4,241 lost surfaces. Of 3,034,888 shared
surfaces, 64,208 have changed semantic analysis multisets (lemma spelling plus
tag set and multiplicity); 2,970,680 retain the same multiset including tag order.
On shared surfaces, 55,171 analyses are removed and 96,684 added. The issue #6
sample gains 284 recognized queries and loses none. Recognition is not a claim
that an analysis is linguistically correct. Queries were extracted as
Cyrillic-only nonempty lines after surrounding-whitespace trimming.

Behavior checks cover ambiguity, normalization and irregular inflection.
Common-gender analyses can change from one common-gender tag to separate male
and female tags. New surname analyses can add ambiguity rather than merely
supply missing coverage. The serialized-reference comparison finds 32,228
result-order changes on otherwise unchanged analysis multisets; see
MEASUREMENTS.md. Source-derived lexical examples and corpus excerpts are omitted
from these publication documents.

## Persisted IDs are a migration blocker

The public ID packs positional lemma and transformation indices, not lexical
identity. With naive JSON source ordering, 2,574,736 old numeric IDs still address
an entry; only 36 retain the same surface, lemma and ordered tags. The other
2,574,700 silently identify different analyses. Another 2,442,276 old positive
IDs no longer address a valid transformation. Only three full paradigms retain
both their position and semantic contents.

Exact ordered-paradigm matching (ignoring tag order within each tag set) finds
160,869 old paradigms somewhere in the new data. Of these, 160,790 have a unique
new match; 79 have multiple candidates. These are fingerprint-based candidate
matches, not yet an accepted ID migration map. No stable-ID policy is chosen.
Options to evaluate:

1. Version-scoped positional IDs, requiring explicit consumer migration.
2. A versioned translation table: unique exact matches are candidates, ambiguous
   and changed paradigms require explicit treatment.
3. Preserve old slots and append new entries, with a documented policy for
   removed/changed forms; measure the memory and compatibility cost first.

## Reproduce locally

Use separate input/output directories outside the repository. Obtain the
pinned sources independently; the commands below do not download them.

```bash
python -m unittest discover -s tools/assessment -p 'test_*.py'

python tools/assessment/compare.py historical \
  --mrd /data/historical.mrd --morph /data/historical.json \
  --gram /data/historical-gramtab.json --output /results/historical.json

python tools/assessment/compare.py legacy \
  --mrd /compiler/src/main/resources/mrd \
  --tab /compiler/src/main/resources/tab \
  --binary /analyzer/src/main/resources/mrd.gz \
  --prefix-policy legacy-ignore --duplicate-policy legacy-last-wins \
  --output /results/legacy.json

python tools/assessment/compare.py diff \
  --binary /analyzer/src/main/resources/mrd.gz \
  --morph /data/current/morphs.json --gram /data/current/gramtab.json \
  --prefix-policy legacy-ignore --database /results/new-assessment.sqlite \
  --queries /data/issue6-queries.txt --output /results/corpus.json
```

The SQLite output must not already exist. Full comparison took about 128 seconds
on the task machine; this is tool execution time, not an analyzer benchmark.
Reports intentionally separate order-sensitive paradigms, semantic multisets,
and positional-ID reuse. Dictionaries and generated databases stay local.

Next: review the measured tradeoffs and choose explicit compatibility policies.
The writer and measurements preserve the compact index and primitive ID code.
See MEASUREMENTS.md for absolute resource growth and remaining gates.

## Experimental writer and measurement commands

The writer requires the database produced by `diff`. Every output path below
must be outside the checkout. First rebuild the published data and compare the
whole gzip file before generating a new dictionary:

```bash
python tools/assessment/write_prefix.py --database /results/assessment.sqlite \
  --table old --output /results/old-prefix.bin
java -Xmx3g tools/assessment/ExperimentalWriter.java \
  /results/old-prefix.bin /results/old-rebuilt.gz
cmp /analyzer/src/main/resources/mrd.gz /results/old-rebuilt.gz

python tools/assessment/write_prefix.py --database /results/assessment.sqlite \
  --table new --output /results/new-prefix.bin
java -Xmx3g tools/assessment/ExperimentalWriter.java \
  /results/new-prefix.bin /results/new-experimental.gz

python tools/assessment/order_comparison.py \
  --database /results/assessment.sqlite \
  --old-binary /analyzer/src/main/resources/mrd.gz \
  --new-binary /results/new-experimental.gz --output /results/order.json
```

Use `--policy retain-legacy` or `--policy tombstone` with `--table new` only for
explicit alternative-policy experiments. These switches do not modify sources
or install the output. `read_binary(..., allow_empty=True)` is required to inspect
a tombstone experiment; the default reader still rejects empty paradigms.

Build a runtime JAR copy with identical code and derive a fixed shared corpus:

```bash
python tools/assessment/make_runtime_jar.py \
  --analyzer-jar /analyzer/build/libs/aot.jar \
  --resource /results/new-experimental.gz --output /results/candidate.jar
python tools/assessment/make_corpus.py --database /results/assessment.sqlite \
  --review-corpus /analyzer/src/jmh/resources/review-corpus.tsv \
  --output /results/migration-corpus.tsv
```

`run_measurements.py` accepts an explicit classpath containing the analyzer's
bytecode/bits dependencies, JMH core and generator 1.37, jopt-simple 5.0.4 and
commons-math3 3.6.1. The Gradle `jmh` source set in merged aot resolves these.
It compiles the isolated harness, runs each measurement sequentially, and
captures raw results. Use the same pinned JDK for compilation and execution:

```bash
python tools/assessment/run_measurements.py \
  --java-home /toolchains/jdk-21.0.12.1+1 \
  --classpath "$ASSESSMENT_DEPENDENCY_CLASSPATH" \
  --analyzer-jar /analyzer/build/libs/aot.jar \
  --candidate-jar /results/candidate.jar \
  --corpus /results/migration-corpus.tsv --output /results/measurements
```

The output directory must not already exist. Avoid concurrent builds or corpus
processing during timings. The Java writer may use a larger heap offline; all
runtime comparison forks use the same fixed 1 GiB heap. Data conversion memory
must not be confused with analyzer runtime memory.


## Regenerate policy reports and profile retained structures

`policy_reports.py` regenerates the four policy reports using the comparison
SQLite database and locally generated variant resources. Fingerprints preserve
ordered forms; exact matching also preserves tag order and multiplicity. Only
one-to-one fingerprint matches are eligible for stable slots. Gender collapse is
a separate hypothetical comparison, never a rewrite. SHA-256 fingerprints are
candidate matching evidence, not an accepted migration map.

```bash
python tools/assessment/policy_reports.py \
  --database /results/assessment.sqlite \
  --binary /analyzer/src/main/resources/mrd.gz \
  --retain-legacy /results/retain-legacy-experimental.gz \
  --tombstone /results/tombstone-experimental.gz \
  --history-dir /data/history --output-dir /results/policy-reports
```

Extract these historical files from a local `sokirko74/morph_dict` checkout with
`git show COMMIT:data/Russian/morphs.EXT > /data/history/NAME`. The committed
`reports/removal-history.json` records the expected SHA-256 for every file.

| Local name | Commit | Extension |
| --- | --- | --- |
| `initial-upstream.mrd` | `4030766250acb4fef1d77be285ee585f1a693bfd` | `mrd` |
| `pre-think.mrd` | `8f7d01059e5152e508ccac3fca5fd1741a3a4216^` | `mrd` |
| `post-think.mrd` | `8f7d01059e5152e508ccac3fca5fd1741a3a4216` | `mrd` |
| `historical.mrd` | `5f7163661b2afd849d2ba7da50c440002950644e` | `mrd` |
| `post-pack.json` | `4670e29b5037404c10e94e05934bec2426034419` | `json` |

History compares only the 4,241 final lost surfaces, not every intervening
analysis change. Prefix sets remain omitted. Published order/history reports contain aggregate counts only; source-derived
lexical samples and identifying surname examples are excluded.

`RetainedStructures.java` is a separate diagnostic, not a timing workload:

```bash
javac -proc:none -cp "$ANALYZER_JAR:$ASSESSMENT_DEPENDENCY_CLASSPATH" \
  -d /results/harness tools/assessment/RetainedStructures.java
java -Xms1g -Xmx1g -XX:+UseG1GC \
  -cp "$ANALYZER_JAR:/results/harness:$ASSESSMENT_DEPENDENCY_CLASSPATH" \
  RetainedStructures > /results/structures.json
```

Run independently for each resource JAR. Counts are reflected from actual
runtime arrays. Size estimates assume CompactStrings enabled, compressed references, 16-byte array
headers, 24-byte String objects and 8-byte alignment; check against the analyzer's
`HeapProfile` histogram on the selected JVM. Duplicate lemma detection compares
full primitive arrays after hashing. The temporary char-array estimate is baseline allocation, not retained heap.
Diagnostic allocations are excluded from
all reported runtime timing/heap measurements.
