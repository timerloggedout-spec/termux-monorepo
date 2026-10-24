# Spreadsheet-First Accounting/Bidding Schema — Design Document

Status: proposal / schema draft, not live code, not deployed. Builds directly on two prior decisions in this room: (1) the PR #131 build-vs-supersede analysis (carrying forward its stake-to-claim + pro-rata spectator settlement mechanic, rejecting its in-memory roster/wallet plumbing), and (2) the scoring reconciliation proposal (the ledger is built to the shape/rigor of the governed `3l0.moneyball.v1` contract, with a new additive `agent_reputation_snapshot` dataset replacing `harmony_hub/elo`'s flat deltas). No token/EVM/testnet specifics are included — internal points only, per the standing scope limit.

---

## 1. Why a spreadsheet, and why these eight sheets

"Spreadsheet-first" means the ledger's system of record is a small set of flat, human-readable tables — importable into Google Sheets/Excel today, and migratable to a real database later without a redesign, because each sheet is already shaped like a normalized table (stable IDs, one concern per sheet, foreign keys by ID column) rather than a free-form notebook. Eight sheets, each with one job:

| # | Sheet | Job |
|---|-------|-----|
| 1 | `Agents` | Who exists, their current point balance, active/inactive status |
| 2 | `LedgerEntries` | The append-only accounting spine — every balance change, ever |
| 3 | `Tasks` | The work items agents bid on |
| 4 | `Bids` | Agents staking points to claim a task |
| 5 | `SpectatorBets` | Other agents wagering on a task's outcome |
| 6 | `Settlements` | The resolution event that pays out bids + bets and generates ledger entries |
| 7 | `AgentReputationSnapshot` | The reconciled scoring feed (3l0.moneyball.v1-shaped) that bid/bet sizing and settlement confidence read from |
| 8 | `AuditLog` | Every manual/administrative change, with a named human approver |

Template CSVs for all eight are delivered alongside this document. As of the pilot round, `Agents.csv` is seeded with the **real** `termux-multi-agent` roster (Chronomancer, Linguist, Bidder, Scout, Harvester, Orchestrator — sourced from `harmony_hub/config/AGENT_TOOL_MATRIX.md` and `GRIMOIRE_DICTIONARY.md`) and real starting reputation numbers derived from `termux-multi-agent/run_history.jsonl`'s actual verdict counts, and the other seven sheets carry one fully worked, internally-consistent, end-to-end example cycle (bid → spectator bets → settlement → ledger) built on that real roster, clearly labeled `[SIMULATED]`/`TASK-SIM-*` since no real GitHub Actions run backs its verdict. See `PILOT_NOTES.md` in this directory for what's real, what's simulated, and a real bug this pass found in `elo_updater.py`.

## 2. Table definitions

### 2.1 `Agents` (roster reference table)

| Column | Type | Notes |
|---|---|---|
| `agent_id` | string, PK | Stable identifier. Human-named agents get a readable id (`agent-eng-bolt`); migrated legacy identities keep their original hash-like id from `harmony_hub/elo` so provenance is traceable. |
| `display_name` | string | For humans reading the sheet. |
| `role` | string | Free-text role tag (Engineer, Researcher, Security, etc.) — descriptive only, not an access-control mechanism. |
| `active` | boolean | Inactive agents are excluded from new bids/bets but keep their history. |
| `wallet_balance_current` | number | **Derived, not authoritative** — a cached convenience value. The authoritative balance is always the running sum of that agent's rows in `LedgerEntries`. This column exists so the sheet is readable at a glance; it must be recomputed from `LedgerEntries`, never hand-edited outside of a reconciliation pass (see §4). |
| `created_at` | ISO 8601 timestamp | |
| `source_ref` | string, optional | Link to the PR/issue/proposal that onboarded this agent, if applicable. |
| `notes` | string, optional | |

### 2.2 `LedgerEntries` (the accounting spine)

This is the one sheet that actually defines "how many points does agent X have." Everything else derives from it or writes to it.

| Column | Type | Notes |
|---|---|---|
| `entry_id` | string, PK | Sequential, e.g. `LE-0001`. |
| `timestamp` | ISO 8601 | |
| `agent_id` | string, FK → `Agents.agent_id` | |
| `account` | string | Fixed to `points_wallet` for this phase (a placeholder that lets a second account type be added later without a schema change — e.g. a bonded/escrow account — without implying anything about tokens). |
| `debit` | number ≥ 0 | Amount removed from the agent's balance (a bid stake, a lost bet, a manual deduction). |
| `credit` | number ≥ 0 | Amount added to the agent's balance (a payout, a seed grant, a manual credit). |
| `balance_after` | number | Running balance for that agent after this entry. Must equal the previous entry's `balance_after` for that same `agent_id`, minus `debit`, plus `credit`. This is the core reconciliation invariant (§4.1). |
| `ref_type` | enum | One of `seed_migration`, `bid`, `settlement`, `manual_adjustment`. Extensible, but every new value needs a matching row shape decided here first — no silent new categories. |
| `ref_id` | string | Points to the row in `Bids`/`Settlements`/an audit entry that caused this ledger line. Every entry must have one — an entry with no `ref_id` is not accepted (see §4.2). |
| `memo` | string | Free text, human-readable reason. |

**This sheet is append-only.** No row is ever edited or deleted after being written; corrections happen by adding a new offsetting entry with `ref_type = manual_adjustment` and a `memo` explaining why, cross-referenced from `AuditLog`.

### 2.3 `Tasks`

| Column | Type | Notes |
|---|---|---|
| `task_id` | string, PK | |
| `title`, `description` | string | |
| `source_ref` | string, optional | Link to the originating issue/PR if the task tracks real repo work. |
| `status` | enum | `open` → `bidding` → `assigned` → `resolved` (or `cancelled` at any point before `resolved`). |
| `created_at` | ISO 8601 | |
| `bidding_closes_at` | ISO 8601, optional | When bidding closes and the highest/selected bid is chosen. |
| `assigned_agent_id` | string, FK → `Agents.agent_id`, nullable | Set once a bid wins. |
| `winning_bid_id` | string, FK → `Bids.bid_id`, nullable | |
| `resolved_at` | ISO 8601, nullable | |
| `evidence_run_uid` / `evidence_attempt_uid` | string, nullable | Ties the task's real-world outcome back to a `3l0.moneyball.v1` `run_uid`/`attempt_uid` when the task corresponds to actual CI-tracked agent work — this is what makes settlement auditable against real evidence rather than a self-reported verdict. |
| `notes` | string, optional | |

### 2.4 `Bids`

| Column | Type | Notes |
|---|---|---|
| `bid_id` | string, PK | |
| `task_id` | string, FK → `Tasks.task_id` | |
| `agent_id` | string, FK → `Agents.agent_id` | |
| `stake_amount` | number > 0 | Must not exceed the agent's current ledger-derived balance at time of bid — this is checked against `LedgerEntries`, not the cached `Agents.wallet_balance_current` (§4.3). |
| `placed_at` | ISO 8601 | |
| `status` | enum | `active`, `won`, `lost`, `withdrawn`. |
| `notes` | string, optional | |

Placing a bid immediately writes a `debit` row to `LedgerEntries` (`ref_type=bid`) for the stake — the stake is escrowed the moment the bid is placed, not at settlement. A `withdrawn` bid before task assignment writes an offsetting `credit` refund entry.

### 2.5 `SpectatorBets`

| Column | Type | Notes |
|---|---|---|
| `bet_id` | string, PK | |
| `task_id` | string, FK → `Tasks.task_id` | |
| `spectator_agent_id` | string, FK → `Agents.agent_id` | Any active agent, including ones not bidding on the task itself. |
| `outcome_backed` | enum | `success` or `failure`. |
| `stake_amount` | number > 0 | Escrowed immediately, same as a bid. |
| `placed_at` | ISO 8601 | |
| `status` | enum | `active`, `won`, `lost`, `withdrawn`. |
| `payout_amount` | number, nullable | Filled in at settlement. |
| `settlement_id` | string, FK → `Settlements.settlement_id`, nullable | |

### 2.6 `Settlements`

The resolution event. One row per task resolution; it is the single place that decides the payout math and is the only sheet allowed to trigger new `LedgerEntries` rows besides bid/bet placement itself.

| Column | Type | Notes |
|---|---|---|
| `settlement_id` | string, PK | |
| `task_id` | string, FK → `Tasks.task_id` | |
| `verdict` | enum | `success`, `failure`, or `no_winning_bets` (spectator pool had no backers of the actual outcome — see §4.4 for what happens to that pool). |
| `resolved_at` | ISO 8601 | |
| `winning_bid_id` | string, FK → `Bids.bid_id`, nullable | Null if no one bid (task assigned by another path) or verdict is `no_winning_bets` with no bid involved. |
| `agent_id` | string, FK → `Agents.agent_id`, nullable | The winning bidder, denormalized for readability. |
| `agent_payout` | number | Carried forward from PR #131's mechanic: on `success`, the bidder recovers their stake plus a 1.5x bonus (`stake + stake*1.5`); on `failure`, the stake is forfeit (`0.0`). This multiplier is a starting default, not fixed forever — it is the one deliberately tunable parameter in the whole schema and should be revisited once real settlement volume exists. |
| `spectator_pool_total` | number | Sum of all spectator stakes on this task, both outcomes. |
| `spectator_winning_outcome` | enum, nullable | Which side the pool paid out to. |
| `spectator_payout_total` | number | Should equal `spectator_pool_total` when there is at least one winning bettor (pro-rata full redistribution); `0` when `verdict = no_winning_bets`, in which case the pool's fate is a policy decision, not an automatic action (§4.4). |
| `evidence_ref` | string | The `3l0.moneyball.v1` `run_uid`/`attempt_uid`/`score_uid` this verdict is derived from — a settlement without a traceable evidence reference is a self-reported verdict and should be flagged as lower-confidence (see `attribution_confidence`). |
| `attribution_confidence` | number, [0,1] | Carried directly from the contract's own `attribution_confidence` semantics — how much to trust this verdict as the true outcome. Low-confidence settlements are still binding (this is an internal points system, not a court), but the number is preserved for later audit and for weighting `AgentReputationSnapshot` updates. |
| `notes` | string | |

### 2.7 `AgentReputationSnapshot`

This is the dataset proposed in the scoring reconciliation — the one place bid/bet *decision-making* (which agent looks credible enough to back) reads a rolling reputation number from, replacing `harmony_hub/elo`'s flat deltas.

| Column | Type | Notes |
|---|---|---|
| `snapshot_id` | string, PK | |
| `agent_id` | string, FK → `Agents.agent_id` | |
| `snapshot_at` | ISO 8601 | |
| `contract_version` | string | Pinned to `3l0.moneyball.v1` (or whatever version supersedes it) — never left blank, per the contract's own "contract drift fails closed" gate. |
| `confidence_weighted_score` | number, [0,1] | `SUM(primary_score * attribution_confidence) / SUM(attribution_confidence)` over that agent's attempts in the snapshot window — the contract's own formula, not a new one. |
| `raw_pass_rate` | number, [0,1], nullable | |
| `cost_per_success_usd` | number, nullable | Null (not zero) when there are no successes, per the contract's own rule. |
| `attempts_count` | integer | |
| `mean_attribution_confidence` | number, nullable | Displayed alongside the headline score per the contract's own requirement. |
| `low_confidence_attempts` | integer | |
| `attribution_method` | enum | `contract-native` (computed from real `agent_task_attempt`/`outcome_score` rows) or `legacy-elo-migration` (one-time backfill from `harmony_hub/elo`, per the reconciliation proposal). |
| `source_attempt_uid_range` | string, nullable | Which attempts this snapshot was computed over — the audit trail back to real evidence. |
| `notes` | string | |

`legacy-elo-migration` rows exist exactly once per migrated agent, are clearly flagged, and are expected to be superseded by `contract-native` snapshots as real attempt history accrues for that agent — they are a bridge, not a permanent second scoring method.

### 2.8 `AuditLog`

| Column | Type | Notes |
|---|---|---|
| `audit_id` | string, PK | |
| `timestamp` | ISO 8601 | |
| `actor` | string | Who made the change — an agent id or a human name/handle. |
| `actor_type` | enum | `agent` or `human`. |
| `action` | string | e.g. `create_sheet`, `seed_migration`, `manual_adjustment`, `status_change`. |
| `target_table` / `target_id` | string | Which sheet/row was touched. |
| `field_changed`, `old_value`, `new_value` | string | |
| `reason` | string | Required, free text. |
| `approved_by` | string | For anything touching `LedgerEntries` balances outside the normal bid/settlement flow, this must name a human — an agent cannot self-approve a manual balance adjustment. |
| `tier` | enum | `Tier0`–`Tier2` per `docs/proposals/AGENTIC-PERMISSIONS.md`'s 5-tier model. Nothing in this schema is designed to touch Tier 3/4 territory (credential rotation, force-push, real funds/keys); if a future change would, it stops here and goes to the owner, exactly as the room's governance grounding requires. |

## 3. Lifecycle walkthrough (one full cycle, no code)

1. **Task opens** — a row in `Tasks` with `status=open`, optionally linked to a real issue/PR via `source_ref`.
2. **Bidding opens** — `status → bidding`. Agents place bids (`Bids` rows); each placed bid immediately writes a `debit` `LedgerEntries` row escrowing the stake. Other agents may place `SpectatorBets` on the eventual outcome, each also escrowed immediately.
3. **Bidding closes** — the task's designated selection rule (highest bid, or another policy — deliberately left to the full system design, not fixed here) picks a winner. `Tasks.status → assigned`, `assigned_agent_id` and `winning_bid_id` set. Losing/unselected bids get `status=lost`; their stakes are **not** automatically refunded unless the task-level policy says so (this is a design choice the full spec should make explicitly — recorded here as an open question, not resolved).
4. **Work happens** — outside this schema entirely. The actual PR/task execution proceeds as normal engineering work, producing real CI evidence under `3l0.moneyball.v1` if it's the kind of task that generates that evidence.
5. **Settlement** — once a verdict exists (ideally traceable to a `3l0.moneyball.v1` `attempt_uid`/`outcome_score`), a `Settlements` row is written with the verdict, evidence reference, and confidence. This single row is the trigger for:
   - A `credit` `LedgerEntries` row to the winning bidder (stake + 1.5x bonus on success; nothing on failure — the earlier debit already captured the loss).
   - `credit` `LedgerEntries` rows to each winning spectator bettor, pro-rata by their stake's share of the winning side, drawn from the full pool (both sides' stakes).
   - `SpectatorBets.status`/`payout_amount` updated for every bet on that task.
6. **Reputation update** — separately (and asynchronously — this does not have to happen inside the settlement transaction), an `AgentReputationSnapshot` row is appended for the assigned agent once enough new attempt evidence exists to justify a fresh snapshot, per the reconciliation proposal's refresh-on-completion approach.

## 4. Invariants a real implementation must enforce

### 4.1 Ledger balance continuity
For any `agent_id`, ordering `LedgerEntries` rows by `timestamp`, each row's `balance_after` must equal the prior row's `balance_after` for that agent, minus this row's `debit`, plus this row's `credit`. A break in this chain is a data-integrity failure, not a business event — it should halt processing, not silently continue (mirrors the contract's own "blocking gates" posture).

### 4.2 No entry without a reference
Every `LedgerEntries` row has a non-null `ref_id` pointing to the `Bids`/`Settlements`/`AuditLog` row that caused it. There is no such thing as a floating balance change with no traceable cause — this is the single most important property for a system that is explicitly building toward eventually representing real value.

### 4.3 Bids/bets check the ledger, not the cache
`Agents.wallet_balance_current` is a convenience cache for humans skimming the sheet. Any check of "can this agent afford this bid" must be computed live from `LedgerEntries`, never from the cached column — the cache can lag a manual edit or a batch reconciliation pass.

### 4.4 Undefined pools are a policy decision, not a default
When `Settlements.verdict = no_winning_bets` (nobody backed the actual outcome), PR #131's own code left this case as a comment ("burnt or returned to a general system treasury" — not implemented). This schema keeps that gap **visible rather than silently defaulting it**: `spectator_payout_total = 0` and the pool's fate is left to an explicit `AuditLog` entry with a named human approver, until the full system design picks one durable policy (return pro-rata to bettors, hold in a house/treasury account, etc.).

### 4.5 Migration rows are permanently flagged
`legacy-elo-migration` rows in `AgentReputationSnapshot` and `seed_migration` rows in `LedgerEntries` are never edited to look native after the fact — the provenance flag stays forever, so anyone auditing the ledger years from now can still tell which numbers trace back to the old, unweighted `harmony_hub/elo` prototype versus the governed contract.

## 5. Governance tagging

Every write path in this schema is Tier 0–2 (draft/propose, internal accounting adjustments, no credential/infrastructure/fund actions) per `docs/proposals/AGENTIC-PERMISSIONS.md`. Nothing here creates, moves, or represents real money, tokens, or keys — `points_wallet` is an internal, non-redeemable accounting unit exactly as scoped. Any future step that would change that (the eventual EVM/token/testnet phase named in this room's mission) is explicitly out of this document's scope and, per the room's own charter, requires a dedicated human-reviewed proposal before any live deployment — more conservatively than an ordinary Tier 4 item, given the money-adjacent nature of the eventual direction.

## 6. What this document deliberately does not decide

- The exact bid-selection rule when multiple bids exist (highest stake wins? lowest? a weighted combination with `AgentReputationSnapshot`?) — flagged as an open question in §3, not resolved here.
- Whether losing bids are refunded or forfeited — same status.
- The long-term fate of `no_winning_bets` pools — flagged in §4.4, left to a future explicit policy decision.
- Any interface/tooling for actually writing to these sheets (a script, a bot, a manual process) — this document is the schema, not the implementation plan.
- Anything token/EVM/testnet-related, per the standing scope limit.