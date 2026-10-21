# ITEMS — lane-compounding

| ID | Item | Status | Evidence / notes |
|----|------|--------|-----------------|
| LC-001 | Dashboard + lane matrix fetch raw master JSON first, baked copy as fallback | executing | this PR; verify served page shows master generated_at |
| LC-002 | Drop data-path triggers from help-wanted-dashboard-deploy.yml once LC-001 is verified | proposed | saves Actions minutes and token calls; needs operator OK |
| LC-003 | Beta posteriors per lane/repo from tribute receipts | proposed | reuse scripts/bayesian_routing.py |
| LC-004 | Markov tribute-state chain | proposed | new reducer, read-only over JSONL |
| LC-005 | ATES VOI ranking of next audit/scout using DAG criticality | executing | Issue #1443: audit existing dependency_phase_engine.py, document dependency direction, add invariant tests, and separate execution readiness from probability propagation and corpus checkpoint eligibility. See DAG-EXECUTION-AND-CORPUS-AUDIT.md. |
| LC-006 | ForeSight forecast receipts + HindSight reflect scoring loop | proposed | HindSight store decision gated on LC-007 |
| LC-007 | Blind evaluation of n8n / Bifrost / Temporal / Neon / Platform201 / JSONL-control treatments | proposed | blind-agent-evaluation skill; MoneyBall/3L0 ranking |
| LC-008 | Decide fate of #1277 Neon lane_events writer | blocked | operator decision |
| LC-009 | Proactive quota admission and production evidence reconciliation | proposed | Connect #1441 quota preflight limits, #1443 DAG readiness, and #522 provenance. No claims of distributed locking, per-minute quota visibility, or live provider validation without evidence. |
