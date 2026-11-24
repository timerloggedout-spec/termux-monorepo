# ITEMS — brr-cross-repo-doe

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| BRRDOE-001 | P1 | executing | Register the separate cross-repository BRR DoE lane and define its source/authority boundaries. | Proposal and campaign are registered; BRR, #5552, #5640, context graph, and DoE ownership are explicit; no duplicate collector/scheduler/queue is introduced. |
| BRRDOE-002 | P1 | executing | Preregister a blocked four-arm retrieval comparison over frozen cross-repository evidence and an adjudicated task set. | Lexical, BRR, graph, and fused arms; factors, blocks, metrics, thresholds, source identity, and decision rules are pinned in DESIGN.json; state remains design-only pending runtime inputs. |
| BRRDOE-003 | P1 | executing | Implement a deterministic offline evaluator for supplied BRR/commit/regression/graph snapshots. | Repository-qualified identity; verified/candidate separation; partial coverage; untestable states; and deterministic rankings have regression tests. |
| BRRDOE-004 | P1 | queued | Validate exact-head CI and integrate with the existing VM-published cross-repository evidence cycle. | Python tests, canonical EXPERIMENT schema, proposal registry, repo-gate, and termux-smoke pass; runtime receipts bind to source SHA and complete coverage; at least one consumer read is evidenced. |

## Validation commands

```bash
python3 -m unittest tests.test_brr_cross_repo_doe -v
python3 -m py_compile experiments/doe/brr-cross-repo-doe/evaluate.py
python3 scripts/proposals/validate_registry.py
python3 scripts/ci/repo_gate.py
python3 scripts/ci/termux_smoke.py
```

## State discipline

A committed design is `COMMITTED`; a CI execution is `EXECUTED`; passing tests on the exact source SHA is `VALIDATED`; a live BRR export and named consumer read are separate runtime acceptance evidence. The private-store dependency currently keeps live execution pending.
