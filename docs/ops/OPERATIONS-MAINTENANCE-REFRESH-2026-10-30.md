# Operations Maintenance Refresh — 2026-10-30

**Repository:** `timerloggedout-spec/termux-monorepo`  
**Default branch:** `master`  
**Master snapshot:** `8d8ac4bbb5dc2a558005d2c2b1acf28ec0534f1c`  
**Observed at:** 2026-10-30 (GitHub API observations; point-in-time, not continuous monitoring)

## Executive status

The repository has advanced materially since the 2026-10-27 hand-off. The current operational focus is now the GitHub App / Repo Replay migration, quota evidence boundaries, notation-driven mesh output, and adaptive telemetry publication.

Recent master commits observed:
- `7b182d5` — merge PR #2450, quota Repo Replay AppID slice + PAT fallback-only trigger.
- `5395190` — regenerate operator matrix (#2455).
- `7d35620` — merge PR #2451, profile-completion builder-resolution annex.
- `ab4d17e` — merge PR #2449, reviewer-metrics Collector-token migration checkoff.

Earlier PR #1735 remains reported by the connector as **open / unmerged**, despite a populated `merge_commit_sha` field. Treat that field as inconsistent metadata, not proof of merge. Its 2026-10-27 snapshot is superseded by this refresh.

## Current workstreams and gates

| Workstream | Observed state | Required next gate |
|---|---|---|
| Repo Replay / GitHub App migration | PR #2450 merged; #2454 open | Verify the AppID route and RR-1/RR-2 migration plan against the live app installation, least privilege, receipt flow, and PAT fallback constraints. |
| Quota / triage router | PR #1441 open, not mergeable; head `e17f7db4...`, base `b8c09be9...` | Rebase/reconcile against current master; obtain a substantive refreshed review; validate current-head CI. Do not promote while exact credential/project binding, authenticated quota/entitlement, and durable accounting remain unresolved. |
| Nomenclature / claim provenance | PR #1734 open; base `50d79c6f...`; head `ad4b8dace...` | Refresh base and verify the dedicated workflow on the exact current head. Candidate records and DCM links remain candidate-only; no equivalence or runtime authority. |
| Mesh poll notation | PR #2453 open; head `3748823c...`; base `7d356206...` | Validate rendering against real poll comments, refresh issues, and step summaries; preserve checklist semantics and evidence references. Its body reports local tests 12/12, not a complete remote acceptance record. |
| Adaptive GitHub App telemetry | PR #2448 draft; head `d25630c3...` | Keep draft. Publisher utility is not wired into Actions; six-hour cadence is design-only; weekly workflow and 30-day artifact remain actual behavior. Add due-time controller, failure-receipt contract, least-privilege workflow integration, tests, and end-to-end receipt before promotion. |
| Migration plan | PR #2454 open; head `9477ded8...`; base `7d356206...` | Confirm RR-1 telemetry-ingest reconciliation and RR-2 PAT→Publisher route are consistent with merged #2449/#2450 and installed GitHub Apps. |

## Quota router: explicit production boundary

PR #1441's latest description reports 453 offline tests and fixes for installation-token comment ownership, cooldown cache behavior, CI trigger coverage, known-exhaustion denial, timezone safety, fixture isolation, coverage accounting, and a CodeQL fixture.

These are implementation/test claims, not production authorization. The PR itself explicitly retains:
- exact Actions credential-to-project binding as unresolved;
- authenticated current project/model quota and entitlement as unresolved;
- durable cross-runner/provider-request accounting as unresolved;
- Gemini eligibility as unknown/false;
- formal review state as CHANGES_REQUESTED until a substantive refreshed review.

No merge, live provider dispatch, credential/OAuth mutation, paid fallback, or production admission activation is authorized by this status note.

## GitHub App / PAT alignment

The migration direction is to make GitHub App installation credentials the normal path and keep PAT use fallback-only or explicitly gated. PR #2450's title/body records a Repo Replay AppID slice and PAT fallback-only trigger; PR #2454 proposes RR-1/RR-2 migration-plan additions.

Acceptance requirements:
1. Verify each installed App's owner, installation ID, repository scope, permissions, and token minting path using authorized GitHub App/installation evidence.
2. Ensure publisher and collector responsibilities are separated, auditable, and least-privilege.
3. Bind every receipt to workflow run, attempt, repository, commit SHA, timestamp, and producer identity.
4. Never publish secrets, raw provider payloads, or private quota counters.
5. Keep PAT fallback explicit, narrow, observable, and non-silent. No automatic broad-scope fallback.
6. Attribute MuseAI activity only when the event/run/job evidence identifies the agent/session; GitHub account identity alone is insufficient.
7. Personal PAT last-used and authorized-application details remain an account-side verification task; this connector does not expose that audit surface. No PAT was changed in this pass.

## Provider validation

This pass did not obtain fresh provider-specific catalog/auth/entitlement/inference evidence. The October 20–21 provider observations documented in the earlier hand-off are stale and must not be presented as current health.

For each provider/model, retain distinct fields:
`credential_present`, `catalog_ok`, `auth_ok`, `entitlement_ok`, `inference_ok`, plus failure classes such as `rate_limited`, `billing_blocked`, `policy_blocked`, `network_error`, and `unknown`.

Do not run paid or potentially billable inference as a health probe. A no-cost test requires explicit authorization, verified free-tier eligibility, one-shot limits, and a hard no-paid-fallback guard.

## Ordered maintenance plan

### P0 — Trust, correctness, migration
- [ ] Reconcile PR #1441 with current master; preserve fail-closed behavior and resolve formal review before promotion.
- [ ] Verify #2450's AppID/Repo Replay slice and #2454's RR-1/RR-2 plan against actual installation permissions and receipt evidence.
- [ ] Confirm PAT fallback cannot silently widen permissions or bypass installation/project binding.
- [ ] Refresh provider evidence only through safe, authorized, bounded checks; keep catalog/auth/entitlement/inference separate.
- [ ] Verify MuseAI's actual credential and effective permissions using account-side audit evidence; do not expose token values.

### P1 — Evidence and telemetry
- [ ] Rebase/validate #1734 against current master and preserve candidate-only DCM/nomenclature semantics.
- [ ] Validate #2453 notation output with golden fixtures for comments, refresh issue titles/bodies, summaries, Unicode symbols, evidence references, and unchanged checklist semantics.
- [ ] Keep #2448 draft until the publisher is wired into Actions, due-time scheduling is persisted, failure receipts are distinct, permissions are least-privilege, and a real end-to-end publication is demonstrated.
- [ ] Ensure all telemetry receipts are append-only/idempotent by run+attempt and cannot overwrite prior evidence.

### P2 — Operational hygiene
- [ ] Reconcile or close stale hand-off PR #1735 after checking its contradictory merge metadata and the actual merge state.
- [ ] Refresh generated operator matrices only from live source data; timestamp and identify source run/SHA.
- [ ] Keep cancelled, skipped, partial, failed, and successful checks distinct.
- [ ] Continue the evidence-first cycle: `RECON → PLAN → IMPLEMENT → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → RECORD → REPEAT`.

## Exit criteria

This refresh is complete when each active workstream has current-base/current-head checks, formal review disposition, traceable run/attempt/SHA evidence, and a clearly stated promotion boundary. Personal-account PAT audit and live provider entitlement remain unresolved until their authoritative evidence is supplied.