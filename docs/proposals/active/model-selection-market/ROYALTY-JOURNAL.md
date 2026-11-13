# MSM-025 — Origin-attributed residual royalty journal

**Implementation:** `scripts/model_selection_market/royalty_ledger.py`
**Contract tests:** `tests/test_royalty_ledger.py`
**Tracking:** #5350
**Version:** `origin-royalty-journal/v1`

## Purpose and authority boundary

Maintain code-to-legacy residual claims as an independent append-only liability journal. Keep origin attribution and payable balances separate from MSM participant wallets, paper-point issuance, cull dispositions, consolidation pools, MoneyBall scores, and external settlement rails.

The journal records entitlement and settlement evidence. It does not authorize payment, move assets, sign transactions, create wallets, or connect to a chain. Any payment adapter requires its own authorization, idempotency domain, reconciliation, and custody controls.

## Artifact lineage

Register each original artifact with immutable artifact ID, SHA-256 content digest, and origin actor. Register derivatives with immutable digest, author, and parent artifact references. Each parent reference includes a source-range/lineage reference and SHA-256 evidence digest. Parent weights use integer basis points summing to 10,000. Derivative lineage is computed from parent lineage using deterministic largest-remainder allocation and lexical tie-breaking.

This supports split/cherry-pick and merge lineage: a derivative can retain shares from multiple original artifacts, and later derivatives inherit those shares. Supersession records connect an earlier artifact to its replacement while preserving prior attribution and accrued claims. Historical events remain append-only.

## Policy activation

Activate a policy version only when the configured policy owner supplies:
- policy ID and monotonic version identifier
- basis-point rate and named basis definition
- effective-from and optional effective-until timestamps
- owner identity, timezone-aware approval timestamp, and SHA-256 approval evidence digest

The current v1 basis is `gross_reward_units`. Policy versions for the same policy ID use non-overlapping effective intervals. The Python module verifies owner identity and evidence shape; an external governance workflow must authenticate the owner and verify the approval evidence digest. The rate remains unset until an owner-approved policy event is appended.

## Accrual and payable lifecycle

Each accrual binds a unique contribution ID, derivative artifact, policy version, basis units, event time, and unit domain. Calculate total royalty as integer basis-point arithmetic; allocate the result across inherited origins deterministically. Keep separate payable balances by beneficiary and unit domain (`paper_point`, `test_token`, or `production_asset`).

Each claim supports:
- partial settlement against a named accrual and origin artifact, with destination, evidence digest, and unique idempotency key
- dispute, which freezes settlement for the accrual
- reversal of unsettled units with reason and evidence
- supersession of derivative lineage without rewriting past accruals

Settlement records are evidence only; external transfer remains a separately authorized adapter operation. A reversal cannot consume already-settled units. A dispute can be cleared only by a governed compensating workflow in a later journal version; v1 leaves disputed claims frozen.

## Culling and pool treatment

The royalty journal is independent from the MSM-005 market journal. Culling a participant or donating their wallet balance to a consolidation pool leaves origin registration, derivative lineage, accrued payables, and future eligible derivative claims unchanged. Pool donations and distributions never debit royalty liabilities. The origin actor can remain a royalty beneficiary after their participant wallet is culled.

## Replay and idempotency

Use the existing durable EventStore framing and exclusive file lock, with a separate JSONL file path from the market event stream. Validate each candidate transition against a replayed state before append. Exact event retries return the original event; conflicting event ID reuse, duplicate contribution IDs, duplicate settlement idempotency keys, duplicate artifact IDs, invalid lineage, policy overlap, and over-settlement fail before append.

A replayed snapshot includes origin and derivative lineage, policy versions, accruals, payable balances, settlements, reversals, disputes, supersessions, event count, and event digest.

## Verification

```sh
python3 -B -m unittest tests.test_royalty_ledger -v
```

Tests cover split/merge lineage, deterministic allocation, policy owner approval, accrual, partial settlement, duplicate protection, dispute, reversal, supersession, replay, and append-before-validation protection.

## Future extensions

- Governance-authenticated approval signatures and policy registry.
- Dispute resolution events and settlement reversal/chargeback lifecycle.
- Contribution-to-artifact provenance adapters from GitHub merge/SHA evidence.
- Multi-currency valuation and explicit FX policy, each isolated by unit domain.
- Payment adapters with per-rail custody, authorization, and reconciliation.
