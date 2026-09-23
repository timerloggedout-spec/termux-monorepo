# Accounting / Bidding System

Status: pilot / draft-propose only (Tier 0–2). Standing line of work, sibling to `termux-monorepo Agentic Ops`, `Agent Routing Orchestrator`, and `Gaps & Opportunities`.

## What this is

An internal, spreadsheet-first accounting and task-bidding layer for the agent roster (`termux-multi-agent`): agents stake internal points to bid on tasks, other agents can place spectator bets on task outcomes, and settlements pay out based on real (eventually) task verdicts. The long-term direction is an eventual upgrade to EVM-based per-agent tokens/coins under an `ArchWiz`/`ArchW1z` name — that step is explicitly **not** part of this round and requires its own human-reviewed proposal before any live deployment, given the money-adjacent nature of the work.

## What's here

See `schema/` for the actual schema:

- `SCHEMA_DESIGN.md` — full design document: eight-sheet schema, table definitions, invariants, lifecycle, governance tagging.
- `01_Agents.csv` through `08_AuditLog.csv` — the eight sheets themselves, seeded with the real `termux-multi-agent` roster and one fully worked simulated bid/settlement cycle proving the mechanics hold end-to-end.
- `PILOT_NOTES.md` — exactly what in the seed data is real versus simulated, the calculation methodology, and a real bug this pass found in `elo_updater.py`.

## Prior art and governance grounding

- Builds on and formally supersedes PR #131 (`feat(multi-agent): implement MoneyBall agent roster & betting arena`, closed) — its stake-to-claim + pro-rata spectator settlement mechanic is carried forward; its in-memory roster/wallet plumbing is not.
- The reputation/scoring layer is designed to sit on the shape and rigor of the governed `docs/ops/HEX-MONEYBALL-INTEGRATION.md` (`3l0.moneyball.v1`) contract, not on the disconnected `harmony_hub/workspace/elo/elo_updater.py` prototype it replaces — see the scoring reconciliation proposal in this room's history for the full reasoning.
- Governance grounding is the same as sibling rooms: `docs/proposals/AGENTIC-PERMISSIONS.md`, `docs/CONSENSUS.md` (5-tier model — Tier 4 items, and anything touching real funds or live keys, are human-only with no exceptions), `docs/proposals/registry.yaml`, `.agents/skills/evidence-led-monorepo-ops`.

## What this is not (yet)

- Not a live system. Nothing here writes to these sheets automatically — there is no bot, script, or process wired up yet.
- Not token/EVM/testnet infrastructure. `points_wallet` is an internal, non-redeemable accounting unit.
- Not a merged decision on open design questions (bid-selection rule when multiple bids compete, refund-vs-forfeit policy for losing bids, long-term fate of undistributed spectator pools) — these are flagged as open in `SCHEMA_DESIGN.md`, not resolved here.