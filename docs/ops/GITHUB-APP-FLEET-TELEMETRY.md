# GitHub App fleet telemetry

Status: six-hour live Collector observation opportunities are configured. Each successful census is retained as a 90-day workflow artifact and published as an immutable, run-addressed repository observation. PR validation remains declaration-only.

## Collection and publication

- `ops/github-apps/registry.json` inventories app identities without secret values; each app manifest is the declared-permission source of truth.
- `scripts/github/github_app_telemetry.py` emits declarations plus a sanitized G4 runtime receipt for the explicitly named app.
- `.github/workflows/github-app-telemetry.yml` offers a census every six hours (UTC), plus manual dispatch on `master`. PR validation never receives app credentials or mints tokens.
- Every live census mints a fresh short-lived Collector installation token using `TERMUX_FLEET_COLLECTOR_APP_ID` and `TERMUX_FLEET_COLLECTOR_PRIVATE_KEY`; client ID is verified as a configured input but the mint action uses App ID.
- G4 receipts contain mint outcome, rate-limit before/after, API calls by HTTP status, repositories inspected, workflow run ID/attempt/SHA, duration, conclusion, and timestamp. Unknown fields are rejected; authorization material is never serialized.
- Every successful run uploads a 90-day artifact and publishes a unique immutable JSON observation under `ops/github-apps/observations/YYYY/MM/DD/`. The publication uses the workflow's narrowly scoped `GITHUB_TOKEN`; the Collector installation token remains read-only and is never used to publish.
- The workflow's repository write permission is limited to the census job; the validation job remains read-only. GITHUB_TOKEN-originated publication commits do not recursively trigger Actions workflows.
- Collector remains read-only. Publisher is a separate principal and its credentials are not reused. Reviewer-ops, Gate/CI, and Lifecycle remain conference-draft/not-provisioned.
- Missing or partial API responses fail closed; no incomplete repository scope is represented as observed.

## Adaptive policy and gates

The six-hour schedule is the maximum observation frequency for this first iteration. The receipt's measured rate-limit headroom is the input to an adaptive cadence recommendation: preserve six-hour checks with healthy headroom, progressively back off as remaining quota falls, and escalate operational review when headroom is critically low. The recommendation is evidence, not a claim that GitHub cron dynamically reschedules itself; the actual cron remains fixed until a separately tested scheduler/controller is adopted.

TEL-03 workflow implementation is present; the first accepted live receipt and immutable publication are operational acceptance. TEL-04 effective permission readback, TEL-05 negative-path integration tests, TEL-06 first accepted runtime receipt, downstream MAINT-02 quota-feed integration, and G1–G5 migration shadows remain distinct gates. A failed collection currently fails the job and is visible in the Actions run; it does not masquerade as a successful G4 receipt or create a successful-observation publication.
