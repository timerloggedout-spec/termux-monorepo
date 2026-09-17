# Pilot Notes — Accounting/Bidding Schema Round 1

Status: pilot proof-of-mechanics only. This document says exactly what is real, what is simulated, and what was found along the way, so nothing in the seed data is later mistaken for a live settlement.

## What's real

- **The roster** (`01_Agents.csv`): Chronomancer, Linguist, Bidder, Scout, Harvester, Orchestrator are the six real, documented agent identities of the `termux-multi-agent` system, sourced directly from `harmony_hub/config/AGENT_TOOL_MATRIX.md` (roles, tools, DB access, output destinations) and `harmony_hub/config/GRIMOIRE_DICTIONARY.md` (codenames/archetypes). No fictional or placeholder names were used for the roster itself.
- **The reputation seed numbers** (`07_AgentReputationSnapshot.csv`): computed from actual verdict rows in `termux-multi-agent/run_history.jsonl` — real PASS/FAIL/SUCCESS/UNVERIFIED counts per agent, not invented figures. Chronomancer: 4 PASS / 0 FAIL. Linguist: 11 PASS / 32 FAIL. Orchestrator: 9 PASS + 1 SUCCESS / 6 FAIL / 5 UNVERIFIED. Bidder, Scout, and Harvester have zero rows in `run_history.jsonl` — this is expected, not a gap: their documented output destinations are `elo_ratings.json`, `~/deepseek-cli/test-reports/`, and `~/deepseek_harvest_work/` respectively, not `run_history`. They're seeded at the same default starting ELO (1000) that `elo_updater.py` itself uses for any new `agent_id`.
- **The scoring formula** used to turn those real verdict counts into a starting number is `elo_updater.py`'s own intended rule: start at 1000, `+10` per success, `-15` per failure, `+2` per partial/other — then normalized to a `[0,1]` confidence-weighted-style score via `(elo - 800) / 600`, floored at 0, consistent with the reconciliation proposal's `legacy-elo-migration` treatment. Every row is explicitly flagged `attribution_method = legacy-elo-migration`, exactly as that proposal specifies, because none of this is yet a contract-native `3l0.moneyball.v1` attempt/outcome_score computation.

## A real bug this pass found

While deriving these numbers, I checked `harmony_hub/workspace/elo/elo_updater.py`'s actual comparison logic against the real verdict strings in `run_history.jsonl`. The script does:

```python
if row['verdict'] == 'success':
    score += 10
elif row['verdict'] == 'failure':
    score -= 15
else:
    score += 2
```

But the real verdict values recorded in `run_history.jsonl` are `PASS`, `FAIL`, `SUCCESS`, `UNVERIFIED`, and `REVIEW` — none of which case-sensitively equals the lowercase `'success'` or `'failure'` the script checks for (not even the one row that says `SUCCESS`, because of the case mismatch). As written, **every single real row falls through to the `else: score += 2` branch**, regardless of whether the agent actually passed or failed. The script has been silently treating every historical PASS and every FAIL identically since it was written.

This pilot's seed numbers use the obviously-intended semantic mapping (`PASS`/`SUCCESS` → success, `FAIL` → failure, `REVIEW`/`UNVERIFIED` → partial) rather than reproducing that bug, because reproducing it would mean every agent gets an identical, meaningless score (`1000 + attempts*2`) — not a useful pilot. The bug itself is a separate, concrete finding worth its own small fix in `elo_updater.py` (a case-insensitive or explicit-enum comparison); it is **not** fixed as part of this PR, since this room's scope is the new accounting/bidding schema, not patching the prototype being retired per the reconciliation proposal. Flagging it here so it isn't lost.

## What's simulated

- **`TASK-SIM-001`** and everything that touches it (`BID-SIM-001`, `BET-SIM-001`, `BET-SIM-002`, `SETL-SIM-001`, and `LedgerEntries` rows `LE-0007` through `LE-0011`) is a **hand-run walkthrough**, not a real task or a real CI-verified outcome. It exists solely to prove the schema's mechanics hold together end-to-end:
  - Chronomancer (the roster's strongest real track record) bids 20 points to claim the task and wins it uncontested.
  - Linguist backs "success" with 20 points; Orchestrator backs "failure" with 10 points as a spectator.
  - The simulated verdict is "success" — consistent with, though not derived from, Chronomancer's real historical record.
  - Settlement pays Chronomancer 50 (stake 20 + 1.5x bonus 30, per the mechanic carried forward from PR #131), and pays Linguist the full 30-point spectator pool (sole backer of the winning outcome, so 100% pro-rata share).
  - Every resulting `LedgerEntries` row is traceable to a `ref_id`, and the balance-continuity invariant holds for all three touched agents (verifiable by hand or by summing each agent's debit/credit rows in order).
- `Settlements.attribution_confidence` for `SETL-SIM-001` is deliberately set to `0.0`, and `evidence_ref` is deliberately set to a literal `SIMULATED` string rather than a real `run_uid`/`attempt_uid` — per the schema's own rule that a settlement without traceable evidence must be flagged as the lowest possible confidence, never presented as equivalent to a real, contract-native settlement.

## What this pilot does not claim

- No real task was executed, no real GitHub Actions run backs any part of the simulated cycle, and no real value (points, tokens, or otherwise) actually changed hands anywhere outside this checked-in example data.
- This does not constitute a live accounting system — there is no script, bot, or process that writes to these sheets automatically yet. That's a separate, later implementation step.
- The `elo_updater.py` bug noted above is reported, not fixed, in this PR.