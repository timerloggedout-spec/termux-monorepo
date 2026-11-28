# ITEMS — cell-the-living-machine

| ID | Item | Priority | Status | Owner lane | Evidence of completion | Dependencies |
|---|---|---:|---|---|---|---|
| CLM-01 | Establish the ArchWiz scope profile, game-specific project manifest, and project registry entry. | P1 | in_review | Orchestration & Quality Control | Scope profile validated by `ops/projects/profile.schema.json`, manifest, registry entry, stable project ID, repository and lane references. | None |
| CLM-02 | Reconcile Research Astute and Search Astutely identity, ownership, access, and reuse boundaries. | P1 | proposed | Research & Intelligence | Verified repository/org identity, connector capability record, rights review, and source-plane contract. | CLM-01 |
| CLM-03 | Map molecular biology databases and cross-reference identifiers for structures, sequences, annotations, pathways, molecules, and literature. | P1 | in_progress | Research & Intelligence | 26-source candidate catalog, API/terms records, identifier crosswalk, sample records, and provenance fields. | CLM-01 |
| CLM-04 | Inventory the full iJEP Studio channel and derive a source-linked content graph. | P1 | in_progress | Research & Intelligence + Game Design & Systems | 125 upload records indexed; per-video transcripts, linked sources, structure IDs, technical comments, and asset-use disposition. | CLM-02, CLM-03 |
| CLM-05 | Define game loop, simulation scope, progression, genre facets, and shared knowledge lenses. | P1 | proposed | Game Development & Production | Reviewed game design, mechanics map, lens contract, and representative learning paths. | CLM-03, CLM-04 |
| CLM-06 | Establish scientific provenance, asset rights, and science-integrity review contracts. | P1 | proposed | Game QA & Accessibility + Research & Intelligence | Per-claim/per-asset source records, evidence classes, confidence fields, and reviewer checklist. | CLM-03, CLM-04 |
| CLM-07 | Provision dedicated game repository and connect it to the MonoRepo project profile. | P1 | blocked_external | Orchestration & Quality Control | Repository ID, default branch, license decision, CI identity, and profile link. | CLM-01 |
| CLM-08 | Select engine and build a bounded vertical slice with one cell membrane and three mechanisms. | P1 | proposed | Game Development & Production | Reproducible build, playable scenario, deterministic tests, and independent QA evidence. | CLM-03, CLM-05, CLM-06, CLM-07 |
| CLM-09 | Establish search-result aggregation and research-seed synchronization with Search Astutely. | P1 | blocked_external | Research & Intelligence + Delivery Reliability | Verified API/connector, source snapshots, stable IDs, deduplication, update cadence, and failure-state tests. | CLM-02 |
| CLM-10 | Establish cross-repository integration contracts, release provenance, and link validation. | P2 | proposed | Delivery Reliability / CI-CD | Manifest contract, repository identity checks, source revision pins, and CI validation. | CLM-01, CLM-07, CLM-09 |

## Execution boundary

CLM-01 is the initial documentation/control-plane increment. CLM-02 through CLM-06 are research and design increments. CLM-07 and CLM-09 depend on external account/API actions. CLM-08 begins after the project repository, source map, and acceptance contract are ready.
