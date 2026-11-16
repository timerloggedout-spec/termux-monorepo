# ITEMS — continuous-capability-evolution-lab

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| CCEL-001 | P1 | executing | Establish CEEL architecture, boundaries, participant families, and source-of-truth map. | CEEL reuses Integration Intelligence, DoE, ATES, Delphi and proposal authorities; no parallel control plane. |
| CCEL-002 | P1 | executing | Define capability opportunity graph, strict JSON Schema, seed inventory and deterministic validator. | Graph parses; node IDs unique; edge endpoints resolve; lifecycle/provenance states explicit; tests cover valid, duplicate, unresolved and malformed cases. |
| CCEL-003 | P1 | executing | Register platform candidates and define fair comparison. | Candidate states remain evidence-qualified; comparison includes native baseline, treatments and interactions. |
| CCEL-004 | P1 | executing | Define event-driven awareness and GitHub-native trigger mapping. | Native events primary; bounded cursor reconciliation fallback; no duplicate scheduler. |
| CCEL-005 | P1 | queued | Define DoE campaign admission, execution, analysis and promotion evidence. | Shared cohort/configuration identity, immutable run evidence, randomization/blocking, interaction analysis, uncertainty, costs and fail-closed promotion. |
| CCEL-006 | P1 | queued | Document FOSS template inspiration, benefit compounding and evolutionary reuse. | Candidates have source provenance/disposition; reuse and combinations measured; Pareto trade-offs visible. |
| CCEL-007 | P0 | proposed | Establish MOSAIC (Methodology Optimization, Self-assessment, Adaptive Intelligence & Calibration) as CEEL's meta-methodology program within the existing DoE family. | MOSAIC specification names the boundary; reuses DoE/ATES/Delphi/SHE/3L0/MoneyBall/CEEL; no parallel registry, ledger, scheduler or authority. |
| CCEL-008 | P0 | executing | Reconcile methodology self-application and define Sigil-Operator Notation (SON) micro-dense DO statements. | #1959 and #1963 fetched and reconciled as open/parked RFPs; immutable method identity, preregistration, independent evaluation, versioned outcomes and promotion gates specified; SON lexicon and examples documented. |
| CCEL-009 | P1 | proposed | Preregister a bounded method-selection tournament. | Frozen baseline/cohort, explicit method arms, independent evaluator, budget, stopping rule, uncertainty and held-out confirmation; no live dispatch until authorized. |
| CCEL-010 | P2 | proposed | Evaluate adaptive and recursive MOSAIC revisions. | Bounded recursion, independent evaluator, valid adaptive inference, Pareto outcomes and rollback evidence. |

| MOS-007 | P0 | proposed | Connect the MOSAIC methodology specialist to the shared root Brain through a versioned, acyclic extension contract and verified host composition; preserve MOSAIC under `archwiz/mosaic_brain/`. | Root kernel remains domain-neutral; MOSAIC depends on `termux-brain` and implements the contract; host composes both without a duplicate registry or state authority; cross-crate tests pass; explicit shadow integration proves correlation and zero canonical state mutation; operational activation remains separately authorized. |

## Validation

- python3 scripts/integrations/validate_capability_graph.py
- python3 -m unittest discover -s tests -p 'test_capability_opportunity_graph.py' -v
- python3 scripts/integrations/validate_portfolio.py
- python3 scripts/proposals/validate_registry.py
- python3 scripts/ci/repo_gate.py
- python3 scripts/ci/termux_smoke.py

The MOSAIC addition is documentation-only. The existing CEEL graph/portfolio checks must remain green; repo-gate and Termux smoke must run on the same immutable PR head before merge. A committed specification or queued workflow is not runtime validation.
