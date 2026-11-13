# MSM-005 paper accounting contract v1 + cull/pool event extension v2

Implements: MSM-005.A, MSM-005.B, MSM-005.C, MSM-005.D, MSM-005.E, MSM-024. Tracking: #1521, #1526–#1529, #5345. This is the implementation contract on top of the unmerged #1470 foundation, not evidence of merge or deployment.

## One market authority

`MarketGraph` owns cards, observational bets, and the opt-in paper account/reservation lifecycle. Its optional `event_path` is a **single local append-only market event stream**, including cards and bets. `accounting.py` is its persistence helper, not another market or the MSM-002 performance ledger. With no event path, accounting is explicitly ephemeral. Existing observational APIs and the `observational_until_promote` policy remain unchanged.

The sole asset is `paper_point`: integral, nonredeemable paper points, scale zero. Positive amounts must be integers (not booleans), at most `2**63 - 1`. Account balances cannot overflow that bound. Opening an account issues no points. Every issuance requires explicit provenance. There is no implicit faucet, provider entitlement, quota consumption, currency, payout multiplier, fee, burn, redemption, signing, chain, testnet, or payment support.

## Events and identities

Versioned events have a strictly ordered sequence, stable event ID/idempotency key, type, and canonical payload. Creation time is captured once; retries compare intent rather than a newly generated timestamp. Event IDs are unique across the market stream. Account owners are nonempty explicit local actor identities; this local trusted-process API is not remote user authentication or a multi-tenant authorization service.

Cards retain existing MSM-005 card IDs. Paper bets retain their MSM-005 entry IDs and actor classes (`itself`, `others`, `job`); reservation IDs uniquely identify holds and prevent duplicate holds for the same operation. Offers link an existing card, its owner, the payer, and an explicit recipient; offering a card alone cannot move points or transfer ownership. The API validates account ownership and market linkage, not model/provider availability.

The supported lifecycle is explicit account opening, attributed issuance, reservation, then exactly one settlement or release. Settlement debits the held amount from its owner and credits an existing recipient account by exactly that amount. It does not transfer card ownership, score a model, choose a winner, or update routing. Cancel, expiry, void, rejection, tie, and unresolved outcomes are explicit release reasons. There is no wall-clock auto-settlement or inferred timeout. Corrections never rewrite history: an active hold may be void-released, and a settled event is final under v1; post-settlement compensating adjustments are not supported.


## Participant culling and consolidation pools — event schema v2

Culling is one atomic event in the existing market journal. Record the participant, stable decision ID, reason, final score snapshot, SHA-256 evidence digest, capture timestamp, target pool, available-balance disposition, and an explicit disposition for every active reservation.

- `available_disposition` is `retain` or `donate`. Donation transfers the participant's available balance into the named `pool:<pool_id>` account.
- Every active reservation appears exactly once in `reservation_dispositions`. `refund` releases the hold to the participant; `donate` forfeits the held amount into the pool.
- A cull event closes the participant account to new issuance, reservations, cards, bets, and settlement receipts. Preserve the final score/evidence snapshot and the complete decision in the event payload. Mark the participant's remaining open observational bets as culled while preserving their original journal events.
- When a culled participant is the recipient of another participant's active card offer, refund that hold to its payer. Apply donation only to reservations owned by the culled participant.
- The cull transition updates every affected reservation and linked bet in one journal event. Any missing, duplicate, foreign, or already-terminal reservation aborts the complete transition before append.
- Pool distributions name a stable distribution ID, reason, and explicit recipient/units allocations. Require unique active recipients, bounded integer units, sufficient pool balance, and recipient balance headroom.
- Distribution events debit the pool and credit recipients atomically. Preserve undistributed remainder in the pool for later governed rounds.
- Version 2 events extend the v1 event envelope. Replay accepts v1 market/account events and v2 `cull` / `pool_distribute` events; event type/version mismatches fail closed.
- Every mutation uses the same event ID on retries. Decision IDs and distribution IDs are unique within their respective lifecycle. CSV remains a deterministic projection of the single journal.

The score snapshot is evidence metadata; it does not itself authorize culling or determine allocation weights. A human-governed decision supplies the reason, dispositions, pool, and distribution schedule. Keep scoring/reputation, participant eligibility, and accounting balances as distinct domains.

### Culling and pool CLI

```bash
python3 -m scripts.model_selection_market.cli paper --events /tmp/msm.jsonl cull \
  --participant alice --decision-id season-1-cull-alice --reason cohort_expiry \
  --score 0.42 --evidence-digest <sha256> --pool-id season-1 \
  --available-disposition donate \
  --reservation-dispositions '[{"reservation_id":"hold-1","disposition":"refund"},{"reservation_id":"hold-2","disposition":"donate"}]' \
  --event-id cull-alice

python3 -m scripts.model_selection_market.cli paper --events /tmp/msm.jsonl distribute-pool \
  --pool-id season-1 --distribution-id season-1-awards --reason cohort_awards \
  --allocations '[{"recipient":"bob","units":25},{"recipient":"carol","units":15}]' \
  --event-id season-1-awards
```

Use `retain` plus `refund` dispositions to return value to participants; use `donate` only under the recorded pool policy.


## Invariants and retries

For every accepted event prefix:

- `balance = issued + settlement credits - settlement debits`.
- `reserved = sum(active reservation amounts)`.
- `available = balance - reserved`.
- `0 <= reserved <= balance <= 2**63 - 1`.
- Total balances equal total explicit issuance; reserve/release conserve each balance and settlement conserves the total.

Exact retries of an event ID return its original effect, including after restart or an ambiguous append acknowledgement. Reusing the ID for different intent fails closed. A second terminal event, reserve against insufficient available points, duplicate linked operation, unknown owner, invalid amount, or unsupported asset/version must not append anything. A caller reconciles an uncertain write by reopening/replaying and retrying the **same** event ID, never by inventing a new ID.

## Local persistence and crash recovery

A local POSIX filesystem with working advisory file locks, append, `fsync`, and atomic rename is required (Linux and Termux). All participating writers use the market API and its lock. Shared/network filesystems with unproven locking, external file edits, and hostile processes are unsupported. Mutations reload under the exclusive lock, validate the complete transition, append a complete framed event and `fsync`, then rebuild state. Snapshots reload under that lock. There is no independent balance database or authoritative cache.

Restart deterministically replays the stream. Corruption, invalid transitions, missing ordering, unsupported versions, and incomplete trailing writes fail closed; they are not silently discarded or repaired. An operator must preserve and investigate a corrupt stream rather than minting replacement events. An append that completed durably before the caller crashed is found by its stable event ID on retry. CSV generation is outside the accounting transaction and can always be retried from durable state.

## Disposable MSM-012 views

MSM-012 CSV v2 preserves the v1 column prefix and observational stake/card/offer rows, then adds a JSON event_payload column so cull decisions, reservation dispositions, and pool allocations remain inspectable. Account/reservation/event rows expose derived balance, reserved, available, event count/digest, and market references. The parser accepts CSV v2, prior CSV v1, and the legacy column prefix. Formula-sensitive strings are escaped. CSV validation and optional comparison against a fresh event-stream projection detect corrupt/stale views. Exports validate fully before atomic replacement and refuse to overwrite their source stream or lock.

CSV editing, viewing, or reading never imports issuance or settlement into the market. JSON snapshot export remains compatible but does not prove freshness; authoritative rebuild uses the event stream. A source digest identifies the complete event prefix. The CSV is not a cryptographically authenticated document and the digest is not a signature.

## Validation boundary

Synthetic offline tests cover self/peer/job bets, card-linked offers, zero-funded opening, issuance provenance, reserve/settle/release, atomic cull, counterparty refunds, forfeiture, pool distribution, idempotency, CSV v1/v2 parity, wallet promotion gates, invalid amounts, exact/conflicting retries, conservation, process contention, restart, and corrupt tails. Existing market, CSV, performance-ledger and selection regressions remain in the focused run. Required repository gates and exact candidate SHA/test evidence belong in the implementation PR. Local Linux results are not native Android execution, a merged feature, or a deployed service.

## Reproducible wire rules and linkage (technical review resolution)

An event is one UTF-8 JSON object followed by a mandatory newline, serialized with Python-compatible `json.dumps(sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)`. The sequence starts at one and increases by exactly one under the writer lock; booleans are not valid versions or sequences. Event time is an ISO-8601 UTC string captured at initial acceptance. Correlation identifies the reservation for lifecycle events, otherwise the event ID. The `source_digest` is SHA-256 over the concatenation of canonical complete event objects, each followed by a newline, including their version, sequence, metadata, and payload. It identifies a prefix, not an independently authenticated claim. Replay rejects unrecognized events/fields and invalid transition payloads. History is never mutated when reservations become terminal.

A bet operation key is the ordered pair `(actor_id, entry_id)`; the legacy `entry_id` alone omits the actor and is insufficient for accounting uniqueness. Different actors may observe the same subject/prediction. V1 permits exactly one paper reservation per actor/entry pair over its lifetime, including after release. Reservation and bet actor, integer stake, entry reference, asset, and status must agree. Existing observational bets are not silently converted into paper-funded bets. Bet settlement names an existing account explicitly; deciding the outcome and choosing that recipient is the trusted local caller's responsibility, not an inferred prediction oracle.

An offer operation key is `(card_id, payer, to_owner)`, with one paper reservation over that operation's lifetime in v1. `to_owner` must own the referenced existing card and settlement can credit only that stored recipient. A new counterparty or distinct card is a different operation; reopening or repricing a closed identical offer is unsupported in v1. Point settlement does not transfer the card. Card ownership is not editable through CSV.

A failed/partial write is not acknowledged as success. A complete event whose acknowledgement was lost is recovered through its event ID. A non-newline-terminated tail or otherwise invalid JSON/order/schema blocks all further accounting and projection from that stream; manual forensic repair is explicitly outside this implementation. New stream creation also requires directory durability. The API cannot distinguish malicious but syntactically valid edits by a process with filesystem write access: trusted local access remains an explicit assumption.

CSV v2 structural validation requires JSON-object event_payload records; v1 and legacy-prefix readers remain supported. CSV structural validation rejects unknown versions/record types, missing headers/required fields, duplicate account/reservation identities, non-integer account amounts, inconsistent `balance - reserved != available`, and mismatched per-row source digest/count. When `view --events` is supplied, the entire CSV must equal a fresh canonical projection of that locked/replayed event prefix; changed rows, missing rows, stale digest/count, reordered rows, or edited amounts fail closed. Without `--events`, viewing validates structure but cannot establish freshness or authenticity and never authorizes an accounting operation. Exporting a JSON snapshot similarly validates the supplied snapshot, not its provenance. A generated projection can become stale immediately after another valid writer appends; that is detected on its next checked view, not prevented by making CSV authoritative.

Independent technical contract review identified linkage/cardinality, append framing, canonical digest, and CSV validation ambiguities; the rules above resolve them before final runtime acceptance. This is an item-scoped implementation review, not owner consensus or an assertion that #1526–#1529 are closed.

## Run locally (synthetic paper points only)

Use the existing unified CLI; every mutation names a stable event ID. Keep the event stream somewhere private outside Git. These commands do not invoke any provider:

```bash
python3 -m scripts.model_selection_market.cli paper --events /tmp/msm-market.jsonl open --owner alice --event-id open-alice --issuer fixture --source synthetic --reference demo
python3 -m scripts.model_selection_market.cli paper --events /tmp/msm-market.jsonl open --owner bob --event-id open-bob --issuer fixture --source synthetic --reference demo
python3 -m scripts.model_selection_market.cli paper --events /tmp/msm-market.jsonl issue --owner alice --units 100 --event-id issue-alice --issuer fixture --source synthetic --reference demo
python3 -m scripts.model_selection_market.cli paper --events /tmp/msm-market.jsonl reserve-bet --owner alice --actor-class job --subject-kind job --subject-id offline-fixture --units 25 --reservation-id hold-1 --event-id reserve-1
python3 -m scripts.model_selection_market.cli paper --events /tmp/msm-market.jsonl settle --reservation-id hold-1 --recipient bob --event-id settle-1
python3 -m scripts.model_selection_market.paper_wallet export-events /tmp/msm-market.jsonl /tmp/msm-paper.csv
python3 -m scripts.model_selection_market.paper_wallet view /tmp/msm-paper.csv --events /tmp/msm-market.jsonl
```

`paper status` displays the replayed market; `paper card` registers a card, and `reserve-offer` holds points against that card's owner without transferring it. `paper release --reason cancelled|expired|void|rejected|unresolved|tie` records an explicit release. A repeated command must reuse the same event ID and identical arguments. This is a trusted local simulation interface, not a custodial wallet, authenticated service, economic market, or source of redeemable value.
