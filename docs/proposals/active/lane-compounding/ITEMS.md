# ITEMS — lane-compounding

| ID | Item | Status | Evidence / notes |
|----|------|--------|------------------|
| LC-001 | Dashboard + lane matrix fetch raw master JSON first, baked copy as fallback | executing | this PR; verify served page shows master `generated_at` |
| LC-002 | Drop data-path triggers from help-wanted-dashboard-deploy.yml (Pages redeploy per status push) once LC-001 is verified | proposed | saves Actions minutes and GITHUB_TOKEN calls; needs operator OK |
| LC-003 | Beta posteriors per lane/repo from tribute receipts, emitted into help-wanted-status.json | proposed | reuse scripts/bayesian_routing.py |
| LC-004 | Markov tribute-state chain (STAKE→SOLUTION→MERGED/CLOSED) | proposed | new reducer, read-only over JSONL |
| LC-005 | ATES VOI ranking of next audit/scout using DAG criticality | proposed | dependency_phase_engine.py |
| LC-006 | ForeSight forecast receipts + HindSight reflect scoring loop | proposed | HindSight store decision gated on LC-007 |
| LC-007 | Blind evaluation of n8n / Bifrost / Temporal / Neon / Platform201 / JSONL-control treatments | proposed | blind-agent-evaluation skill; MoneyBall/3L0 ranking |
| LC-008 | Decide fate of #1277 Neon lane_events writer (keep no-op, convert to JSONL writer, or mirror) | blocked | operator decision |
