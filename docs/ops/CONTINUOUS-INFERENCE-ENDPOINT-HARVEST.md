# Continuous inference endpoint harvesting and operational performance

Implements: MSM-025 (model-selection-market)

## Objective

Continuously discover and normalize inference endpoints from the repository's approved provider catalogues and public activity sources. Fold every valid endpoint into the existing dispatch, quota, DoE, and operational-feed systems so the endpoint population compounds over time.

Extend the existing provider catalog, availability, quota, Swarm, DoE, and dashboard machinery. Reuse their canonical records and generators; keep one source of truth per concern.

## Operating flow

```text
approved provider catalogues + public activity feeds
  → source-pinned harvest + normalized provider×model endpoint delta
  → canonical provider/model registry + dispatch catalogue
  → quota-family / quota-record mapping (unknown remains explicit)
  → DoE participant enrollment + task-fit dispatch pool
  → swarm / nested-family / desk / web activity feed refresh
  → measured dispatch outcomes + usage + latency + rate-limit evidence
  → operational performance scorecard
  ↺ repeat on source change and scheduled cadence
```

## 1. Harvest sources

Use the existing source adapters and discovery surfaces:

- Native provider model catalogues in `scripts/provider_model_catalog.py`.
- Extension and protocol catalogues in `scripts/provider_extension_catalogs.py` and `scripts/provider_catalog_protocols.py`.
- Existing G4F / g4f-working harvested provider×model inventory.
- Existing pinned-source research refresh in `scripts/model_selection_market/provider_recon.py`.
- Approved public web activity sources: provider changelogs, model-release feeds, public GitHub releases/commits, and documented catalogue changes. Activity signals create or refresh candidates; they do not establish invocation, entitlement, or quota.

Every harvest cycle records source identity, canonical URL, observed UTC time, source revision or ETag/Last-Modified where available, content hash, collector version, result status, and a bounded error class. Use conditional requests, pagination caps, response-size caps, timeouts, rate-limit respect, and deduplication. Preserve source provenance and model identifiers verbatim alongside normalized IDs.

## 2. Normalize endpoint identity

The unit of inventory, DoE participation, dispatch accounting, and performance measurement is the provider×model endpoint, not the provider family alone.

Each normalized endpoint carries:

- stable endpoint ID, provider ID, model ID and source aliases;
- source URL, source revision/hash, observed timestamp and freshness;
- modality/task capabilities and declared API protocol;
- lifecycle state (active, deprecated, removed, unknown);
- catalog evidence class and policy/terms review status;
- dispatch surface and task-fit classification;
- quota service/family mapping and quota evidence state;
- DoE participant key and immutable instance identity where dispatched.

Deduplicate aliases against canonical provider identities and exact model IDs. Preserve upstream variants when they represent materially distinct model versions or access routes. Record removed endpoints as tombstones with source evidence; retain history.

## 3. Dispatch and DoE enrollment

Add each valid discovered endpoint to the existing provider dispatch catalogue and DoE participant population. Keep provider-family routing separate from endpoint-level participant identity.

Use distinct states:

- `catalogued`: source-backed endpoint record exists.
- `doe_enrolled`: endpoint has a stable participant key and experiment metadata.
- `dispatch_candidate`: endpoint is visible to task-fit dispatch selection.
- `proof_pending`: a bounded provider-specific invocation proof is required.
- `invocation_proven`: exact provider/model invocation completed with attributable evidence.
- `production_eligible`: all existing capability, policy, entitlement, quota-headroom, route, freshness, and safety gates pass.
- `blocked` / `deferred`: retain a machine-readable reason and next evidence needed.

Catalog discovery automatically creates inventory and DoE candidate participation. Dispatch selection uses the existing task-fit and rotation policy. Proof-pending endpoints receive only explicitly bounded, policy-approved proof experiments. Production dispatch requires the existing admission gates plus provider-specific invocation proof. A catalogue listing, model count, workflow success, family-level route, or public web mention is not invocation proof.

DoE records must use the existing experiment schema, configured-instance key, dispatch/run ID, provider and model identity, task class, treatment, outcome, and usage fields. Candidate enrollment and dispatch attempts remain distinct from successful invocation and confirmed outcome.

## 4. Quota mapping

Map every endpoint to its canonical provider quota family and service record using the existing quota registry and manager contracts.

- Create or reconcile a quota mapping for every endpoint family and model service.
- Reuse provider-specific passive managers and existing response/header observations.
- Publish documented limits separately from measured usage and remaining balance.
- Carry source, observed UTC time, reset window/timezone, authority, and freshness.
- Keep `unknown`, `stale`, `unavailable`, and `not-entitled` explicit.
- A missing quota reader remains a coverage gap; a public limit never becomes account headroom.
- Feed quota headroom into existing cadence and dispatch preflight. Preserve free-first and no-paid-fallback policy.

## 5. Invocation proof and credential blockers are separate ledgers

Maintain provider-specific invocation evidence as its own endpoint-level proof record. Each proof identifies the exact provider, model, route/adapter, runtime environment, run/attempt, timestamp, response class, latency, and redacted request/response metadata.

Maintain credential/provisioning blockers in the existing credentials-blocked inventory and provider blocker surfaces. Keep that list separate from invocation proof: a missing credential is a blocker state, not an invocation result; a successful catalog read is not proof of a completion route. Store secret names and availability state only. Keep secret values, tokens, cookies, sessions, and raw authorization payloads outside Git and generated feeds.

Classify invocation outcomes distinctly: success, credential-missing, entitlement-unknown, billing-blocked, policy-blocked, rate-limited, capacity, route/model mismatch, egress/network, timeout, malformed response, and unknown. Use bounded retries only where the provider contract permits; honor Retry-After and provider reset semantics.

## 6. Operational feeds and visibility

Regenerate existing derived feeds from their canonical inputs:

- `ops/challenge/desk-feed.json` — complete provider dispatch catalogue, endpoint census, dispatch classes, and blocker references.
- `ops/tracking/nested-family.json` — endpoint/model membership and task/dispatch counts.
- `ops/quota/swarm-feed.json` and dashboard mirror — family and endpoint quota coverage, population, usage, rate-limit events, and gaps.
- `ops/quota/usage-series.json` — measured provider/model usage series.
- Existing web activity and dashboard feeds — source changes, new/removed models, harvest freshness, dispatch outcomes, and operational gaps.

Generated files remain generator-owned. Update their builders and contracts; avoid hand-editing generated snapshots as a substitute for source integration.

## 7. Operational performance scorecard

Publish endpoint and family aggregates with explicit denominators, time windows, source timestamps, and confidence. At minimum report:

| Metric | Definition |
|---|---|
| Catalogue freshness | Endpoints with a successful source observation inside the configured freshness window / endpoints expected from active sources |
| Harvest yield | New, changed, deprecated, and removed endpoint counts per cycle |
| Dispatch coverage | Catalogued endpoints mapped into the dispatch catalogue / valid catalogued endpoints |
| DoE coverage | Valid catalogued endpoints enrolled as participants / valid catalogued endpoints |
| Quota mapping coverage | Endpoints with a canonical quota-family/service mapping / valid catalogued endpoints |
| Quota evidence freshness | Mapped endpoints with fresh authoritative or measured quota evidence / mapped endpoints |
| Invocation proof coverage | Endpoints with current provider-specific successful invocation proof / endpoints requiring proof |
| Credential-blocked coverage | Endpoints carrying a current credential/provisioning blocker, reported from the separate blocker inventory |
| Dispatch throughput | Attempts, completed invocations, failures, deferrals, and unique endpoints by time window |
| Operational reliability | Success rate, latency percentiles, timeout/error classes, 429 rate, and recovery time, separated by provider×model |
| Evidence lag | Time from upstream source change to normalized record, dispatch/DoE enrollment, and feed publication |

Report both endpoint-weighted and provider-family-weighted views. Preserve cohort and task-class splits so a large family cannot hide a failing endpoint. Separate catalog coverage, dispatch participation, invocation proof, and production eligibility in every dashboard.

## 8. Cadence and automation

Use existing provider-availability, catalog-sync, provider-recon, quota, DoE, and surface-feed workflows. Add source-change triggers where supported and a bounded scheduled reconciliation for sources without events. Reuse the existing scheduler and workflow permissions; avoid a parallel poller or scheduler.

A cycle is complete only when its normalized delta is reconciled into dispatch, quota, DoE, and feed outputs, or each unresolved surface has a named gap with owner/evidence requirement. Publish an append-only cycle receipt containing source revisions, endpoint counts/deltas, updated output refs, run IDs, errors, and duration.

## 9. Acceptance criteria

1. Every approved source is enumerated with owner, protocol, cadence, terms boundary, and freshness policy.
2. Repeated harvests are idempotent and produce deterministic endpoint deltas.
3. New endpoints appear in the canonical dispatch catalogue and DoE participant population with stable provider×model identity.
4. Quota mappings cover every endpoint family; unavailable account-specific evidence stays unknown.
5. The separate credential-blocker inventory remains authoritative and receives endpoint/provider blocker references without secret values.
6. Provider-specific invocation proof is independently attributable to exact provider×model, adapter, runtime, and run.
7. Existing desk, nested-family, swarm/quota, usage-series, and web activity feeds reflect the same harvest cycle.
8. Operational performance metrics expose denominators, freshness, failure classes, and cohort splits.
9. Tests cover new/changed/removed endpoints, aliases, duplicate models, source outages, pagination, 429/Retry-After, stale evidence, missing credentials, quota unknown, proof success/failure, and feed reconciliation.
10. Repo-gate and Termux smoke pass; implementation PRs cite `Implements: MSM-025` and include run-backed end-to-end evidence.

## Existing canonical surfaces

- `scripts/provider_model_catalog.py`
- `scripts/provider_availability_probe.py`
- `scripts/model_selection_market/provider_recon.py`
- `scripts/ops/provider_invoke.py`
- `scripts/ops/auto_quota_cadence.py`
- `scripts/quota_swarm_feed.py`
- `scripts/dashboards/surface_feeds.py`
- `ops/quota/registry.json`
- `ops/quota/swarm-feed.json`
- `ops/tracking/nested-family.json`
- `ops/challenge/desk-feed.json`
- `experiments/doe/routed-dispatch/`
- `docs/ops/PROVIDER-DISPATCH-MAP.md`
- `docs/ops/CADENCE-PROVIDER-ONBOARDING.md`
- `docs/ops/INFERENCE-AVAILABILITY-LEDGER.md`

## Boundaries

This work expands discovery, participant enrollment, observability, and dispatch coverage. Provider-specific invocation proof, credentials, terms acceptance, entitlement, quota headroom, and production admission remain separate evidence gates. Public web activity is a discovery signal only. Existing account and free-tier policy, no-secret-in-Git policy, task-fit rotation, dual-gate promotion, and append-only evidence rules remain in force.
