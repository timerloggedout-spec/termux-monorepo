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
- The derivation treats quota-backed ledger reads as UNAVAILABLE and defers
  those arms on `quota_unknown`. Daily-pool/no-provider-quota arms defer
  on `pool_unknown` until a fresh shared-pool record exists.
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
  "pools": {
    "daily-free-inference": {
      "status": "available",
      "observed_at": "2026-11-12T15:29:00Z",
      "reset_window": "daily",
      "reset_tz": "UTC",
      "source_ref": "https://provider.example/terms/free-pool",
      "experiment_label": "QUE-5454"
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
  (`snapshot_stale`); quota-backed arms defer on `quota_unknown` and
  daily-pool/no-provider-quota arms defer on `pool_unknown`.
- `arms[arm_id][YYYY-MM-DD].draws` and `budgets[arm_id]` are required for
  provider-quota-backed arms. An arm absent from `arms` is `quota_unknown`,
  Treat the missing arm record as unknown; do not synthesize zero draws.
- `pools[pool_id]` is required for `daily_pool_no_provider_quota` arms and
  carries `status`, `observed_at`, `reset_window`, `reset_tz`, `source_ref`,
  and `experiment_label`. These arms do not require provider-specific
  `arms[arm_id]` draws or `budgets[arm_id]` numeric headroom.
- Reset fields are REQUIRED for either quota class. The values are the
  ledger's observed resets, never calendar-inferred (QUOTA-RESET-CONTRACT).
- `coverage.complete` — whether the fleet-draw coverage stamp is
  complete (QDesk #5152 c.6825931792: unstamped coverage means the
  Gemini-class pre-flight cannot fire). `last_quota_terminal` is the
  last quota-terminal event timestamp, or null.

## Consumption

- The derivation reads the snapshot only when the file exists at
  `ops/que/feeds/ledger-snapshot.json` (the dispatch-executor workflow
  passes it conditionally). It never writes to the ledger, never
  invents draws, and never falls back to lane-local counts.
- The derivation re-emits snapshot arms/coverage/budgets/pools and derived
  `pool_eligibility` into the executor's `--usage` record (`pool-usage.json`).
  The executor also requires the fresh `pool-cadence/v1` feed via `--cadence`;
  only arms in `pool.eligible` can dispatch. Stamps carry references, not
  copies, of ledger evidence.
- GitHub-independence held: the ledger leg stays local (owner
  constraint); the repo side reads published snapshots only.


## Daily pool with no provider quota counter

A provider can have no provider-specific quota counter and still be eligible through an explicitly governed shared daily pool. This is a distinct quota class, not a conversion of an absent numeric limit into unlimited capacity.

An arm opts into this path only when its build-arm budget contains:

- `quota_class: daily_pool_no_provider_quota`
- `pool_id` and `focus`, matching a pool/focus allocation in `ops/quota/allocations.json`
- a non-empty `experiment_label`
- `quota_evidence_ref` and the normal `quota_metric_source` registry reference

The matching `ops/quota/registry.json` service record must explicitly carry the same `quota_class`. A null `limit`, missing live endpoint, or `unmetered / unknown` prose is NOT sufficient to assign this class.

For this class, `pools[pool_id]` is required and must contain a fresh `status: available` observation, `observed_at`, explicit `reset_window` and `reset_tz`, `source_ref`, and the same `experiment_label`. `status: exhausted` defers as `pool_exhausted`; missing/stale evidence defers as `pool_unknown` / `pool_stale`. A `leftover-only` focus allocation requires `leftover_available: true` in the pool observation.

Provider-specific `arms[arm_id]` draws and `budgets[arm_id]` numeric headroom are not required for this class. The shared pool observation is the admission authority; the executor stamps `provider_quota_class`, `pool_id`, experiment label, and pool evidence. Provider-quota-backed arms retain the existing per-arm headroom gate unchanged.

The cadence feed re-emits `pools` and per-arm `pool_eligibility` in its usage record. No provider is automatically assigned this class from missing quota data; the registry and build-arm record must explicitly establish it.