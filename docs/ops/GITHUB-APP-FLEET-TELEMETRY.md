# GitHub App fleet telemetry

Status: the adaptive telemetry implementation is on the feature branch; it is not active on `master` until reviewed, merged, and operationally verified. PR validation remains declaration-only and receives no App credentials.

## Collection and publication

- `ops/github-apps/registry.json` inventories app identities without secret values; each app manifest is the declared-permission source of truth.
- `scripts/github/github_app_telemetry.py` emits declarations plus a sanitized G4 runtime receipt for the explicitly named app.
- The feature-branch workflow wakes hourly (minute 17). A persisted cadence controller decides whether a census is due; not every hourly wake performs a full census.
- The controller adapts the next census interval from measured post-census rate-limit headroom: 3 hours at 75% or greater remaining, 6 hours at 50–74%, 12 hours at 25–49%, and 24 hours below 25%. Manual dispatch forces a census.
- Due-time state is stored in `ops/github-apps/telemetry-cadence-state.json` and updated after successful publication. If census or publication fails, state is not advanced, so the next hourly opportunity retries.
- Every census mints a fresh short-lived Collector installation token using `TERMUX_FLEET_COLLECTOR_APP_ID` and `TERMUX_FLEET_COLLECTOR_PRIVATE_KEY`; client ID is verified as a configured input but the mint action uses App ID.
- G4 receipts contain mint outcome, rate-limit before/after, API calls by HTTP status, repositories inspected, workflow run ID/attempt/SHA, duration, conclusion, and timestamp. Unknown fields are rejected; authorization material is never serialized.
- Successful censuses upload a 90-day artifact and publish a unique observation under `ops/github-apps/observations/YYYY/MM/DD/`, keyed by workflow run ID and attempt.
- The census job alone receives `contents: write` for publication and cadence-state updates. The Collector installation token remains read-only and is never used to publish. PR validation remains read-only.
- The publisher supplies no existing-file SHA, so an existing observation path is rejected rather than overwritten. It verifies receipt run ID and attempt against the publishing workflow.
- Collector remains read-only. Publisher is a separate principal and its credentials are not reused. Reviewer-ops, Gate/CI, and Lifecycle remain conference-draft/not-provisioned.
- Missing or partial API responses fail closed; no incomplete repository scope is represented as observed.

## Acceptance gates

- Workflow and publisher/controller tests must pass on the PR.
- Verify the first real scheduled/manual census, G4 receipt, 90-day artifact, immutable observation, and cadence-state update.
- Complete TEL-04 effective permission readback and TEL-05 negative-path integration coverage.
- Complete MAINT-02 quota-feed integration using evidence-backed readings.
- Keep G1–G5 migration shadows and PAT retirement separately gated.
- Failure receipts remain a separate contract: failed collection must not be represented as a successful G4 receipt.
