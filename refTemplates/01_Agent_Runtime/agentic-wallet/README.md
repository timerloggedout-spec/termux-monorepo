# Agentic Wallet — template spec (fleet-native)

A reusable template for giving a lane/agent a **paper/test
agentic wallet** on the fleet's established in-house wallet
layer: per-agent spin-up, a required per-task ante, optional
wagering modules, spend controls, and sweep triggers — all as
events on the hash-chained wallet-ledger of record. The full
parameterization is `SPEC.md` in this directory.

**Family placement: `01_Agent_Runtime`.** The template
parameterizes an agent-runtime capability — a wallet is
provisioned as part of an agent's runtime spin-up and its
controls bind at runtime. It is fleet-native, authored from
the fleet's own MoneyBall design record.

**Instantiation in one line:** pick the target lane/agent →
its spin-up appends a provisioning event to the wallet-ledger
of record → declare the control parameters as stamped
snapshots → enable the optional modules the work needs. The
genesis rule is cited in the spec, never re-derived.

**External comparator registration — MergeEarn:** the owner
reports prior use of MergeEarn in wallet-template design.
MergeEarn is registered here as an external bounty/work-funding
and payout-flow comparator:
https://github.com/Saidur-droid/MergeEarn
The referenced upstream PR #76 is a product/contribution
interaction record, not proof of code adoption or settlement
correctness. The fleet wallet ledger remains the sole source
of record for fleet wallet balances and events.

**Hard exclusions (stamped, not optional):** ∅ chain/mainnet
legs · ∅ key custody · real money is a separate owner gate —
Solana/mainnet legs stay behind the chain-wiring + key-custody
rulings. Paper/test rails only; the unit of account is
`soft_quota_token` (observational).

Sources: see `SOURCE.txt` for the internal ledger/spec lineage
and the registered MergeEarn comparator.
