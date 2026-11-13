# Economy backtest v2 results — 2026-11-13

**Simulation:** `economy-backtest/v2`
**Implementation commit:** `72a7dd92f9d3f9e1dc595ea656fd278f608438c3`
**Scenario:** `economy-pilot-cohort-001`
**Matrix:** 4 policy variants × 10 fixed seeds = 40 runs
**Baseline:** `baseline-0bp`
**Randomization:** `sha256_keyed_participant_round_v1`
**Matrix digest:** `57735cf1cc742ead7df656ce3876cf0c1a2dfbde309d540dd334a97e2f3dffcb`
**Source digest:** `f2e9d4579dad4b514e670f29491e59f9a2a5d1d84e06689fa6afe3f42d3747ed`
**Summary:** [matrix-summary.json](./matrix-summary.json)

## Method

Version 2 keys each random draw by seed, round, and participant ID. This provides common random numbers across policy variants even when cull thresholds change who remains active. The first declared policy is the baseline. The matrix reports per-policy 95% normal-approximation intervals and paired per-metric deltas with 95% intervals versus that baseline.

## Mean results across ten seeds

| Policy | Retention | Task success | Balance Gini | Pool distributed | Pool remainder | Royalty accrued |
|---|---:|---:|---:|---:|---:|---:|
| baseline-0bp | 63.33% | 62.09% | 0.44261 | 1,718.9 | 207.7 | 0 |
| recycle-5000bp | 63.33% | 62.09% | 0.44249 | 1,896.5 | 56.1 | 0 |
| resilient-cull-6 | 90.00% | 58.89% | 0.25025 | 439.7 | 86.4 | 0 |
| royalty-250bp | 63.33% | 62.09% | 0.44279 | 1,713.1 | 207.7 | 74.0 |

## Paired deltas versus baseline

- **Pool recycle 50%:** +177.6 distributed units; −151.6 pool remainder. The 95% interval for the paired remainder delta is [−284.10, −19.10].
- **Resilient cull threshold 6:** +26.67 percentage points retention; −3.20 percentage points task success; −0.19237 balance Gini.
- **Hypothetical royalty 250 bp:** +74.0 royalty units; the 95% paired interval is [62.47, 85.53]. This is sensitivity only, not an approved rate or basis.

All 40 runs have a conservation residual of exactly zero.

## Provenance

- Workflow run: [43493132656](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/43493132656)
- Artifact ID: `14071171427`
- Artifact ZIP SHA-256: `67b2f7a23ef9c02b6d1f5b9c3463a1b0b761ac6417c6b499db0cb539dc6f10ff`
- Artifact size: 225,508 bytes; retention through 2027-02-11
- Runtime: Python 3.14.4

The CI artifact contains all 40 immutable run manifests/results and the complete matrix. The checked-in summary preserves the exact matrix/source digests, policy metrics, paired intervals, implementation SHA, and artifact checksum.

## Evidence classification

**EXPLORATORY SYNTHETIC.** Six synthetic participants, 30 rounds, and ten seeds per policy do not establish predictive performance. The paired design improves internal policy comparisons; it does not replace verified observed cohorts, temporal holdouts, walk-forward evaluation, or owner approval. No royalty rate, future derivative eligibility rule, testnet activity, or production policy is authorized by these results.
