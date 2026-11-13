# Wallet and testnet promotion gates

**Status:** policy preflight implementation; wallet provisioning and signing remain separately authorized adapter work.

## Promotion lifecycle

`PAPER → TESTNET_PREFLIGHT → TESTNET_PROVISION → TESTNET_RECONCILE → PRODUCTION_REVIEW → PRODUCTION`

1. **PAPER:** use the MSM-005 event journal and nonredeemable `paper_point` only.
2. **TESTNET_PREFLIGHT:** validate a `wallet-promotion/v1` manifest with `evaluate_wallet_manifest`. Require isolated chain ID and signer namespace, test-token asset class, bounded caps, revocation, recovery, reconciliation, monitoring, dual control, and distinct owner/security approvals.
3. **TESTNET_PROVISION:** a separately reviewed adapter creates wallets and test assets only after an approved preflight receipt. Store signer references; keep key material in an approved vault/HSM.
4. **TESTNET_RECONCILE:** reconcile chain events against the adapter's idempotent operation journal. Record transaction IDs, finality, fees, failed attempts, and balance deltas.
5. **PRODUCTION_REVIEW:** require production chain/key profile, owner + security + custody approvals, legal/custody references, caps, monitoring, revocation, recovery, and rollback.
6. **PRODUCTION:** enable only after explicit release approval and independently verified testnet evidence.

## Code boundary

`scripts/model_selection_market/wallet_promotion.py` performs deterministic, read-only manifest validation. It performs zero network calls, key generation, signing, funding, wallet creation, or settlement. Its receipt says `preflight_only`; it never asserts that a wallet exists.

Testnet and production use distinct chain IDs, signer namespaces, asset classes, credentials, and operation-idempotency domains. Treat every funding or settlement command as a separately authorized action. Preserve one source of accounting truth per rail and reconcile rail-specific events into governed projections.

## MSM-005 cull and pool integration

Record each cull decision in the paper journal, including score/evidence snapshot and explicit reservation dispositions. Route donations to the consolidation pool. Allocate pool balances through versioned, idempotent distribution events. Keep performance scores, eligibility decisions, paper balances, and testnet balances as separate domains.

## Acceptance

- Unit tests cover manifest identity, isolated chain/key namespaces, signer-reference handling, caps, approval roles, and fail-closed unknown fields.
- Testnet provisioning adapters require a passing receipt bound to the exact manifest digest plus a separate owner authorization.
- Production promotion requires fresh testnet reconciliation, dual control, custody/legal evidence, and rollback readiness.
