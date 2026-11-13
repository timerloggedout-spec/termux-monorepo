# Economy backtest results — 2026-11-13

**Simulation:** `economy-backtest/v1`
**Implementation commit:** `81890b9284e25decdfd73077938318f7a8d6259f`
**Runtime:** Python 3.14.4
**Scenario:** `economy-pilot-cohort-001`
**Matrix:** 4 policy variants × 10 fixed seeds = 40 runs
**Matrix digest:** `a20f63bb7781c1be7a81d13a6e478e606784aad1f4b44c9ef86aab75f07be674`
**Source digest:** `f2e9d4579dad4b514e670f29491e59f9a2a5d1d84e06689fa6afe3f42d3747ed`
**Run index:** [matrix-summary.json](./matrix-summary.json)

## Scenario

Six synthetic participants; 30 rounds; 100 paper-point units per successful task. Initial balances total 2,700 units. Seeds: 11, 22, 33, 44, 55, 66, 77, 88, 99, 111. The same seed set is applied to every policy variant.

## Mean results across ten seeds

| Policy | Active | Culled | Retention | Task success | Balance Gini | Balance HHI | Pool distributed | Pool remainder | Royalty accrued |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline-0bp | 3.5 | 2.5 | 58.33% | 62.38% | 0.48254 | 0.36776 | 1,946.6 | 287.3 | 0 |
| recycle-5000bp | 3.5 | 2.5 | 58.33% | 62.38% | 0.48225 | 0.36764 | 2,207.9 | 61.8 | 0 |
| resilient-cull-6 | 4.8 | 1.2 | 80.00% | 59.87% | 0.31737 | 0.22947 | 728.4 | 269.4 | 0 |
| royalty-250bp | 3.5 | 2.5 | 58.33% | 62.38% | 0.48293 | 0.36809 | 1,940.1 | 286.3 | 71.2 |

All 40 runs report a conservation residual of exactly zero.

## Interpretation

- **Cull threshold:** raising the miss threshold from 4 to 6 increases mean retention from 58.33% to 80.00% and reduces balance Gini from 0.48254 to 0.31737 in this cohort. Task success rate falls from 62.38% to 59.87%; the retained lower-probability participants add attempts and alter the denominator. Test broader cohorts and longer horizons before selecting a policy.
- **Pool recycling:** increasing distribution from 25% to 50% raises distributed units by 261.3 and reduces the mean pool remainder from 287.3 to 61.8. Inequality changes only slightly in this run.
- **Royalty sensitivity:** the 250-basis-point scenario accrues 71.2 units on the simulator's hypothetical gross-reward basis and slightly increases Gini/HHI. This is exploratory sensitivity only. It establishes neither an owner-approved rate nor a royalty basis or future eligibility rule. See #3747, #3748, and MSM-025.
- **Conservation:** every run satisfies initial + issued = participant balances + pool remainder + royalty payables.

## Provenance and artifacts

- Workflow run: [43466642190](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/43466642190)
- Job: `132027429015`
- Artifact ID: `14059486675`
- Artifact ZIP SHA-256: `45ff4e64a195fdb58683accc18a32cad8851b04700c8f1a479b81a58fdbca453`
- Artifact size: 223,691 bytes; Actions retention: 90 days
- Baseline single-run ID: `2bb38863331247b547836dbe2a1d2442076b20ec35d6fc3468e048f238d54474`
- Baseline result digest: `4281d95d74b974dbc7bb03b23a1f16ade48ae337567cd4e49cbfd47d62df1f96`

The version-controlled matrix summary preserves the 40 run IDs, per-run result digests, policy/seed mapping, aggregate metrics, and artifact checksum. The Actions artifact contains full event streams and individual manifests/results.

## Evidence classification

**Evidence classification: EXPLORATORY SYNTHETIC**

These results are a deterministic simulation baseline, not a historical backtest of observed participant activity. No wallet provisioning, testnet transaction, real-value settlement, or production policy selection follows from this run. Add a verified historical event adapter, cohort identity reconciliation, temporal holdouts, and walk-forward evaluation before treating results as predictive evidence.
