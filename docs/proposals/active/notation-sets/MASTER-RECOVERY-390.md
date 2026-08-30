# NSE-390 master-alignment recovery

## Decision

PR #390 is a long-lived production integration surface. Its comparison against `master` must be treated as a reconciliation problem, not as a blind rollback.

A deletion is classified as follows:

1. **source/runtime/test deletion** — recover when the same artifact remains authoritative on `master`.
2. **proposal/documentation deletion** — recover when it contains active provenance, taxonomy, or research constraints.
3. **generated telemetry deletion** — do not blindly regenerate or silently discard; preserve the artifact identity and classify it as generated evidence/archive material.
4. **intentional replacement** — retain only when a successor is explicit, tested, and provenance-linked.

## Recovery loop

`compare(master, head) → classify → recover/preserve → validate → wait for automation → re-fetch current SHA/reviews/checks → repeat`.

The current PR branch is required to remain **0 commits behind `master`** at each production checkpoint. Counts, timestamps, changed-file totals, and review/check state are observations generated from GitHub rather than hand-maintained values.

## Recovered master artifacts

The recovery pass restores the SHE P0.8–P0.13 planners, their public package exports, the P0 roadmap, the cache security/dispatch behavior, the notation-set hygiene and NSE-022/NSE-023 research records, and the SHA-bound PR production ledger.

These recoveries preserve the existing observer-only contracts: dual-gate verification, SHA binding, fail-closed deserialization, no automatic merge, and no live persistence/signing.

## Telemetry policy

The historical `ops/github-telemetry/raw/**` and generated performance snapshots are **evidence**, not source code. They require an archive/provenance decision before deletion or regeneration. The recovery workflow therefore excludes them from automatic source restoration.

## Relationship to #175 / #320 / #324

- #175 remains the broader alignment/repair lineage.
- #320 remains the notation taxonomy and Linguist-related research seed.
- #324 remains a proposal/research expansion rather than authority to delete unrelated master artifacts.
- #390 is the production integration surface where those contracts must converge without semantic collapse.

## 70% diaspora

The historical PR #154 `to_1337speak()` 70% probability threshold remains an **initial rollout parameter** for incremental character-level variability. It is not an index score, confidence threshold, or compression ratio. Exact round-trip mapping remains the invariant.
