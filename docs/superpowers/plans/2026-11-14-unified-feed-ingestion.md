# Unified Feed Ingestion — Implementation Plan

**Date:** 2026-11-14  
**Proposal:** `integration-intelligence-superpowers`  
**Work items:** IIS-002 (active), IIS-003–IIS-005 (queued)  
**Branch:** `feat/unified-feed-adapter-20261114`  
**Target:** `master`

## Desired outcome

One normalized integration-event and time-series measurement ingestion contract, one append-only database extension in the existing Neon `lane-events` project, bounded/idempotent batch writes with receipts, and compatible adapters for the existing web and terminal presentation lanes.

## Constraints

- Reuse the existing Integration Intelligence registry and event envelope.
- Preserve v1.0.0 events; new timestamp semantics are v1.1.0.
- Extend the existing Neon project/database; never auto-create a second project.
- Preserve `lane_events`, provider-observation, Provenance, HindSight, Evidence Envelope, JSONL history and dashboard-surface-feed authorities.
- No browser database credentials.
- No workflow YAML edits: `.github/workflows/**` is operator-owned under `docs/proposals/AGENTIC-PERMISSIONS.md`.
- No live database migration without an authorized production credential and a reviewed execution plan.
- No automatic retry in the writer; the owning workflow classifies and decides retries.

## Task 1 — Canonical event/measurement/batch contracts

**Status:** implemented on branch; validation pending.

Paths:
- `docs/integrations/schemas/integration-event.schema.json`
- `docs/integrations/schemas/integration-measurement.schema.json`
- `docs/integrations/schemas/integration-batch.schema.json`
- `docs/integrations/ADAPTER-CONTRACT.md`

Acceptance:
- Event v1.0.0 remains valid.
- Event v1.1.0 requires `observed_at` and privacy classification; `event_at` is source time.
- Measurement values preserve units, dimensions, temporality and null status.
- Batch receipts describe record type, accepted/duplicate/rejected counts, payload bytes/hash and timestamps.
- All schemas parse as JSON and remain closed to unknown properties.

Tests:
- `python3 -m json.tool docs/integrations/schemas/integration-event.schema.json >/dev/null`
- `python3 -m json.tool docs/integrations/schemas/integration-measurement.schema.json >/dev/null`
- `python3 -m json.tool docs/integrations/schemas/integration-batch.schema.json >/dev/null`

## Task 2 — Existing Neon database schema and bounded batch writer

**Status:** implemented on branch; validation pending.

Paths:
- `ops/lane-events/integration-events.sql`
- `scripts/ops/integration_event.py`
- `tests/test_integration_event_batch.py`

Acceptance:
- Add `integration_events`, `integration_measurements`, `integration_ingest_batches` to the existing database.
- Append-only UPDATE/DELETE guards and indexes support event time, observation time and metric series.
- Writer enforces default 250 records / 512 KiB and hard 500 records / 1 MiB ceilings.
- One transaction inserts a batch's records and receipt; stable idempotency keys account for duplicate delivery.
- Failed transactions roll back data and attempt a metadata-only failed receipt.
- Invalid schema, privacy, timestamp, size and secret-shaped values fail closed.
- Neon project lookup is read-only; missing project is a blocker, not a project-creation request.
- Dry-run performs no credential resolution or database I/O.

Tests:
- `python3 -m py_compile scripts/ops/integration_event.py`
- `python3 -m unittest discover -s tests -p 'test_integration_event_batch.py' -v`
- Inspect generated SQL for both record types and failure receipts.
- Execute against an ephemeral Postgres test database only after the repository has an approved test-database fixture; production Neon is out of scope for this PR.

TDD note: the focused test module was added during the first implementation slice, after the initial writer commit. A RED run was not observed in the available environment. The tests and validation evidence must be executed before the item can be marked validated.

## Task 3 — Compatibility adapters and historical reconciliation

**Status:** queued (IIS-003).

Inventory and map:
- `ops/lane-events` records;
- `provider-observation/v1`;
- `ops/telemetry/*.jsonl`;
- `scripts/telemetry_ingest/` outputs;
- `telemetry-feed-series.jsonl` and PR-lane series;
- existing dashboard-surface-feed snapshots.

Each mapping must retain original source ID, source timestamp, collection timestamp, source SHA/ref, parser version, cursor/page bounds, coverage state, idempotency rule and null semantics. No source rewrite or unbounded backfill.

## Task 4 — Shared projections and presentation adapters

**Status:** queued (IIS-004).

- Rebuild existing web feed shapes from one consistent read-model snapshot.
- Preserve static Pages as read-only JSON consumers.
- Feed typed normalized events to the existing Ratatui/Tokio model through bounded channels.
- Define a versioned read-only Termux Unix-domain-socket protocol with permission, framing, message-size and reconnect contracts.
- Evaluate Taria as an optional adapter only after its Rust MSRV, pre-alpha status, protocol and one-client limitation are reconciled.
- Use Ratatui TestBackend for rendered-buffer, empty/error/stale/resize fixtures.

## Task 5 — Benchmarks and recovery validation

**Status:** queued (IIS-005).

Measure records/sec, bytes/sec, batch fill, p50/p95/p99 acknowledgement latency, queue depth, duplicates, rejection, source-cursor lag, projection lag, replay correctness and per-surface parity. Record workload, environment, SHA, run/attempt and artifact provenance. Derive future partitioning and batch tuning from these results.

## Validation record

The GitHub connector was used to create the feature branch and commit the scoped implementation files. No local repository shell or live Neon connection was available in this execution context. The focused Python test, JSON Schema validator, Postgres execution, repository dual gates and current-SHA GitHub checks remain pending until run by the repository's validation surfaces.

Required repository gates:
- `python3 scripts/ci/repo_gate.py`
- `python3 scripts/ci/termux_smoke.py`

A workflow YAML update is deliberately excluded from this agent-owned slice. The operator-owned workflow must later add the focused test invocation to an appropriate integration CI lane.

## Stop conditions

- Missing or unverified existing Neon project: BLOCKED.
- Missing database credentials or migration permission: BLOCKED.
- Schema/privacy/idempotency regression: FAIL.
- Source identity or historical coverage ambiguous: HOLD for reconciliation.
- Repeated cycles without measurable progress: STAGNATED.
- All acceptance criteria proven on one immutable SHA: SUCCESS; promotion follows repository gates and review policy.
