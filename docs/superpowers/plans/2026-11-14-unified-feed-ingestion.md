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
- No live database migration without `LANE_EVENTS_MIGRATION_DATABASE_URL` and a reviewed operator execution plan.
- Runtime ingestion requires `LANE_EVENTS_WRITER_DATABASE_URL` or a read-only Neon API lookup of the dedicated `integration_ingest`/`lane_events_writer` role; legacy owner URLs are excluded.
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
- Optional source cursors are attached to the first/last chunk; a derived `integration_latest_cursors` view exposes only acknowledged final cursors.
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


## Workflow, context and stewardship controls

### Bounded feedback loop

`OBSERVE → CHOOSE → ACT → VERIFY → RECORD → REPEAT or STOP`.

- Observe fresh GitHub branch/base state, workflow runs, jobs, steps, artifacts and current source coverage.
- Choose one highest-value bounded action from the accepted IIS work items.
- Act once, preserving the exact commit and batch identity.
- Verify the same acceptance criteria under recorded conditions.
- Record SHA, run/attempt, batch receipt, hashes, result, failure class and remaining work.
- Repeat only when new evidence can change the next action.

Terminal states: `success`, `clean_noop`, `blocked`, `approval_required`, `exhausted`, `stagnated`.

### Workflow research and repository facts

- The supplied Jules Actions research recommends `google-labs-code/jules-action@v1`, test-driven-development, scoped subagents, and VM setup scripts.
- Repository fact: `.github/workflows/agent-pr-jules-handoff.yml` posts a `DISPATCHED` receipt for trusted `@jules` comments and observes later head mutation; it does not invoke Jules. Do not report Jules execution from that receipt alone.
- Existing root `setup.sh` and `.devcontainer/devcontainer.json` provide the base agent environment. An ephemeral Postgres integration-test fixture is still required for real DDL execution.
- `.github/workflows/**` is operator-owned. This implementation does not change workflow YAML; the focused test invocation requires a separately authorized workflow update.
- No Termux MCP device-control tool is connected in this session, so device health/resource snapshots were unavailable. GitHub repository work used the GitHub connector.
- The repository `LOOPS.md` file was absent. The loop is recorded here; no project-wide loop library was created.

### Context graph freshness

The canonical `workspace/llm_map/context_relationships/manifest.json` is a historical snapshot generated 2026-10-26, marked `PARTIAL`, with `next_start_page = 2`. It is stale for this 2026-11-14 change and was not treated as current graph truth. Current source files and GitHub metadata were inspected directly. Refresh the graph only through its trusted publisher/bounded reconciler; do not edit generated index artifacts directly.

