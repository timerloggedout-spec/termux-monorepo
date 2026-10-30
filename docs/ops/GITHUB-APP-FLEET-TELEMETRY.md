# GitHub App fleet telemetry

Status: the adaptive telemetry proposal now implements six-hour Collector census opportunities, per-run immutable observation publication, and a 90-day artifact copy on its feature branch. These changes are not active on `master` until reviewed, merged, and operationally verified. PR validation remains declaration-only and does not receive App credentials.

## Collection and publication

- `ops/github-apps/registry.json` inventories app identities without secret values; each app manifest is the declared-permission source of truth.
- `scripts/github/github_app_telemetry.py` emits declarations plus a sanitized G4 runtime receipt for the explicitly named app.
- The feature-branch workflow uses `17 */6 * * *` (UTC) and supports manual dispatch on `master`. The current `master` workflow remains Monday 06:17 UTC until this change is accepted.
- Every live census mints a fresh short-lived Collector installation token using `TERMUX_FLEET_COLLECTOR_APP_ID` and `TERMUX_FLEET_COLLECTOR_PRIVATE_KEY`; client ID is verified as a configured input but the mint action uses App ID.
- G4 receipts contain mint outcome, rate-limit before/after, API calls by HTTP status, repositories inspected, workflow run ID/attempt/SHA, duration, conclusion, and timestamp. Unknown fields are rejected; authorization material is never serialized.
- Successful censuses upload a 90-day artifact and invoke `scripts/github/publish_github_app_telemetry.py` to create a run/attempt-addressed observation under `ops/github-apps/observations/YYYY/MM/DD/`.
- The census job alone receives `contents: write` for publication. The Collector installation token remains read-only and is never used to publish. The PR validation job remains read-only.
- The publisher supplies no existing-file SHA, so an existing observation path is rejected rather than overwritten. It verifies that receipt run ID and attempt match the publishing workflow.
- Collector remains read-only. Publisher is a separate principal and its credentials are not reused. Reviewer-ops, Gate/CI, and Lifecycle remain conference-draft/not-provisioned.
- Missing or partial API responses fail closed; no incomplete repository scope is represented as observed.

## Adaptive operation: current boundary

Six-hour cron is a more frequent fixed cadence, not yet a fully dynamic scheduler. The G4 receipt exposes rate-limit headroom that can drive adaptive policy, but actual dynamic backoff requires persisted next-due state and a tested cadence controller. Until that exists, do not claim the schedule changes itself. A failed collection fails the run; it does not create a successful observation. Failure receipts and publication are a separate follow-up contract.

## Acceptance gates

- Workflow and publisher tests must pass on the PR.
- Verify the first scheduled/manual live run, G4 receipt, artifact, and immutable repository observation.
- Complete TEL-04 effective permission readback and TEL-05 negative-path integration coverage.
- Complete MAINT-02 quota-feed integration using evidence-backed readings.
- Keep G1–G5 migration shadows and PAT retirement separately gated.
