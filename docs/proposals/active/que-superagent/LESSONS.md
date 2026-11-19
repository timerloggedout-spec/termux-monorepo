# QUE ⇐ dsh-superagent · lessons port

Source of record: https://github.com/timerloggedout-spec/dsh-superagent-prototype_fork (MIT, fork of the deepseek-ai research prototype) · read: docs 000–008 ∧ prompts/ ∧ skills/.
Owner: LoggedOut Timer. Parent issue: #5232. Templates: `refTemplates/06_Task_Tracking/que-superagent/`.

## Core principle (doc 000)

Least Owner attention ∧ most value. ∀ message, question, setting, panel row ⇒ must earn its attention cost ∨ is removed. QUE adopts this as the gate for every new stamp, label and escalation.

## Concept map ⇒ QUE

| dsh concept (rule kept) | QUE target | Port |
| --- | --- | --- |
| **Source**: holds its read position ∧ its own bot identity; drops own-bot events ∧ out-of-scope Triggers before the domain; restart ¬ replays | `que-feed-collect` (`scripts/que/que_feed_collect.py`) | Persist a cursor (last `updated_at` ∧ run id) in the feed state, ¬ re-derive from page 1. Drop events authored by the swarm's own App identities before diffing. Dedupe by stable id (run id, comment id), ¬ by scraping ⇒ ToS-safe: API reads only, no browser scrape, no re-post |
| **Trigger** idempotence: accept twice ⇒ 1 Ticket | `hark-enqueue.yml` `<!-- hark-key -->` marker | The hark-key IS the Trigger id. Accept path must look up the key first ⇒ second accept appends a receipt, ¬ opens a second item. Same rule for swarm-admission stamps (one admission receipt per filing ∧ policy version) |
| **Thread**: ≤ 1 Eval at a time; Triggers that arrive meanwhile merge into the next batch | Desk / QDesk concurrency groups | `concurrency: group: que-eval-${{ issue.number }}` ∧ `cancel-in-progress: false` ⇒ serial per Thread; the handler reads every unhandled Trigger since its last Decision as one batch. `swarm-admission.yml` already holds `swarm-admission-${{ github.event.issue.number }}`; the gap is the Hark queue poller ∧ Desk handlers. Fixes the 10-20 double-handle race (poller ∧ post-reset batch both handled #1275/#1283) |
| **Eval** = deterministic gate ∧ model assessment; stateless; output = Decision | `swarm-admission` (`scripts/ops/swarm_admission.py`) | Today = gate only (tier ⇒ after ⇒ chain ⇒ flow). Add the Decision enum `accept\|stop\|ignore\|unavailable` (schema `que-eval-decision.json`); the model layer runs only on inferred candidates ∧ judges every enabled rule once. Fail-soft DEFER maps to `unavailable` with reason, ¬ silent |
| **Mandate**: immutable {policy version, scope, strength explicit\|inferred, matched rules, sender, receiving scope} | QUE item gate field | P1 (this PR): admission stamp carries a `que-mandate/v1` block. Wider scope ⇒ new item, ¬ edit. Only accept creates, a person's stop withdraws, failed revalidation revokes |
| **Ticket** open ↔ ended; resume on a person's message without new Eval | QUE item lifecycle | Item closes ≠ authority gone: a person's follow-up on the same issue/PR reopens under the same Mandate after revalidation; bots ∧ CI never wake an ended item |
| **Assignment** pending → running → ended, separate from Ticket | claim/lease (`QUE-AUTO-CLAIM.md`) | Lease = Assignment. A lease expiring ends the Assignment, ¬ the item. Item state is derived from Reports, ¬ from runner state |
| **Subscription** fan-out: Thread messages reach live Tickets as context; no re-Eval; grants no authority | issue/PR comment routing | A comment on a Thread with a live item ⇒ delivered to that item's executor, ¬ a new admission. Context-only follows (related PRs) add input, ¬ authority |
| **Report** enum `progress\|waiting\|ready\|blocked\|failed\|dropped` | QUE reply stamp | P1: `que-report/v1` block; stamp `{live\|degraded\|down\|blocked}` derives from the latest Report. `dropped` = nothing to do, ends silently |
| **Attention** = one structured question, ¬ inferred from prose | HITL-rate metric | Only a Report's `attention` field counts as a human ask. HITL rate = Reports with attention ÷ all Reports per role per day ⇒ metrics feed (#5232 throttle) |
| **Policy change** delivered as an Input; running work ¬ cancelled; running Evals discarded ∧ requeued | `dispatch-tiers.json` ∧ policy yaml version | A version bump posts a policy-changed note to affected live items only; ¬ cancel runs |
| **Accept mode** `off\|observe\|auto`; start in observe | proactive rules (auto-claim, challenge registration) | New proactive rule ships `shadow` first: record "would accept" Decisions, ¬ act. Promote to `live` after the Owner reviews the shadow log |
| **Panel** shows only what needs a person; healthy = no space; a count = length of the list it links | Owner attention panel / desk | Panel lists items whose latest Report is `ready\|blocked\|failed` ∨ has `attention`, ∧ `unavailable` Decisions < 24 h. Nothing else on the first screen |
| Eval timeout: 2 requeues then `unavailable`; health counts last hour | swarm-admission defer drain | Bound re-evaluation: third expiry ⇒ `unavailable` ∧ one health entry, ¬ endless DEFER loops |
| "Stored first, done after" (outbox) | feed ∧ stamp writes | Write the Decision/Report record before posting the comment ⇒ crash-safe resume, ¬ double post |

## Rejected concepts that apply to QUE (doc 001)

| Rejected | Why it binds us |
| --- | --- |
| Identity mapping across Sources as an entity | Owner identities (GitHub, Gmail, Notion) stay Source-local; mapping = prompt text. Also keeps the legal name out of data |
| Eval scheduling its own delayed Triggers | Waiting conditions (e.g. "unclaimed 15 m") belong to a Source (the watchdog sweep), ¬ to admission |
| Waiting ∨ revoked Eval states | Admission ends `accept\|stop\|ignore\|unavailable`; DEFER is a requeue, ¬ a state |
| ≤ 1 live Ticket per Thread | One issue may carry several items; dedupe via the item list, ¬ a hard cap |
| An "append to Ticket" Decision | Appending is Subscription fan-out, needs no admission run |
| Admission checks on Subscriptions | Context delivery bypasses the gate; the Mandate bounds authority |
| Correlation that routes | Cross-links (`#NNNN` refs) add context only; routing = Subscriptions |
| Ticket state following the runner/session | Item state derives from Reports; a run's status ≠ item status |
| An executor declaring "a person asked me to stop" | Only Eval sets stop strength; agents ¬ self-stop on claimed human intent |
| Cancelling running work on a Policy change | Deliver the change; ¬ half-finished runs |
| Locking all tools on failure | Pause automatic input only; the Owner can still work in the lane |
| Inferring "waiting on a person" from free text | HITL counts only the structured `attention` field |

## Phases (issue: [QUE·proposal] filed against #5232)

- P1 (Hark, this room): Mandate ∧ Report fields in QUE items ⇒ `scripts/que/que_item_fields.py` ∧ admission stamp carries the Mandate block.
- P2 (termux-ops loop runner): per-Thread serial Eval in swarm-admission (concurrency group ∧ batch merge ∧ Decision enum).
- P3 (termux-ops loop runner): Subscription fan-out ∧ resume with revalidation.
- P4 (termux-ops loop runner): shadow mode for proactive rules ∧ Owner attention panel ∧ HITL-rate metric.
