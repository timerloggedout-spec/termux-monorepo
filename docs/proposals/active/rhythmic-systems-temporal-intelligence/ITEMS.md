# ITEMS — rhythmic-systems-temporal-intelligence

| ID | Item | State | Evidence / exit condition |
|---|---|---|---|
| RS-001 | Temporal assignment windows, phase classification, collector cadence, and WAIT wake policy | implementing | timezone-aware unit tests; DST-fold elapsed-time regressions; QUE lifecycle fixtures; repo gate |
| RS-002 | Exact-ratio rhythmic overlay, rational supercycles, Jazz division taxonomy, and polyphonic roles | implementing | `deepcli/deepcli/observatory/rhythm.py`; `deepcli/tests/test_rhythm.py`; Jazz taxonomy JSON validation; `music/jazz-3-2-offbeat.strudel.js` |
| RS-003 | Ballet Coordinator and Orchestra Conductor cue-sheet placements | implementing | dependency-wave tests; all three placement tests; phase/open-length/barrier/evidence cue-sheet contract; cohort-isolated DoE tests |
| RS-004 | Music as Code independent and mixed-mode stimulus paths | implementing | `music/jazz-3-2-offbeat.strudel.js`; `docs/ops/RHYTHMIC-SYSTEMS-TEMPORAL-INTELLIGENCE.md`; Strudel source syntax validation; independent/mixed-mode documentation; runtime rendering qualification |
| RS-005 | Temporal DoE factor registration and shared notation cross-domain mappings | implementing | DoE matrix v2 registration in DOE-FAMILY and settings register; NSE-025 crosswalk; proposal-lifecycle validation |
| RS-006 | Brain/CNS-inspired Composer, signal/context/intent modules, and deterministic score contract | implementing | signal collision and confidence tests; bounded attention focus; focused-signal retention in bounded context; intent validation; deterministic action shortlist; timing/wake tests; canonical ATES receipt resolution; policy-sensitive score ID; Conductor cue metadata preservation; repo gates |
| RS-007 | Production runtime invocation of Composer from the owning Manager/QUE or collector workflow | planned | selected runtime owner; canonical ATES receipt resolver; event/wake input mapping; end-to-end receipt-to-score evidence; workflow and promotion gates |

## Acceptance contract

- Preserve dependency-phase readiness, QUE admission/claim ownership, specialist execution, and ATES evidence authority.
- Keep architecture seed, Conductor placement, wave strategy, and temporal treatment as independent experimental axes.
- Require canonical ATES receipt resolution, full-factor arm identity, cohort-local rankings, and disjoint winner/loser sets.
- Preserve failed, censored, skipped, and inconclusive experimental arms.
- Promote implementations only after the exact candidate SHA passes the repository gates.
