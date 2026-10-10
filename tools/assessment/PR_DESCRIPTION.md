Add isolated, reproducible tools for evaluating dictionary changes before any production migration. The tooling compares historical MRD/JSON expansions, reproduces the published wire resource, characterizes coverage, ambiguity, tags, result order and persisted-ID compatibility, and measures runtime memory/startup/lookup costs against the merged optimized analyzer.

All changes are under `tools/assessment/`: source readers, authored fixtures, experimental writers, offline comparison/report generators, benchmark/profiling harnesses, aggregate evidence and documentation. Downloaded corpora, expanded databases, experimental resources and JARs are excluded. Existing compiler resources, dependencies, enums and production code are unchanged.

Validation and evidence:

- **18 authored tests pass.** Independent review verified the numeric claims, artifact hashes, resource-only JAR differences and matching/order logic.
- Historical MRD→JSON conversion reproduces 7,040,634 ordered raw forms; the legacy MRD/TAB reconstruction matches all 174,628 published paradigms and the complete compressed resource.
- Four policy reports regenerate with identical counts; historical examples are deterministic.
- Measurements expose substantial costs and compatibility hazards: about 40.6% more retained heap, 4,241 lost surfaces, changed tags/order, and unsafe naive reuse of positional IDs. Recognition is explicitly distinguished from linguistic correctness.
- Profiling identifies unique strings and index capacity as the main retained costs. A separate analyzer startup improvement preserves the current dictionary and is not required by these tools.

`MIGRATION_OPTIONS.md` contains a proposal for version-qualified IDs and explicitly versioned tag/order behavior, plus alternatives and missing redistribution evidence. **No migration policy is selected or implemented.** No new dictionary is installed or redistributed. See `README.md`, `MEASUREMENTS.md` and `PROFILING.md` for pinned inputs, reproduction commands and measurement limitations.
