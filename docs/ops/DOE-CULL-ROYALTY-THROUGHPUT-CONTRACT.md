# Cull · Royalty · Throughput Continuity Contract

**Status:** implementation contract · cull integration pending · owner policy rate remains governed separately.

## Invariants

1. **Wallet waterfall:** cull transfers the participant's wallet balance to the configured pooled-buckets destination as the existing paired `cull_transferred` movement. The wallet transfer moves wallet value only.
2. **Royalty separation:** accrued unpaid royalties remain liabilities of their immutable origin beneficiary. Cull never transfers, burns, forfeits, nets, or reassigns those claims to the pool.
3. **Forward attribution:** eligible post-cull derivative contributions continue to accrue to the registered origin beneficiary under the effective owner-approved royalty policy. The derivative lineage and origin registration remain immutable.
4. **Settlement continuity:** accrued claims remain settleable after the origin participant is culled. Settlement is an independent append-only event, idempotent by settlement identity, with beneficiary, unit domain, amount, evidence, and source accrual references.
5. **Throughput continuity:** participant culling changes lifecycle status; it never deletes, resets, or re-keys the participant's throughput history or longitudinal card.
6. **Card projection:** cards show cumulative historical throughput and quality, plus current lifecycle state. Culled participants remain queryable and rankable in historical cohorts; active-pool rankings exclude them from current active competition while retaining their historical cohort entries.
7. **No metric fabrication:** absent throughput evidence remains null. Cull itself contributes zero task completions, zero work units, and zero throughput. Preserve pre-cull totals and timestamps.
8. **Atomic cull evidence:** one cull decision record binds participant identity, wallet balance at cull, pool destination, cull event/time, royalty disposition reference, and throughput-card snapshot reference. Wallet debit/credit remains a paired ledger transfer; royalty and telemetry journals remain independent ledgers joined by immutable references.

## Cull record contract

Required fields:

- `event_id`, `participant_id`, `culled_at`, `reason_ref`
- `wallet_id`, `wallet_balance_at_cull`, `wallet_unit`, `pool_destination`
- `royalty_account_ref`, `royalty_disposition` = `preserve_origin_claims`
- `throughput_card_ref`, `throughput_snapshot_sha256`
- `prior_lifecycle_state`, `new_lifecycle_state` = `culled`

The cull record references the independently verifiable wallet, royalty, and throughput records. It does not merge their accounting domains.

## Royalty disposition

At cull time, snapshot the origin's accrued, unsettled payable by unit domain. Preserve each claim and its evidence chain. The cull event changes the origin participant's lifecycle status only. A royalty accrual after cull resolves the immutable origin beneficiary from derivative lineage; it never resolves the beneficiary from current participant activity status.

Where an origin identity is legally or operationally retired, route payment only through an explicit owner-approved beneficiary succession event. Cull alone grants no succession authority.

## Throughput card projection

Card identity is stable: `participant_id` + cohort/generation identity. Each event appends to the same longitudinal series:

- cumulative task count / weighted task value
- cumulative successful and failed actions
- retry/error rate
- validation and quality evidence
- active duration / workflow duration
- attribution confidence
- lifecycle transitions and cull timestamp

Projection fields:

- `lifecycle_state`: `active | paused | culled | retired`
- `active_eligible`: boolean
- `historical_visible`: always true for a registered participant with evidence
- `culled_at`: timestamp or null
- `metrics_as_of`: timestamp
- `metric_epoch` and source event references

Historical cards remain visible after cull. Current active leaderboards filter by `active_eligible`; historical leaderboards include culled participants and preserve the cohort's original comparison window. Re-admission creates a new lifecycle event and active eligibility interval, never a replacement identity or reset card.

## Transaction / replay order

```text
CULL_REQUEST
  → freeze decision inputs + participant identity
  → snapshot wallet balance + throughput card + royalty payable
  → validate wallet destination + origin lineage + policy state
  → append cull decision record with all three evidence references
  → append paired wallet cull transfer
  → retain royalty claims; continue origin accrual routing
  → mark participant lifecycle=culled; active_eligible=false
  → refresh card projection from full event history
  → replay + reconcile all ledgers and card projection
```

The decision record is the cross-ledger join point. Each ledger keeps its own hash chain, idempotency key, and verifier. A partial execution is surfaced as pending/reconciliation-required and resumes idempotently; it never silently drops the royalty or telemetry leg.

## Acceptance tests

- Cull with zero royalty payable: wallet transfer succeeds; origin record and card remain.
- Cull with accrued unpaid royalty: payable amount and beneficiary remain unchanged; settlement after cull succeeds.
- Post-cull derivative contribution: accrual resolves the original beneficiary and policy version.
- Cull does not create royalty accrual, settlement, reversal, or pool credit.
- Throughput history before and after cull folds to identical cumulative totals; lifecycle metadata changes only.
- Historical card remains visible; active ranking excludes culled participant.
- Re-admission appends a lifecycle event and continues the same longitudinal series.
- Replay after interruption reconciles all three evidence legs without duplicate transfers or accruals.
