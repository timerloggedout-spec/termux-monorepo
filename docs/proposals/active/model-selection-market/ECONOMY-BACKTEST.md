# Economy Backtesting — MSM-026

**Implementation:** `scripts/model_selection_market/economy_backtest.py`
**Schema:** `schemas/economy-backtest.schema.json`
**Tracking:** #5351
**Version:** `economy-backtest/v1`

## Purpose

Run deterministic, seeded policy experiments over a synthetic participant economy. Preserve each exact manifest and result as immutable JSON artifacts. Compare reward, cull, pool-recycling, and hypothetical royalty policies under common seeds.

## Current evidence boundary

Version 1 is a **synthetic cohort simulator**. It does not yet ingest historical event journals or claim an empirical backtest of observed economy behavior. The first run establishes a reproducible baseline and validates accounting invariants. Historical event replay becomes a later adapter after event provenance and participant identity mapping are reconciled.

## Model

Each participant has a success probability in basis points, initial paper-point balance, and optional origin participant. Each round:

1. Draw a deterministic task outcome using the manifest seed.
2. Issue the configured gross paper-point reward for a success.
3. Accrue a hypothetical origin royalty from gross reward when a derivative participant names an origin.
4. Cull participants after the configured consecutive miss threshold and transfer their remaining wallet balance to the promotions/incentives/bonuses pool.
5. Distribute the configured fraction of the pool to active contributors, pro rata by successful tasks; retain any undistributed remainder.

Royalty payables stay separate from participant balances and pool value. The simulator preserves accrued claims for an origin even after that origin is culled.

## Conservation

`initial_units + issued_units = participant_balance_units + pool_remainder_units + royalty_payable_units`

Pool distributions are transfers. Royalty accrual is carved from gross reward and recorded as a separate payable. The conservation residual must equal zero.

## Metrics

- issuance, participant balances, pool inflow/distribution/remainder
- royalty accrual/payable and beneficiary count
- task success rate, active retention, cull count
- pool recycling rate, balance Gini, balance HHI
- conservation residual

## Reproduction

```sh
python -m scripts.model_selection_market.economy_backtest \
  --manifest experiments/model-selection-market/economy-backtest/scenarios/baseline.json \
  --output-dir artifacts/economy-backtests
```

The run ID binds the normalized manifest, synthetic cohort digest, simulation version, exact implementation commit SHA, and Python runtime fingerprint. The CLI resolves the commit from `GITHUB_SHA` or the checked-out Git HEAD; use `--code-commit` to pin it explicitly. The result digest covers metrics, balances, event sequence, and royalty payables. Artifact writes use create-once semantics; identical reruns verify existing bytes and changed content at the same path raises an error.

## Policy comparison

Use `run_matrix(base_manifest, policy_variants, seeds)` or the committed `policy-matrix.json` to compare policies across common seeds. The matrix pins four policy variants × ten seeds (40 deterministic replications). Pre-register policy variants and seeds before reading results. Report means and per-seed rows; add confidence intervals and temporal holdouts when historical observations support them.

The sample manifest sets royalty rate to zero. The test suite explores nonzero rates strictly as sensitivity hypotheses; the repository's owner-approved royalty percentage remains unset.

## Promotion gates

1. Run offline deterministic tests and conservation checks.
2. Record baseline and at least three policy variants over a fixed seed set.
3. Reconcile model assumptions against historical ledger evidence.
4. Add temporal train/validation/test splits and walk-forward evaluation after sufficient observed periods exist.
5. Require independent review and explicit policy approval before any economic policy promotion.

Synthetic outputs remain `exploratory_synthetic`; keep them separate from MoneyBall scores, observed contribution outcomes, wallet authority, and settlement records.
