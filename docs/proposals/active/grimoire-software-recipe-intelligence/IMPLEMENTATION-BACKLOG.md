> Scope correction: this backlog belongs to the existing MOSAIC Brain capability; it does not establish a GRIMOIRE product or independent system. See ../continuous-capability-evolution-lab/MOSAIC-BRAIN-SOFTWARE-RECIPE-MODEL.md and SCOPE-CORRECTION.md.\n\n# MOSAIC Brain — SRM Domain Extension Backlog

Status: proposed backlog; not implementation authorization.

| ID | Priority | Work | Deliverable | Exit criteria |
|---|---|---|---|---|
| SRM-000 | P0 | Charter, identity and collision rules | Naming registry + decision record | IDs unique; aliases and namespace rules frozen |
| SRM-001 | P0 | Canonical SRM v1 | Model specification | Required/optional/unknown semantics reviewed |
| SRM-002 | P0 | Schema + validator | JSON Schema, validator, fixtures | Positive/negative fixtures pass |
| SRM-003 | P0 | Taxonomy + Siglary bridge | Taxonomy and notation registry | Multi-label, typed, versioned; no namespace collision |
| SRM-004 | P0 | Provenance and revision identity | Digest/lineage contract | Immutable source and revision refs |
| SRM-005 | P1 | Read-only extraction | Git, docs, manifests, workflows, tests adapters | Source provenance on every extracted fact |
| SRM-006 | P1 | AST/CST extraction | Tree-sitter adapter | Parser versions and parse gaps represented |
| SRM-007 | P1 | Deterministic + statistical classifier | Baseline model/evaluation | Held-out labels and calibration reported |
| SRM-008 | P1 | Similarity and duplicate search | Hybrid retrieval baseline | Precision/recall and false positives reported |
| SRM-009 | P1 | Typed relationship graph | Graph schema and builder | No dangling refs; full/incremental parity fixtures |
| SRM-010 | P2 | Retrieval and composition | Contract-aware composer | Rejects incompatible/unknown contracts |
| SRM-011 | P2 | Evaluation receipts | Execution/evaluation contract | Immutable recipe-to-run-to-result lineage |
| SRM-012 | P2 | DoE competition | Experiment reports | Predeclared metrics and held-out confirmation |
| SRM-013 | P3 | Sandboxed execution | Isolated executor adapter | Explicit admission, resource/network limits, receipts |
| SRM-014 | P3 | Bounded evolution | Revision proposal generator | No self-approval or autonomous promotion |
| SRM-015 | P3 | Operational integration | SHE/Corpus/ATES/MoneyBall projections | Existing authorities remain authoritative |

## Dependency order

```text
SRM-000 -> SRM-001 -> SRM-002 -> SRM-003 -> SRM-004
                                  |
                                  v
SRM-005 -> SRM-006 -> SRM-007 -> SRM-008 -> SRM-009
                                                |
                                                v
                                      SRM-010 -> SRM-011
                                                    |
                                                    v
                                                SRM-012
                                                    |
                                    separate admission gate
                                                    v
                                      SRM-013 -> SRM-014
                                                    |
                                                    v
                                                SRM-015
```

## Explicit non-goals for initial implementation

- No production workflow replacement.
- No rewrite of Commit Replay or Repo Replay.
- No replacement for Kahn DAG, Gantt, Bayesian routing, Markov research, package managers, SBOMs, or Git.
- No secret retrieval or storage.
- No external network calls from extracted recipe content.
- No automatic PR merge, deployment, or permission expansion.
- No self-modification of governance policies.

## Review checklist

- [ ] Existing implementation census completed.
- [ ] Commit Replay / Repo Replay overlap reviewed.
- [ ] Existing Context Relationship Graph overlap reviewed.
- [ ] Existing DoE component and Delphi segment registries reviewed.
- [ ] SRM schema and naming collision review completed.
- [ ] Security/privacy review completed.
- [ ] DoE protocol preregistered before collecting comparison outcomes.
- [ ] Source package and decision provenance pinned.
