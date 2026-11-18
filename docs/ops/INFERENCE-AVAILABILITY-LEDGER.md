# Inference availability ledger (#5546 ∧ #5576)

DO publish per-endpoint `{limit, measured, last_ok}` from measured fleet evidence; quoted limits stay in `limit`, measurements stay in `measured_*`.

- Builder: `scripts/inference/availability_ledger.py` ⇒ `ops/inference/availability-ledger.json` (current) ⊕ `ops/inference/availability-ledger.jsonl` (append-only cycle history).
- Workflow: `.github/workflows/inference-availability-ledger.yml` (daily 13:23 UTC ∨ dispatch) ⇒ branch `inference-ledger` carries cycle state; the master copy = seed cycle.
- Measured sources: `ops/3l0/intake.jsonl` ⊕ `experiments/doe/routed-dispatch/{records,stamps}` ⊕ `ops/quota/quota-probe-ledger.jsonl` ⊕ `--extra` JSONL streams (VM spend logs once exported). CI runs ∉ inference calls.
- Target: 7,500 measured calls/day; `target_met`, `gap_calls_day`, `best_measured_day` report the honest standing.
- Allocation (feeds #5576 pre-scoped budgets): endpoints with success ≤ 72h ∧ known daily limit ⇒ min(limit_day, target share); success ≤ 72h ∧ unknown limit ⇒ 2 × measured_24h; else probe-only (1/day). `delta_vs_prior` records the Δ vs the previous cycle.
- Coverage gap: calls executed on the VM ∨ seats without a committed record stay unmeasured ⇒ export the VM spend log as an `--extra` stream to close it.
