# GitHub App fleet telemetry

Status: weekly live Collector census is implemented; PR validation is declaration-only. Publisher is registered as a separate identity but is not probed until its own credential binding is verified.

- `ops/github-apps/registry.json` inventories app identities without secret values; each app manifest is the declared-permission source of truth.
- `scripts/github/github_app_telemetry.py` emits declarations plus a sanitized G4 runtime receipt for the explicitly named app.
- `.github/workflows/github-app-telemetry.yml` runs every Monday at 06:17 UTC and supports manual dispatch. PR validation never receives app credentials or mints tokens.
- Every live census mints a fresh short-lived Collector installation token using `TERMUX_FLEET_COLLECTOR_APP_ID` and `TERMUX_FLEET_COLLECTOR_PRIVATE_KEY`; client ID is verified as a configured input but the mint action uses App ID.
- G4 receipts contain mint outcome, rate-limit before/after, API calls by HTTP status, repositories inspected, workflow run ID/attempt/SHA, duration, conclusion, and timestamp. Unknown fields are rejected; authorization material is never serialized.
- Collector remains read-only. Publisher is a separate principal and its credentials are not reused. Reviewer-ops, Gate/CI, and Lifecycle remain conference-draft/not-provisioned.
- Missing or partial API responses fail closed; no incomplete repository scope is represented as observed.
- Artifacts are retained for 30 days and are not committed to the repository.

TEL-03 implementation is present; its first scheduled/manual live workflow run is the operational acceptance. TEL-04 effective permission readback, TEL-05 negative-path integration tests, TEL-06 first accepted runtime receipt, and downstream G1–G5 migration shadows remain distinct gates.
