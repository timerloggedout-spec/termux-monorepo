# ArchWiz data-flow manifest — work items

**Proposal:** archwiz-data-flow-manifest  
**Scope:** local scanner and manifest generation, provenance, coverage, and downstream command status.

| ID | Work item | Acceptance evidence | State |
|---|---|---|---|
| ARCH-SNAPSHOT-001 | Make scanner and manifest inputs/outputs explicit and checkout-relative while preserving current default local paths. | CLI fixture tests cover paths with spaces, missing inputs, symlink exclusion, and bounded file scanning. | Pending |
| ARCH-SNAPSHOT-002 | Add source SHA, tree SHA, generator version, UTC generated_at, input digests, coverage state, indexed/mapped/unmapped counts, and candidate-only mention labels. | Deterministic fixture tests verify metadata, hashes, coverage, and candidate semantics. | Pending |
| ARCH-SNAPSHOT-003 | Propagate manifest generator failures through Aether and reindex pipeline callers. | Unit and subprocess tests prove non-zero exit status and stop-on-failure behavior. | Pending |
| ARCH-SNAPSHOT-004 | Document the repaired workflow and regenerate from real local inputs. | ICM route, usage documentation, repo/Termux gates, and a local manifest receipt with source provenance. | Pending — device inputs required |
