# ITEMS — lane-compounding

| ID | Item | Status | Evidence / notes |
|----|------|--------|------------------|
| LC-001 | Dashboard + lane matrix fetch raw master JSON first, baked copy as fallback | executing | verification 2026-11-03 FAIL (Docs lane, firsthand): raw-first URL names `docs/ops/generated/Tribute-status.json` (capital T) → 404 on master (file is `tribute-status.json`); served page loads the baked fallback, so the mechanism is not live; charts loader likewise baked-first with a dead pre-rename fallback path. See MANIFEST decisions of record |
| LC-002 | Drop data-path triggers from tribute-dashboard-deploy.yml (Pages redeploy per status push) once LC-001 is verified | held | APPROVED 2026-11-03 (owner delegation to main) conditioned exactly on LC-001 verification; verification FAIL → held per the condition; data-path triggers NOT dropped |
| LC-003 | Beta posteriors per lane/repo from tribute receipts, emitted into tribute-status.json | authorized | reuse scripts/bayesian_routing.py · authorized 2026-11-03 (owner delegation to main), Hark executor, outputs via MoneyBall/3L0 |
| LC-004 | Markov tribute-state chain (STAKE→SOLUTION→MERGED/CLOSED) | authorized | new reducer, read-only over JSONL · authorized 2026-11-03 (owner delegation to main), Hark executor, outputs via MoneyBall/3L0 |
| LC-005 | ATES VOI ranking of next audit/scout using DAG criticality | authorized | dependency_phase_engine.py; see DAG and corpus audit dossier · authorized 2026-11-03 (owner delegation to main), Hark executor, outputs via MoneyBall/3L0 |
| LC-006 | ForeSight forecast receipts + HindSight reflect scoring loop | authorized | HindSight store decision gated on LC-007 · authorized 2026-11-03 (owner delegation to main), Hark executor, outputs via MoneyBall/3L0 |
| LC-007 | Blind evaluation of n8n / Bifrost / Temporal / Neon / Platform201 / JSONL-control treatments | authorized | blind-agent-evaluation skill; MoneyBall/3L0 ranking · authorized 2026-11-03 (owner delegation to main), Hark executor |
| LC-008 | Decide fate of #1277 Neon lane_events writer (keep no-op, convert to JSONL writer, or mirror) | decided | DECIDED 2026-11-03 (overtaken by events): #1277 writer LIVE as the Neon lane-events recorder under the 2026-10-28 end-to-end provisioning (recorder run 40770746018, rows verified; Neon = primary store per owner scope correction); keep-no-op branch dead |
