# NSE-390 master-alignment recovery

PR #390 is treated as a reconciliation surface, not a blanket rollback.

## Classification

- **Source/runtime/tests:** recover when the artifact remains authoritative on `master`.
- **Active proposal/research:** recover when it carries current provenance, taxonomy, or constraints.
- **Generated telemetry/evidence:** preserve identity and provenance; do not silently regenerate or delete.
- **Intentional replacement:** retain only when the successor is explicit, tested, and provenance-linked.

## Required loop

`compare(master, head) → classify → recover/preserve → validate → wait → re-fetch current SHA/reviews/checks → repeat`.

The production checkpoint must derive counts, timestamps, changed-file totals, review state, and check state from GitHub. A stale review, skipped provider, or unobserved workflow is not completion.

## Historical alignment

The #154 70% `to_1337speak()` threshold remains an initial rollout parameter for incremental character-level variability. It is not a compression ratio or confidence score. Exact round-trip reconstruction remains the invariant, with private mapping material separated from public obfuscation surfaces.

## Related work

#175 = broader alignment/repair lineage.  
#320 = notation taxonomy/Linguist research seed.  
#324 = research/proposal expansion.  
#390 = production integration surface.
