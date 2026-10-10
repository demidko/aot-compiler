# Dictionary migration measurements and decisions

The optimized analyzer remains unchanged. These are local experiments with
alternative resources, not a proposed production dictionary replacement.
All candidate corpora, compiled dictionaries, and benchmark query data remain
outside this repository. Public enums and wire ordinals are unchanged.

## Writer validation and result order

`write_prefix.py` interns strings and ordered morphology exactly as the existing
compiler does. `ExperimentalWriter.java` constructs reference records with the
actual Java `HashMap<Integer, Set<Integer>>` and `HashSet<Integer>` behavior,
rather than approximating their iteration order in another language.

Recompiling the published data reproduces **the entire original gzip file byte
for byte**, including all four blocks and reference order. Compressed SHA-256:
`7bc652a568090d6f07e9d53213329769e4d1597a5688d9c77e422b63b5c5fc41`.
Uncompressed SHA-256:
`c100622d592a0b52805594d2cd9cb3a364669295388b2d2516ce08fb87c8bb13`.
This validation completed before generating and benchmarking the new resource.

The new resource changes observable order on **32,228 surfaces** whose ordered-tag
analysis multisets are otherwise identical. Another 2,938,452 retain the same
result sequence. These comparisons use serialized hash-reference order and then
transformation order, matching runtime traversal; analysis payloads include
lemma spelling and ordered tags. Numeric IDs are deliberately compared separately,
since naive source ordering changes almost all of them.

Preserving old IDs alone does not guarantee result-order preservation. Adding
candidate lemmas can resize a Java hash set and reorder existing candidates.
A compatibility writer could preserve each old reference sequence and append new
candidates, but that is a separate order policy that these experiments do not
silently impose.

## Comparable performance

Host: Linux x86-64 VM, five visible AMD EPYC 9V74 CPUs. JVM: Temurin
21.0.12.1+1, G1, `-Xms1g -Xmx1g`. JMH 1.37, one thread, three forks,
three one-second warmup iterations and five one-second measurement iterations.
No builds, corpus comparisons, or other measurement workloads ran concurrently.

Both runtime JARs have identical bytes for every entry except `mrd.gz`; the
baseline uses merged optimized aot, not the pre-optimization implementation.
The JSON reader runs offline. JSON introduces **no runtime parser path**.

The fixed query corpus contains 1,024 dictionary-distributed known words with
identical ordered-tag analysis multisets in both versions, plus 203 misses
(75 varied authored misses and 128 identifier-shaped misses). Both versions
assert expected analysis counts during setup. Each operation constructs a fresh
string. Workloads cycle through 4,096 seeded shuffled inputs; the nominal 10%
miss mix is 410/4096. These are controlled workloads, not production frequency
estimates or benchmarks of the newly added vocabulary.
Corpus SHA-256:
`997d89b5a89c74852789c94762e1e9756e049d4f024821c93bac6af3da717b02`.

| Miss share | Optimized published data, ns/op | New data, ns/op | Mean change | Allocation, old → new |
| --- | ---: | ---: | ---: | ---: |
| 0% | 478.33 ± 20.99 | 486.65 ± 16.48 | +1.7% | 258.62 → 258.62 B/op |
| ~10% | 452.90 ± 25.19 | 462.61 ± 23.64 | +2.1% | 249.14 → 249.14 B/op |
| 50% | 320.49 ± 12.28 | 322.60 ± 18.26 | +0.7% | 210.13 → 210.13 B/op |
| 100% | 129.01 ± 2.48 | 124.25 ± 2.99 | −3.7% | 161.93 → 161.93 B/op |

Errors are JMH's 99.9% score confidence intervals. The small positive mean
changes do not establish a lookup regression. No general speedup is claimed.
The existing compact index and primitive-ID wins remain in place.

A separate JMH sample-time run at 50% misses gives the following distributions:

| Percentile | Published data | New data |
| --- | ---: | ---: |
| p50 | 240 ns | 251 ns |
| p90 | 571 ns | 561 ns |
| p95 | 641 ns | 641 ns |
| p99 | 1,232 ns | 1,160 ns |
| p99.9 | 38.3 µs | 28.2 µs |

Sample mode has different instrumentation from average-time mode. GC and VM
scheduling affect the sparse tail, including millisecond outliers; these tail
figures are descriptive, not evidence of improved tail latency or an SLA.

## Startup, memory and artifact growth

Five alternating fresh-JVM runs measured first lookup/class initialization;
JVM launch time is excluded and the OS page cache was not flushed. Retained heap
is measured after an explicit GC request. Three separate processes sample heap
usage every millisecond during initialization; sampled peak is a lower bound on
the instantaneous maximum. Maximum RSS comes from Linux child-process rusage,
including the full process through post-GC reporting. MB below means decimal MB.

| Metric | Published data | New data | Change |
| --- | ---: | ---: | ---: |
| Compressed dictionary | 43.487 MB | 58.229 MB | +33.9% |
| Uncompressed dictionary | 115.247 MB | 155.457 MB | +34.9% |
| First lookup median | 1,193 ms | 1,515 ms | +27.0% |
| Startup thread allocation | 626.292 MB | 858.166 MB | +37.0% |
| Retained heap median | 330.646 MB | 464.938 MB | +40.6% |
| Sampled peak heap median | 417.384 MB | 532.203 MB | +27.5% |
| Peak RSS median | 510,416 KiB | 733,080 KiB | +43.6% |

This is a real resource regression in absolute terms, not a free migration.
Coverage also grows: distinct surfaces +34.46%, paradigm forms +40.25%, and
lemma records +70.85%. Retained bytes per stored form are nearly unchanged,
65.91 → 66.08; retained bytes per distinct surface increase 108.80 → 113.78.

The packed reference index crosses its power-of-two capacity boundary:
4,194,304 → 8,388,608 long buckets, adding 33,554,432 bytes. Serialized reference
bytes grow 36,766,208 → 49,417,536. More strings and paradigm arrays account for
additional storage. Removing that capacity margin by raising load toward 100%
could seriously hurt unsuccessful lookup and is not an accepted mitigation.

Decision options are an explicitly larger full dictionary, an optional extended
profile while retaining the current default, or further measured storage work.
None guarantees the current footprint with larger coverage. No runtime core
optimization or migration policy was changed in this assessment.

## Why 4,241 surfaces disappear

These losses already exist before JSON conversion; the first JSON conversion
itself preserves every generated form. Categories are mutually exclusive by
surface spelling, not linguistic judgments:

- **4,079 contracted nominal surfaces** come from an ending in published
  model 61. The first morph_dict snapshot maps affected lemmas to different
  models without that ending. There are 4,080 lost analysis occurrences of this
  model ending because one surface has multiple entries. This can remove
  legitimate stylistic forms; treating all losses as corrections is unjustified.
- **42 surfaces associated with one corrected lemma spelling** are already
  changed in the earliest available morph_dict snapshot. The change predates
  JSON conversion and is not evidence of a JSON parsing defect.
- **120 other surfaces** involve changed adjective/noun/verb paradigms, short
  abbreviations and isolated forms. Their individual linguistic acceptability
  is not inferred from the diff.

Only aggregate categories are reported here. Source-derived spellings, lexical
examples and corpus excerpts are omitted from these publication documents.

Of the 4,241 total, **4,237 are already absent in the first morph_dict commit**
`4030766250acb4fef1d77be285ee585f1a693bfd` (2021-12-03). That repository cannot by
itself identify the earlier originating edits; the report does not attribute
those losses to the later `pack` commit.

One additional surface disappears in `b4c7af3d2b787b4c40c124204725130a74a753ab`
(2021-12-20). Three abbreviation surfaces are explicitly removed in
`5c07ac137d48454f90f4292a7abe11ebb9e732cb` (2023-03-05). The 2022
revision `8f7d01059e5152e508ccac3fca5fd1741a3a4216` removes none of these otherwise-lost surfaces,
although analysis-level changes can still occur on retained surfaces.

Actionable choices: retain selected legacy variants with provenance, accept
specific reviewed corrections/removals in a versioned data release, or retain
all old analyses as a compatibility profile. The last option preserves coverage
but also preserves possible defects and increases ambiguity.

## Stable-ID experiments

Matching exact ordered paradigms uniquely in both corpora preserves **160,790
old lemma slots and 4,755,810 transformation IDs (94.79%)**. There are 13,838
unresolved old slots, containing 261,202 IDs; 79 old paradigms have ambiguous
exact semantic matches. No arbitrary candidate is selected.

Both experiments keep the 174,628 original slots and append 137,563 unmatched
new records, for 312,191 slots total:

| Local experiment | Retired slots | Forms | Compressed size | Retained heap median |
| --- | --- | ---: | ---: | ---: |
| Sequential new data, control | IDs reassigned | 7,036,268 | 58.229 MB | 465.023 MB |
| Tombstones | 13,838 empty paradigms | 7,036,268 | 57.722 MB | 465.175 MB |
| Retain legacy | Keep all old paradigms | 7,297,470 | 59.076 MB | 467.528 MB |

Heap values in this table come from a separate three-round alternating comparison
with the same JVM settings. The extra compressed/retained cost of legacy retention
is small relative to the full corpus increase: about 0.85 MB and 2.50 MB above its
new-data control. Small timing/RSS differences in these three runs are not claimed
as improvements. Stable variants have not received separate warmed JMH runs.

Full binary readback verifies:

- Legacy retention preserves all **174,628** old ordered paradigms, with zero
  changed old slots: every existing valid ID retains its analysis.
- Tombstones preserve **160,790** old paradigms and leave **13,838** empty slots,
  with zero nonempty slots reassigned to a different old meaning.

The current analyzer can represent empty paradigms without a wire change, but
its lazy ID decoder still constructs an object for a retired ID; dereferencing
its form fails. Tombstones therefore require an explicit consumer/versioning
contract, and likely a separately reviewed validity API. Retention instead
keeps legacy defects and can add duplicate/conflicting analyses when newer
records for the same word are appended. Neither policy is selected here.

## Common-gender compatibility

Upstream commit `944f4736d0310147657b6a05e6a404c32fee3b26` (2023-11-02)
replaces `mas-fem` with `mas` plus `fem`. Current gramtab has 35 such noun codes
and no common-gender codes. This affects 132,678 current paradigms, including
many surnames; it is not limited to a few familiar common-gender nouns.

A local matching-only experiment collapses the two gender tags to the existing
`MaleFemale` tag. It recovers semantic matches for 9,260 distinct old paradigms
(9,406 new candidates, so ambiguity must still be resolved). This was not
applied to any measured dictionary or production enum.

Options are faithful new tags with a documented behavior change, an explicit
legacy-tag compatibility adapter for the reviewed codes, or separate versioned
views. Emitting all three tags would create a third representation and is not
a neutral compatibility fix.

## Provenance and remaining gates

The dictionary has multiple upstream sources. In addition to the Zaliznyak
attribution, commit `10dc9c8243575bea3c3b52018a07055e9383b66a` says it adds 118,000
surnames from disclosures.ru. Source-file LGPL notices alone do not settle
corpus redistribution permission. This report makes no legal determination.

Remaining decisions are the ID contract, treatment of lost/corrected forms,
common-gender representation, reference-order policy, acceptable absolute memory
increase, and redistribution licensing. The code-only tools are suitable for
review independently of corpus approval. No new corpus has been published.
