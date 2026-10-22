# ITEMS — ArchWiz Hyper-Forge Gemini review (proposal archwiz-hyperforge-gemini-review)

Derived from MILESTONES.yaml during the #953 rebase; states mirror the milestone states there.

| ID | Work | Priority | Owner | Status | Evidence / Boundary |
|---|---|---|---|---|---|
| HF-M0 | Source normalization and governance: canonicalize source plan terminology; separate source requirements from engineering interpretation; publish implementation matrix + engineering considerations; register proposal and link GitHub review surfaces. | P1 | ChatGPT | implemented | Issue #951. GEMINI-PLAN.md, IMPLEMENTATION-MATRIX.md, ENGINEERING-CONSIDERATIONS.md in this package. |
| HF-M1 | Termux Hyper-Forge cockpit: dependency-free ANSI/TUI cockpit; ArchWiz menu integration; capability matrix; Tron presentation mode; regression coverage; evidence/authority documentation. | P1 | ChatGPT | implemented | Issue #952. |
| HF-M2 | Foresight and ChronoMancer composition: canonical Foresight state contract; ChronoMancer session/timeline contract; correlation identifiers; end-to-end bounded-loop test; evidence receipt. | P1 | ChatGPT | partial | Issue #944. |
| HF-M3 | Dispatch and forensic capability parity: map source cockpit capabilities to repository entry points; missing-tool behavior; capability-level acceptance tests; forensic/research lane boundaries; promotion/restore safety. | P1 | ChatGPT | partial | Issue #945. |
| HF-M4 | Evidence and live operational surfaces: map live metrics to canonical evidence; Action → Effect integration; preserve COMMITTED/EXECUTED/VALIDATED/PROMOTED states; activity/narrative feed contract; artifact provenance validation. | P1 | ChatGPT | partial | Issue #946. |
| HF-M5 | Native Android presentation: shared Termux/Android protocol contract; four-tab surface (Swarm Dispatch, Forensics & RECON, Pipeline & CI, Metrics & Live); Android-specific acceptance suite. | P2 | ChatGPT | planned | Issue #947. |
| HF-M6 | Quote untrusted CLI arguments and script paths in Aether/Forge shell-backed dependency, bookmark, and lexicon commands; add injection regression tests. | P1 | Manus | implemented | PR #895 review follow-up; `tests/test_archwiz_shell_quoting.py`. |
| HF-M7 | Bind Aether/Forge function-search patterns as jq data and quote index paths; retain regex matching and cover real-shell injection regressions. | P1 | Cue | implemented | Follow-up to #1452; `tests/test_archwiz_funcfind.py`. |
| HF-M8 | Stop Aether map/reindex on failed invoked stages, propagate failing exit status, and withhold completion claims after failed generators. Preserve missing optional bloat/FTS skips. | P1 | Cue | implemented | `tests/test_aether_reindex.py`; focused failure-mode and CLI regressions, including real subprocess exit codes. |
| HF-M9 | Quote ArchWiz script paths in Aether reindex generator invocations so shell metacharacters and whitespace in the installation path remain literal. | P1 | Cue | implemented | `archwiz/aether.py`; argument-boundary and real CLI regressions in `tests/test_aether_reindex.py`; limited to manifest/tools/reference-hub paths. |
