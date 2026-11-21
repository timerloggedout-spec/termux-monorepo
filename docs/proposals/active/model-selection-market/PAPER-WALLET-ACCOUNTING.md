# Paper Wallet Accounting Extension (MSM-005)

**Status: Proposed — not implemented.** This document specifies an extension to the existing MSM-005 market lane. It does not claim that balances, reservations, or settlement currently exist. The current MSM-005 implementation is a cards/bets/graph stub; the MSM-012 paper CSV is a read-only projection of that market data, not a wallet or accounting system.

## Goal

Add an opt-in, auditable **paper accounting** capability for the existing MSM-005 wagers, bids, cards, and offers. Extend that lane with one authoritative durable market event stream for paper balances and settlement. The current `MarketGraph` keeps cards, bets and edges in memory and emits a snapshot; it does not already provide a durable accounting log. Persistence, locking and recovery are proposed additions inside MSM-005, not proof of an existing engine or a second market. Derive account state and CSV from that event stream. CSV is a materialized view only: it must never become a second write authority or be edited to change a balance.

The paper account unit is an internal, nonredeemable point (for example, `paper_point`), not dollars, currency, a token, provider quota, or a claim on value. Values are exact integers in a declared smallest unit; no floats, implicit fractional rounding, currency conversion, or negative balances. Use an explicit scale/precision contract (prefer integral points with no fractional scale unless a concrete requirement justifies a versioned smaller unit).

## Existing boundaries and reuse

- **MSM-005 remains the lane** for wagers/bids/cards/offers and its actor classes (`itself`, `others`, `job`). Extend it; do not create a parallel market or duplicate MSM item.
- Bids, self/peer/job wagers, and offers must reference existing MSM-005 identities and records. Paper balances support these existing activities; they do not replace or redefine them.
- **MSM-012 remains a projection**: preserve its existing CSV columns/records and projection semantics. Extend its output additively for paper account/reservation/settlement events and/or computed balances, clearly labeled paper-only. Existing stakes/cards/offers continue to project from MSM-005. The CSV must be reproducible from the authoritative event log and schema/version.
- The separate performance ledger (`MSM-002`) and 3L0/model-success scoring are not the accounting authority. No duplicate scoring ledger, 3L0 score writes, model-selection weight updates, routing-weight changes, or bypass of dual-gate/promotion rules.
- Provider quota reservations describe provider-side capacity/limits and are categorically distinct from paper wallet reservations. Neither can create, consume, or settle the other.
- **No cryptographic wallets, RPC, signer, blockchain, tokens, testnet, payment rails, cash, or real-money support.** Do not import capabilities or assumptions from the read-only wallet-testnet reference into this scope.

## Proposed contract: MSM-005.A — accounting/event contract

Define versioned event records appended to the existing market/event ledger, with stable event ID, schema version, event type, timestamp, actor/account ID, causation/correlation ID, idempotency key, and provenance. Amounts are positive integers where required; event-specific fields must be validated and bounded. Suggested event vocabulary:

- `paper_account_opened`: account ID, owner/actor, unit identifier and contract version.
- `paper_funds_issued`: account, positive integer amount, issuance source/reason, authorized issuer/process, evidence/reference, and explicit nonredeemable paper-only designation. Every credit must have provenance; no unexplained balance creation.
- `paper_reservation_created`: account, amount, linked MSM-005 bet/bid/wager/offer reference, reserve purpose, expiry/timeout policy, and unique reservation ID.
- `paper_reservation_settled`: reservation ID, outcome reference, settlement rule/version, integer debit/credit amounts, and finality status.
- `paper_reservation_released`: reservation ID, reason (cancel, void, timeout, rejection, or other defined release), actor/process and evidence.
- `paper_event_voided` or compensating adjustment: reference to prior event, reason and provenance. Never silently mutate or delete history; specify whether correction is a compensating event or a terminal void before implementation.

The reducer/replay contract must define allowed transitions, terminal states, settlement math, payout/fee policy (default: no fees and no payout multiplier until separately specified), treatment of ties/unknown outcomes, and treatment of duplicate or conflicting settlement attempts. An offer alone is not a transfer. Offers and card trades remain observational unless an explicit MSM-005-linked accounting operation is accepted and reserved.

## Invariants and safety

For each account, at every accepted ledger prefix:

`available = issued + settled credits − settled debits − active reservations`

`reserved = sum(amount of active reservations)`

`available >= 0` and `reserved >= 0` always. Use a consistent definition in schemas and exports; expose both available and reserved so a reservation cannot be mistaken for spendable funds. Do not permit a reservation exceeding currently available funds. A reservation is not a settlement, and settlement/release must close exactly one active reservation. Settlement cannot spend again after a reservation is closed.

- Enforce idempotency for issuance, reserve, settle, release, void, and retry operations. Replaying the same event/request must not duplicate effects. Reuse of an idempotency key with different canonical payload must fail closed.
- Prevent duplicate active reservations for the same wager/operation according to a declared uniqueness key; retries return the original result or a clear conflict, never a second hold.
- Validate ownership/actor authorization and linkage to the existing MSM-005 record; reject unknown accounts, malformed amounts, invalid transitions, unsupported versions, and cross-unit operations.
- Serialize concurrent balance-changing operations with an exclusive lock or a proven atomic append/compare-and-append mechanism. Check and append reservation atomically; a read-then-write race is not acceptable. Document filesystem/process assumptions and fail safely when locking/atomicity cannot be established.
- Define crash/restart behavior: recover by replaying the authoritative append-only ledger; ignore only a demonstrably incomplete trailing write under a specified framing/checksum rule, otherwise report corruption and refuse accounting actions. Rebuild projections deterministically; do not repair by silently inventing events or trusting stale CSV/cache data.
- CSV/export must be formula-injection-safe, deterministic for equivalent event history, versioned, and explicitly marked `paper_only` / nonredeemable. Validate the complete source before replacing output; write via temporary file and atomic rename where supported.

## MSM-005.B — account and lifecycle implementation

Implement the event contract and deterministic state reducer in the existing MSM-005 market/event path. Provide account creation and controlled paper issuance with explicit provenance, balance queries, and reserve → settle or release flows linked to existing bets/bids/wagers/offers. Include void/timeout/cancellation behavior and define whether expiry is evaluated by an explicit release event or deterministic recovery action; never infer settlement from elapsed time alone without a recorded event. No account may spend beyond available points; reserved points are unavailable to other operations.

Keep settlement policy intentionally narrow and configurable only through versioned, validated policy. Ensure paper accounting remains observational and cannot affect model scores, 3L0 labels, routing/admission, provider quotas, paid spend, or dual-gate decisions.

## MSM-005.C — MSM-012 CSV materialized view

Preserve existing MSM-012 projection responsibilities and source records. Add a reproducible projection of the accounting events and reducer-derived available/reserved balances, with fields sufficient to trace account, event, linked market entry, unit, amount, status, provenance, and contract version. Clearly distinguish event rows from derived balance rows. CSV import/edit must never feed the ledger. Maintain compatibility or explicitly version the CSV schema; do not silently reinterpret existing `units` or `unit_kind` stake fields as account funds.

## MSM-005.D — tests and proof

Add deterministic unit and integration tests for the contract, state transitions, CSV projection, and failure behavior. Tests must use temporary local files and synthetic identities only; no network, provider account, chain, signer, testnet, or payment access.

### Acceptance tests

1. Opening an account creates no funds; a funded account requires a valid, attributable issuance event.
2. Amounts reject booleans, floats, zero/negative values where prohibited, overflow/out-of-range values, malformed numeric strings, and unit mismatches; accepted values round-trip exactly as integers.
3. Reservation succeeds at exactly available balance; a further reservation or overspend fails without writing a partial event. Reserved funds are unavailable to any second wager/accounting operation.
4. Two concurrent attempts competing for the same remaining balance result in at most one valid reservation; demonstrate lock/atomic append behavior, including process-level contention where supported.
5. Identical idempotent retries yield one effect; conflicting payload reuse fails. Duplicate active reserve, duplicate settle, settle-after-release, release-after-settle, and duplicate issuance retries do not alter totals twice.
6. Successful reserve → settle debits/credits exactly once under the selected settlement rule. Cancel, void, rejection, timeout, and unresolved/tied outcome paths follow documented policies and close/release reservations correctly; an offer without accepted accounting action moves no funds.
7. Replay after clean restart yields identical account states, event ordering and CSV. Simulated crash/truncated-tail recovery follows the documented rule; corruption or unsupported event version fails closed.
8. CSV is derived only from event data, preserves legacy MSM-012 stake/card/offer projection, labels paper-only/nonredeemable, avoids formula injection, and cannot alter balances when modified or re-imported.
9. Provider quota reservation data does not affect paper balances and paper accounting does not call or mutate quota managers. Performance/3L0 ledgers and routing/model weights remain unchanged by accounting events.
10. No implementation path or test introduces wallet keys, signing, blockchain/RPC, testnet, token issuance, real-money denomination, payment, or cash redemption.

## Milestones

1. **Contract:** agree event schema/versioning, integer unit, issuance authority/provenance, settlement policy, uniqueness keys, crash/locking guarantees, and additive CSV compatibility. Capture decisions in tests/schema before implementation.
2. **Implementation:** extend the existing MSM-005 event/market path and reducer; add account, issuance, reservation, settlement/release, idempotency/concurrency/recovery behavior; extend MSM-012 as a deterministic read-only projection.
3. **Proof:** run focused unit/integration and restart/concurrency/failure tests; verify legacy projection compatibility and no quota, scoring, routing, money, or blockchain effects. Record reproducible commands and evidence before any completion claim.

## Completion and issue mapping

This is a proposal only; no accounting implementation or due date is asserted. The issue mapping below records the requested tracking, not implementation completion. Do not reuse an existing MSM ID, create a duplicate MSM-012, or interpret the existing MSM-005 “done” stub as completion of this new accounting engine. Completion requires verified contract, implementation, and proof evidence for the extension.

## Published tracking

Owning issue: [wallet / #1521](https://github.com/timerloggedout-spec/termux-monorepo/issues/1521). Native subissues: [MSM-005.A / #1526](https://github.com/timerloggedout-spec/termux-monorepo/issues/1526), [MSM-005.B / #1527](https://github.com/timerloggedout-spec/termux-monorepo/issues/1527), [MSM-005.C / #1528](https://github.com/timerloggedout-spec/termux-monorepo/issues/1528), [MSM-005.D / #1529](https://github.com/timerloggedout-spec/termux-monorepo/issues/1529).

[Milestones, Project and dependency map](../termux-agentic-hub/RESEARCH-WALLET-TRACKING.md).
