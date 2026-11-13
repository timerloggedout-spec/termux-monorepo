# Ledger Snapshot Contract — `ledger-snapshot/v1`

QUE #5160 / #5152. The published-snapshot input contract for the
autoQuotaCadence derivation (`scripts/ops/auto_quota_cadence.py`).
Owned by Cadence (#5152 / #5113 T2); this file names the slots T2 must
fill — it does not fill them.

## Status: UNPUBLISHED

The #5152 ledger read contract {store, fields, freshness} is
UNPUBLISHED until #5113 T2 publishes it (Cadence review c.6802642639
gap 1; QDesk addendum c.6802661589). Until then:

- No `ops/que/feeds/ledger-snapshot.json` exists in the repo.
- The derivation treats ledger reads as UNAVAILABLE and defers every
  arm on `quota_unknown`.
- NOTHING in Actions meters, polls, or re-derives draws. The snapshot
  is the ledger's published output, consumed read-only.

## Shape (what T2 publishes)

```json
{
  "schema": "ledger-snapshot/v1",
  "generated_at": "2026-11-12T15:30:00Z",
  "arms": {
    "gemini-cli": {
      "2026-11-12": {"draws": 3}
    }
  },
  "budgets": {
    "gemini-cli": {
      "daily_total": 20,
      "spendable_primary": 16,
      "reserved_escalation": 4,
      "reset_window": "midnight PT",
      "reset_tz": "America/Los_Angeles"
    }
  },
  "coverage": {
    "complete": true,
    "stamped_at": "2026-11-12T15:30:00Z",
    "last_quota_terminal": "2026-11-11T13:02:46Z"
  }
}
```

Field rules:

- `schema` MUST be exactly `ledger-snapshot/v1` (the derivation rejects
  anything else with exit 2).
- `generated_at` is the snapshot's publication time. Freshness bound:
  **3600 seconds** — an older snapshot is treated as absent
  (`snapshot_stale`) and every arm defers on `quota_unknown`.
- `arms[arm_id][YYYY-MM-DD].draws` — recorded draws for that arm-day.
  An arm absent from `arms` is `quota_unknown`, never zero.
- `budgets[arm_id]` — the arm's budget record. `reset_window` and
  `reset_tz` are REQUIRED for eligibility (gap 2): a budget without
  them leaves the arm deferred on `reset_window_unknown` /
  `reset_tz_unknown`. The values are the ledger's observed resets, never
  calendar-inferred (QUOTA-RESET-CONTRACT).
- `coverage.complete` — whether the fleet-draw coverage stamp is
  complete (QDesk #5152 c.6825931792: unstamped coverage means the
  Gemini-class pre-flight cannot fire). `last_quota_terminal` is the
  last quota-terminal event timestamp, or null.

## Consumption

- The derivation reads the snapshot only when the file exists at
  `ops/que/feeds/ledger-snapshot.json` (the dispatch-executor workflow
  passes it conditionally). It never writes to the ledger, never
  invents draws, and never falls back to lane-local counts.
- The derivation re-emits the snapshot's arms/coverage/budgets verbatim
  into the executor's `--usage` record (`pool-usage.json`); the
  executor's quota gate and pre-flight read from that record. Stamps
  carry references, not copies, of ledger evidence.
- GitHub-independence held: the ledger leg stays local (owner
  constraint); the repo side reads published snapshots only.
