# 2026-11-23 · Compute mesh cross-repo map ∧ result consumers

Superpowers sequence: RECON ✓ → FRAME ✓ → PLAN (this file) → ISOLATE → RED → GREEN → VERIFY.

## FRAME
- Outcome: every mesh compute result has a mapped consumer in `architecture.md`; unwired edges labeled.
- Non-goals: change lab DoE logic; touch Neon.
- Acceptance: map lists all 10 edges with state ∧ evidence; G1 ∧ G2 consumers pass tests.

## Tasks
1. Docs (this PR): `docs/architecture/flows/compute-mesh.{md,mmd}` ∧ §8 link in `architecture.md`. Test: links resolve.
2. G1 promotion consumer: `scripts/doe/clf_champion_promote.py` — RED test `tests/test_clf_champion_promote.py` (fixture champion.json ⇒ method@version row; reject incomplete generation). GREEN minimal reader via contents API.
3. G2 VM ledger ingest: extend `scripts/tracking/repo_tracking.py` with `hark-vm` source — RED test on fixture jobs.jsonl ⇒ per-surface participation counts.
4. G3: lane-events VM fallback per #5704 Δ1.
5. VERIFY: readback counts match ledger; finish branch.
