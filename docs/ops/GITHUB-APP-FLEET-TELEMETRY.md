# GitHub App fleet telemetry

Status: the existing live Collector census remains weekly (Monday 06:17 UTC) and uploads a 30-day artifact. The six-hour cadence and immutable repository publication described here are proposed changes on the adaptive telemetry work branch; they are not active until the workflow and publisher implementation are merged and verified.

## Current collection contract

- `ops/github-apps/registry.json` inventories app identities without secret values; each app manifest is the declared-permission source of truth.
- `scripts/github/github_app_telemetry.py` emits declarations plus a sanitized G4 runtime receipt for the explicitly named app.
- Every live census mints a fresh short-lived Collector installation token using `TERMUX_FLEET_COLLECTOR_APP_ID` and `TERMUX_FLEET_COLLECTOR_PRIVATE_KEY`; client ID is verified as a configured input but the mint action uses App ID.
- G4 receipts contain mint outcome, rate-limit before/after, API calls by HTTP status, repositories inspected, workflow run ID/attempt/SHA, duration, conclusion, and timestamp. Unknown fields are rejected; authorization material is never serialized.
- Collector remains read-only. Publisher is a separate principal and its credentials are not reused. Reviewer-ops, Gate/CI, and Lifecycle remain conference-draft/not-provisioned.
- Missing or partial API responses fail closed; no incomplete repository scope is represented as observed.
- Current artifacts are retained for 30 days and runtime data is not committed to the repository.

## Proposed adaptive publication design

- Raise observation opportunities to every six hours (UTC), subject to rate-limit-aware backoff.
- Publish a unique immutable record keyed by UTC date, workflow run ID, and attempt; never overwrite historical observations.
- Keep the Collector installation token read-only. Use a separate, job-scoped workflow token for repository publication, and grant `contents: write` only to the census job.
- Retain a workflow artifact as a secondary copy. Sanitize all published data and never serialize credentials or installation tokens.
- Record an adaptive cadence recommendation from measured rate-limit headroom and recent collection outcomes. A fixed GitHub cron does not dynamically reschedule itself; true adaptive scheduling needs a persisted due-time gate or a separately tested scheduler/controller.
- Failed or incomplete probes must not be represented as successful G4 receipts. Failure publication requires a separately defined failure-receipt contract.

TEL-03 implementation is present for the weekly workflow; its first accepted live receipt remains operational acceptance. TEL-04 effective permission readback, TEL-05 negative-path integration tests, TEL-06 first accepted runtime receipt, downstream MAINT-02 quota-feed integration, and G1–G5 migration shadows remain distinct gates.
