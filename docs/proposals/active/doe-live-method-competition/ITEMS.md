# ITEMS — doe-live-method-competition

| ID | Item | State | Evidence / exit condition |
|---|---|---|---|
| DLM-001 | Publish the live-mode DOE framework (substitution map, unit rules, fair-competition rules, contract shape) | done | PROPOSAL.md on proposal branch (PR #1848) |
| DLM-002 | Register in canonical proposal registry + lifecycle files | done | registry.yaml entry + MANIFEST.md + ITEMS.md on proposal branch |
| DLM-003 | Lifecycle validation green | executing | proposal-lifecycle validate-registry must pass on exact PR SHA |
| DLM-004 | Derived quota census (#1595) merged and exposing runs_per_day / decision_node | posted | prerequisite: run-budget ledger for every experiment contract |
| DLM-005 | Cadence reconciliation fan (#1596) live | posted | prerequisite: observed-vs-planned dispatch integrity gate |
| DLM-006 | Pilot 1 contract: context routing x CedrLang compression | posted | factor levels from Linguist PRs #1607/#1642/#1679; outcomes: semantic fidelity, token density, decode failures |
| DLM-007 | Pilot 2 contract: dispatch topology x quota policy | posted | dispatcher node verdict timing x max-parallel/max-busy; outcomes: queue delay, admission pauses, settled-build rate |
| DLM-008 | Lane/artifact coverage ledger with dispositions | posted | Phase 1-2 deliverable; unknowns and blocked areas must be visible |
