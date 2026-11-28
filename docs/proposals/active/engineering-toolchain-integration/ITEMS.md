# ITEMS — engineering-toolchain-integration

| ID | Item | Priority | Status | Owner lane | Evidence of completion | Dependencies |
|---|---|---:|---|---|---|---|
| ETI-01 | Establish independent engineering taxonomy and FOSS/free-tier tool catalog. | P1 | executing | Engineering Architecture | Validated taxonomy with polyhierarchy, controlled axes, source links, license/access metadata, portable formats and ordered toolchains. | None |
| ETI-02 | Wire engineering discovery into the Termux Agentic Hub. | P1 | executing | Termux Hub Runtime | Named shell-free taxonomy-validation and read-only tool-inventory capabilities with deterministic tests. | ETI-01 |
| ETI-03 | Surface engineering capabilities in ArchWiz and the operator index. | P1 | executing | ArchWiz / QDesk | Tool index, skill discovery and ArchWiz cockpit menu option [21] point to canonical engineering registry and probe. | ETI-01, ETI-02 |
| ETI-04 | Bind engineering work to existing QUE/QDesk admission and execution. | P1 | executing | QUE / QDesk | Engineering issue form declares issue-dispatch/v1, tier 3 and existing project-task route; tests verify admission matching and the QUE parser contract. | ETI-01, ETI-03 |
| ETI-05 | Connect toolchain benchmarks to DoE/MVT/ATES and Learnings. | P1 | executing | DoE / MVT / ATES | Experiment factors, immutable fingerprints, repeated arms, terminal states, evidence receipts and learning handoff. | ETI-01, ETI-02 |
| ETI-06 | Cross-link engineering with Reverse Engineering and refTemplates. | P1 | executing | Reverse Engineering / Research | Shared artifact and hardware/firmware links with independent taxonomies, pinned source lineage and citation-only cross-surface references. | ETI-01 |
| ETI-07 | Define free/no-card remote execution for GUI and compute-heavy tools. | P1 | executing | Tooling / Delivery Reliability | Runner capability matrix, install provenance, resource budgets, network boundary, artifact retention and cost/card gate. | ETI-01, ETI-02 |
| ETI-08 | Verify device runtime and current-SHA repository gates. | P1 | blocked_external | Termux Runtime / Delivery Reliability | Live Termux inventory receipt, tests, repo-gate, termux-smoke, exact SHA and review evidence. | ETI-02, ETI-03, ETI-04, ETI-05, ETI-07 |

## Execution boundary

ETI-01 and ETI-02 are implemented in this branch as repository-native catalog and read-only capability work. ETI-03 through ETI-07 remain scoped integration slices. ETI-08 requires an actual device-side Termux call and current-SHA gate receipts. Promotion remains subject to the repository's dual gates and review.
