# Wallet and testnet promotion gates

**Status:** implement policy preflight; route wallet provisioning and signing through separately authorized adapters.

## Promotion lifecycle

`PAPER → TESTNET_PREFLIGHT → TESTNET_PROVISION → TESTNET_RECONCILE → PRODUCTION_REVIEW → PRODUCTION`

1. **PAPER:** use the MSM-005 event journal and nonredeemable `paper_point` only.
2. **TESTNET_PREFLIGHT:** validate a `wallet-promotion/v1` manifest with `evaluate_wallet_manifest`. Require isolated chain ID and signer namespace, test-token asset class, bounded caps, revocation, recovery, reconciliation, monitoring, dual control, and distinct owner/security approvals.
3. **TESTNET_PROVISION:** a separately reviewed adapter creates wallets and test assets only after an approved preflight receipt. Store signer references; keep key material in an approved vault/HSM.
4. **TESTNET_RECONCILE:** reconcile chain events against the adapter's idempotent operation journal. Record transaction IDs, finality, fees, failed attempts, and balance deltas.
5. **PRODUCTION_REVIEW:** require production chain/key profile, owner + security + custody approvals, legal/custody references, caps, monitoring, revocation, recovery, and rollback.
6. **PRODUCTION:** enable only after explicit release approval and independently verified testnet evidence.

## Local preflight

Run the read-only validator against a reviewed manifest:

```bash
python3 -m scripts.model_selection_market.wallet_promotion wallet-manifest.json \
  --production-chain-id 1 \
  --production-key-namespace prod/msm
```

The receipt binds the manifest SHA-256 and returns `action: preflight_only`, with provisioning, signing, and funding each marked false. This validator checks policy shape and identity consistency; a trusted external governance workflow must authenticate approvers and verify their evidence digests before provisioning. The JSON Schema is the structural contract; the Python gate enforces its cross-field rules and environment-specific comparisons.

## Code boundary

`scripts/model_selection_market/wallet_promotion.py` performs deterministic, read-only validation implementing the field and policy constraints documented in `schemas/wallet-promotion.schema.json`. Keep network calls, key generation, signing, funding, wallet creation, and settlement in separately authorized adapters. Its receipt says `preflight_only`; it never asserts that a wallet exists.

Testnet and production use distinct chain IDs, signer namespaces, asset classes, credentials, and operation-idempotency domains. Treat every funding or settlement command as a separately authorized action. Preserve one source of accounting truth per rail and reconcile rail-specific events into governed projections.

## MSM-005 cull and pool integration

Record each cull decision in the paper journal, including score/evidence snapshot and explicit reservation dispositions. Route donations to the consolidation pool. Allocate pool balances through versioned, idempotent distribution events. Keep performance scores, eligibility decisions, paper balances, and testnet balances as separate domains.

## Acceptance

- Unit tests cover manifest identity, isolated chain/key namespaces, signer-reference handling, caps, approval roles, and fail-closed unknown fields.
- Testnet provisioning adapters require a passing receipt bound to the exact manifest digest plus a separate owner authorization.
- Production promotion requires fresh testnet reconciliation, dual control, custody/legal evidence, and rollback readiness.
