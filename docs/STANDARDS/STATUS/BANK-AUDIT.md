# Bank Naming Audit

Generated: 2026-10-02

## Convention (from BANK-NAMING.md)

    <project>::<method>::<vendor>::<family>::<model>::<settings>::<role>::<comp>

Primary bank exception:  <project>::primary

## State matrix

Read from `memory_units` grouped by `bank_id`, classified by convention state.
Refresh by running `hs-facts count`.

| bank_id | convention | action |
|---------|-----------|--------|
| termux-monorepo::primary | OK-primary | keep, active writer (agent_hindsight) |
| termux-monorepo::mvt::google::gemini::base | OK-mvt | keep, legacy MVT lane |
| termux-monorepo::mvt::google::gemini::gemini-3.5-flash-lite::standard::producer::base | OK-mvt | keep, current lane |
| deepagent::termux-monorepo | STALE-v1 | rename to termux-monorepo::primary OR delete if empty |

## Investigation log

Run `hs-bank-audit` (planned) to refresh this table with:
- last_write_at
- distinct origins
- writer identification (grep + /proc/<api>/environ)

## Rename rules

Before renaming any bank:
1. Identify writer via grep + /proc environ
2. Note last_write_at — if within 5 min, PAUSE first
3. If writer is env-driven (HINDSIGHT_BANK_ID), rename the env first
4. If writer is literal in a script, patch the script
5. Re-run audit to confirm no writes to old name
6. THEN update PG via FK-drop transaction
