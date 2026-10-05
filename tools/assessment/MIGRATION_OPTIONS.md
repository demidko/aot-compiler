# Dictionary migration options — proposal only

No policy below is selected or implemented. Keep the current published dictionary
as the production default while the data rights and compatibility questions are
resolved. The startup optimization is independently useful and does not require
a migration. See MEASUREMENTS.md and PROFILING.md for pinned inputs and evidence.

## Recommended proposal

Offer the newer dictionary as an explicit, versioned opt-in release, with a
rollback path to the existing resource. Treat its identity as the SHA-256 of the
actual generated dictionary plus the documented mapping/prefix policy.

- **IDs:** use a version-qualified identifier `(dictionary fingerprint, packed
  long ID)` for persistence and interchange. Do not interpret an old bare long
  against a new resource. The current bare-long API cannot detect that mistake;
  a version-checking boundary/API and consumer migration are prerequisites.
  Keep the existing release/resource for legacy consumers. Exact one-to-one
  ordered-paradigm matches may seed a reviewed translation table; unmatched or
  ambiguous cases must remain explicitly unresolved.
- **Tags:** retain all existing enum/wire ordinals. Preserve the newer source's
  separate male/female tags rather than silently collapsing them to the old
  MaleFemale tag. Document this as a versioned semantic difference, with
  examples and caller-facing tests. A normalized linguistic view, if desired,
  should be a separately specified API rather than a rewrite of raw tags.
- **Order and multiplicity:** preserve serialized candidate order and each
  paradigm's transformation order within a pinned resource, including duplicate
  analyses. Make ordering version-scoped and characterize each released
  resource. Do not sort or deduplicate results as part of migration. Accepting
  observed cross-version order changes must be explicit; the current experiment
  changes order on 32,228 otherwise equivalent shared surfaces.
- **Prefix sets:** the assessed resource uses explicit `legacy-ignore`, matching
  the current compiler's omission on 60 source records. Do not advertise this as
  complete upstream semantics. Keep this limitation explicit until a separate
  prefix-expansion implementation and behavior review are complete.

This proposal prioritizes detectable version mismatches and source transparency.
It does not promise old-ID, old-order or old-tag equivalence under a new version.
Existing consumers keep their current behavior until they deliberately migrate.

## Alternatives and measured tradeoffs

| Option | Benefit | Main cost or limitation |
| --- | --- | --- |
| Keep current dictionary | Existing IDs, tags, order and ~331 MB retained heap | No new coverage |
| Versioned new dictionary (proposed) | 1,051,564 added surfaces; ~465 MB retained heap | 4,241 lost surfaces; changed analyses/tags/order; explicit consumer migration |
| Preserve unique slots, tombstone others | 4,755,810 old IDs (94.79%) retain exact ordered paradigms | 261,202 IDs retire; 13,838 empty slots need explicit validation; ~465 MB retained; order still not guaranteed |
| Retain every old slot and append new unmatched paradigms | All old paradigms/IDs remain addressable | Retains suspected defects and removed forms; adds ambiguity; 7,297,470 forms and ~468 MB retained; order still not guaranteed |

Naive replacement with new source ordering is unacceptable for persisted IDs:
2,574,700 old numeric IDs silently refer to different analyses, and 2,442,276
become out of bounds. Only 36 old numeric IDs retain the same analysis.

The newer resource has 4,086,452 distinct normalized surfaces and 7,036,268 forms,
versus 3,039,129 and 5,017,012 today. Issue #6's 298-query sample improves from 4
to 288 recognized queries, with no losses in that sample. Recognition and
source agreement are not proofs of linguistic correctness. Across shared
surfaces, 64,208 have changed semantic analysis multisets.

Retained heap increases about 40.6%; startup increases about 27% with identical
optimized production classes in the original experiment. The bounded startup
candidate removes about 19.4% of new-resource startup allocations and gives a
preliminary lower startup median, but leaves retained heap unchanged. Unique
strings and the index capacity cliff dominate; simple deduplication will not
solve this. Warmed checks cover a fixed shared vocabulary, not the complete new
vocabulary or every downstream workload.

Running old and new analyzers side by side may require roughly the sum of their
retained data, before application overhead. That deployment mode has not been
measured. A single-resource opt-in deployment with rollback avoids assuming
that both dictionaries fit within the current memory budget.

## Missing redistribution evidence

The pinned morph_dict README attributes the Russian data to Zaliznyak's grammar
dictionary. Its grammar-table C++ source carries an LGPL notice. The inspected
checkout has no repository-level LICENSE/COPYING file. These observations do
not establish a license for redistributing the full current corpus or a derived
compiled resource.

Before publishing a new resource, obtain and retain evidence identifying:

1. The terms/rightsholder authorization covering the precise Russian corpus
   snapshot, including modified and compiled redistribution and applicable
   attribution/notice requirements.
2. The provenance and redistribution terms of later additions, including the
   2021-12-15 commit that attributes roughly 118,000 surnames to disclosures.ru.
3. Whether grammar-table code notices apply to any distributed code or generated
   assets, separately from the corpus's data terms.
4. A reproducible provenance manifest tying approved source hashes, transformations
   and required notices to the generated resource hash.

These are gaps in the evidence collected, not a conclusion that redistribution
is prohibited. No new corpus, binary, or dictionary license conclusion is
published by the tooling or startup changes.
