# Research execution contract — THUB-017

This implementation is opt-in and unmerged/undeployed, stacked on PR #1470 at `d2778bcc25966533ccd2f5bc1991aab672fb9cbe`. #1531 is proposal history. No live provider requests, paid fallback, new remote service, native Android validation, or deployment is implied.

## One shared admission boundary

Every inference dispatched by `POST /v1/chat/completions`, including Python/Rust Swarms, traverses `server/admission.py`. Configure `LLM_API_HUB_QUOTA_RECORDS` and optionally `LLM_API_HUB_QUOTA_DB` before starting the hub. Missing, malformed, stale, unverified, exhausted, reset-expired, or cooling-down evidence denies inference. Existing native-provider terms/free-account policy is an additional requirement. There is no provider fallback.

The private JSON source is `{"schema_version": 1, "records": [...]}`. Rows bind exact hub `provider/model`, provider, authenticated account alias, explicit shared scope, `free_account_verified: true`, `evidence_status: "confirmed"`, `horizon: "H0"`, timezone-aware `observed_at`/`reset_at`, and integer `remaining` request units. Optional `remaining_tokens` and `cooldown_until` constrain the same bucket. Money, percentages, public advertisements and trial balances are not request entitlements.

`server/quota_observations.publish_observation()` atomically publishes mode-0600 records from existing `scripts.provider_quota_managers.normalize_observation()` output. The credential-owning caller must explicitly verify the authenticated account/free entitlement and exact provider/model binding. A passive unverified scope alone cannot authorize inference. This API does not poll providers, load keys, or verify any real account; tests use synthetic verified fixture bindings.

SQLite transactions share allowance by account/provider/scope, not per agent or model. Durable window identity prevents refreshed or drifting reset timestamps from creating another allowance; a genuinely expired window needs a newly observed record. Unique attempt IDs prevent repeat dispatch. Durable send intent precedes inference. Known unsent failures can release; timeout, crash, cancellation after send, and unknown usage retain conservative charges. Actual integer token usage reconciles when available. HTTP 429 persists cooldown across callers/restarts. Conservative under-admission is preferable to guessed capacity.

## Correlation and existing 3L0 evidence

Top-level JSON or matching `X-Termux-*` headers accept `run_id`, `job_id`, `request_id`, `attempt_id`, `parent_id`, `adapter`, and `source_revision`. Conflicting body/header identifiers are rejected. These are bounded ASCII identifiers, never prompt/task content. Each outbound call uses unique request/attempt IDs, common run/job IDs, parent ancestry and the immutable adapter pin. The hub emits admission and terminal lifecycle events with exact model/provider through existing `TermuxTelemetryLogger`.

Python uses the existing hub client. Rust uses a temporary bounded loopback bridge to the configured hub endpoint only, preserving hub authorization and adding per-call lineage; it is not a provider route or service. AdvancedResearch executes genuine hash-verified orchestration in a killable temporary worker with bounded injected dependency facades, not full upstream SDK parity.

`scripts/telemetry/research_evidence.py` projects terminal events into the existing `PerformanceLedger`. Sanitized lineage remains in provenance; repeated adapter/hub observations of one attempt are deduplicated. Task dimensions remain null, task outcome `UNKNOWN`, confidence zero, and routing weights unchanged. HTTP 200 is not task success.

## Disable, recover, validate

Leave adapter execution disabled to stop new Research work. Never delete the shared database to regain allowance. Known unsent reservations may use `reconcile(token, actual=0)`; sent/ambiguous reservations stay charged until verified reset evidence. There are no automatic retries or speculative releases.

`research-paper-validation.yml` checks the exact candidate SHA, genuine-source fake-backed hub tests, both repository gates, and a locked Rust-worker/fake-hub job. Receipts bind candidate/workflow revisions, source/fixture hashes and artifact SHA-256 hashes. Linux evidence is not native Android evidence. Native issues stay open for implementation/evidence review; no generated receipt proves task correctness, merge or deployment.
