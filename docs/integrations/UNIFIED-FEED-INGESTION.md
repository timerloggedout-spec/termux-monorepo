# Unified Feed Ingestion and Multi-Surface Adapter Architecture

**Proposal:** integration-intelligence-superpowers  
**Work items:** IIS-002 through IIS-005  
**Status:** IIS-002 contract/database foundation in progress; later adapters queued  
**Operator directive:** 2026-11-14

## 1. Decision

Unify the **data plane**, not the source systems, workflow engines, or presentation surfaces.

Use the existing Integration Intelligence event contract and the existing Neon `lane-events` project/database. Extend that database with normalized integration-event, time-series measurement, and append-only ingestion-batch tables. Keep source-specific adapters thin and keep dashboards as rebuildable read-only projections.

This architecture creates no second database, source registry, scheduler, merge authority, or dashboard framework.

## 2. Existing authorities to preserve

| Concern | Existing authority | Treatment |
|---|---|---|
| Integration identity | `docs/integrations/registry.json` | Reuse stable integration IDs |
| Normalized lifecycle event | `schemas/integration-event.schema.json` | Keep canonical; v1.1.0 adds explicit clocks and preserves v1.0.0 |
| Numeric observations | `schemas/integration-measurement.schema.json` | New child record linked to event ID |
| Batch accounting | `schemas/integration-batch.schema.json` | New immutable batch receipt |
| Workflow completion ledger | Neon `lane_events` | Preserve specialized table and recorder |
| Integration event/measurement storage | Same Neon `lane-events` project/database | Additive tables; no new project |
| Provenance and retention | `scripts/telemetry_ingest/` | Keep Provenance and HindSight independent |
| Provider usage/quota | `provider-observation/v1`, quota registry and source APIs | Preserve source-specific evidence and null semantics |
| Reconciliation evidence | `docs/ops/EVIDENCE-ENVELOPE.schema.json` | Reference evidence; do not duplicate it |
| Dashboard snapshots | `dashboard-surface-feed/v1` and `scripts/dashboards/surface_feeds.py` | Rebuildable projections |
| Feed-history series | Existing JSONL series patterns | Reuse; never treat a rendered feed as source truth |
| Ratatui/Tokio | `integrations/ratatui-tokio-dashboard/` | Separate read-model client |
| OPS-EVENT replay | Existing SeekLog/HITL proposal | Reuse its event-range and replay identity |

The historical telemetry-viz reconnaissance is a dated snapshot, not a current complete inventory. The compatibility adapter census must re-fetch live source files and workflows before implementation.

## 3. Data path

```text
GitHub / Actions / provider APIs / webhooks / local agents
                         |
                         v
              source-specific adapters
                         |
              allowlist + normalize
                         |
              schema + privacy validation
                         |
              stable IDs + idempotency
                         |
                bounded micro-batches
                         |
             one Postgres transaction
                         |
           +-------------+-------------+
           |             |             |
           v             v             v
     integration_events  integration_measurements
           |             |             |
           +-------------+-------------+
                         |
                ingestion receipts
                         |
                read-only projections
                         |
          +--------------+--------------+
          |              |              |
         Web          Ratatui/TUI     CLI / MCP
                         |
                 optional Taria bridge
                   over Unix socket
```

HindSight and Provenance remain independent sinks fed from sanitized source reads. They are not downstream copies of the new Postgres tables.

## 4. Canonical record types

### 4.1 Integration event

The existing `integration-event.schema.json` remains the lifecycle envelope. New events use schema version `1.1.0`:

- `event_at`: source-reported event time; null when unavailable.
- `observed_at`: adapter observation time; required in 1.1.0.
- `recorded_at`: database acceptance time, assigned by Postgres.
- `supersedes`: optional prior event ID; correction is a new event.

Existing 1.0.0 events remain valid and retain their original envelope. Their database `observed_at` is assigned at ingestion if the source did not provide it. The original event JSON is retained without rewriting it.

### 4.2 Measurement

A measurement is a numeric child observation linked to an event ID. Its identity includes measurement ID and idempotency key. Its series dimensions include integration, metric name, metric type, unit, temporality and bounded scalar dimensions.

Supported metric types: counter, gauge, rate, duration and percentage.

Supported temporalities: instant, delta and cumulative.

Measurement statuses: measured, estimated, activity_only and not_established. Measured/estimated require a numeric value; activity_only/not_established require null. Missing is never zero.

### 4.3 Batch receipt

One immutable receipt describes each attempted transaction:

- batch ID, integration ID, adapter version and record type;
- received, inserted, duplicate and rejected counts;
- serialized payload bytes and SHA-256;
- start/completion timestamps;
- optional source cursor before/after;
- status and bounded error classification.

Receipts contain metadata and hashes, never the original raw batch.

## 5. Database model

The migration `ops/lane-events/integration-events.sql` adds three tables to the existing Neon database:

| Table | Key | Purpose |
|---|---|---|
| `integration_events` | event_id; unique idempotency_key | Canonical lifecycle event and source/evidence projections |
| `integration_measurements` | measurement_id; unique idempotency_key | Append-only numeric time-series points |
| `integration_ingest_batches` | batch_id | Immutable batch accounting and recovery evidence |

### Index strategy

- B-tree: integration ID + event/observation time.
- B-tree: repository + workflow run ID.
- B-tree: integration ID + metric name + observed time.
- GIN: bounded JSONB dimensions.
- BRIN: append-correlated event/observation timestamps.

The initial migration uses ordinary Postgres indexes. Time partitioning or TimescaleDB is a measured follow-up, not an assumed dependency. Partitioning is admitted only after table growth, query plans, write amplification, and Neon support are measured.

### Immutability

All three tables reject UPDATE, DELETE and TRUNCATE. Measurements use a composite foreign key so an event ID cannot be associated with a different integration ID. Event/measurement batch references are deferred until transaction commit, allowing the immutable batch receipt and records to be committed atomically. Idempotent re-delivery is handled by unique idempotency keys. Corrections append a new event/measurement and use `supersedes`; history is never silently rewritten.

## 6. Access and credential separation

The new adapter deliberately separates migration, ingestion and query privileges:

| Credential | Use | Required privilege |
|---|---|---|
| `LANE_EVENTS_MIGRATION_DATABASE_URL` | Explicit `schema` command only | Operator-controlled DDL/migration role |
| `LANE_EVENTS_WRITER_DATABASE_URL` | Event/measurement `record` | Dedicated writer role: SELECT + INSERT on the three tables, TEMP on the database |
| `LANE_EVENTS_READONLY_DATABASE_URL` | `count` and future projections | SELECT only |
| `NEON_API_KEY` | Read-only discovery of the existing project and dedicated writer role URI | Project/branch/role metadata access; never creates a project or role |

The writer role must be named `integration_ingest` or `lane_events_writer`. The resolver refuses `neondb_owner` and never falls back to the legacy `LANE_EVENTS_DATABASE_URL` used by the existing lane-event recorder. The `record` command does not apply DDL. The `schema` command requires the separate migration URL. Role creation, credential provisioning and grants remain operator-controlled; no passwords or connection strings enter source.

Expected grants for an already-provisioned writer role:

```sql
REVOKE ALL PRIVILEGES ON integration_events, integration_measurements, integration_ingest_batches FROM integration_ingest;
REVOKE CREATE ON SCHEMA public FROM integration_ingest;
GRANT USAGE ON SCHEMA public TO integration_ingest;
GRANT SELECT, INSERT ON integration_events TO integration_ingest;
GRANT SELECT, INSERT ON integration_measurements TO integration_ingest;
GRANT SELECT, INSERT ON integration_ingest_batches TO integration_ingest;
GRANT SELECT ON integration_latest_cursors TO integration_ingest;
GRANT TEMP ON DATABASE neondb TO integration_ingest;
```

The writer role must not own these tables/schema and must not inherit `neondb_owner` or a migration role. It receives no UPDATE, DELETE, TRUNCATE or CREATE privileges. The read role receives SELECT only. The migration role is not used by runtime adapters.

## 7. Bounded ingestion policy

Initial adapter defaults:

| Control | Default | Hard ceiling |
|---|---:|---:|
| Records per transaction | 250 | 500 |
| Serialized JSON payload | 512 KiB | 1 MiB |
| Database transaction | One per batch | One per batch |
| Queue behavior | Bounded; backpressure | No unbounded in-memory growth |
| Retry | Transient database faults only | No retry on schema/auth/privacy failures |

Adapters may select smaller limits. Limits are configuration, not source-data truncation. A single record larger than the configured batch byte limit is rejected with a visible receipt/error; it is never silently clipped.

The writer is `scripts/ops/integration_event.py`. It groups records by integration ID, validates before database submission, hashes canonical serialized records, and inserts a batch plus its records in one transaction. Unique conflicts count as duplicates; primary-key collisions with different idempotency keys fail the transaction. A failed database transaction rolls back its data writes and attempts a separate metadata-only `failed` receipt; if the database is unreachable, the CLI failure remains the execution evidence. Preflight-invalid records fail before a database transaction.

### Delivery and recovery

- Delivery is assumed at-least-once.
- Deduplication uses stable provider identity + source version; arrival time is not an idempotency key.
- Preserve out-of-order arrivals with source event time, observation time and database record time.
- Persist source cursors only after the corresponding batch transaction is acknowledged. A `--batch-metadata-file` supplies optional cursor metadata keyed by record type and integration ID; `cursor_before` is attached to the first chunk and `cursor_after` only to the final chunk. Failed receipts always store a null `cursor_after`.
- The read-only `integration_latest_cursors` view exposes only the latest emitted receipt with a non-null `cursor_after`; partially committed pages cannot advance the source checkpoint.
- Final-chunk cursor advancement takes a transaction-scoped advisory lock per `(integration_id, record_type)` and compares the stored cursor with `cursor_before`. A mismatch raises `integration_cursor_conflict` and rolls back that final batch; replay is idempotently accepted when the stored cursor already equals the requested `cursor_after`.
- Cursor values are non-secret opaque identifiers (maximum 512 characters). Providers whose continuation tokens contain credentials keep those tokens in secret-backed state and store only a non-secret identifier/hash in the receipt.
- The batch writer performs one attempt and never retries internally. The owning workflow may retry only classified transient failures with bounded exponential backoff and provider Retry-After when present; every attempt gets a new batch receipt and stable record idempotency keys.
- Authentication, permission, signature, schema, privacy and source-integrity errors stop the adapter.
- A failed batch does not block unrelated integrations.
- Every failure is classified; errors and exhausted retries are not success.

### High-frequency behavior

Durable event/measurement ingestion is loss-accounted. Bounded channels apply backpressure rather than silently dropping accepted observations. UI rendering may coalesce redundant gauge redraws, but it must distinguish display coalescing from durable measurement persistence.

Measure records/sec, bytes/sec, batch fill, transaction duration, p50/p95/p99 acknowledgement latency, queue depth, duplicate ratio, rejection ratio, cursor lag and projection lag. Do not claim HFT performance until repeatable benchmark evidence exists.

## 8. Adapter interface

Every adapter implements the same logical stages:

1. `discover()`: identify source/capability and its supported pagination/webhook behavior.
2. `fetch(cursor, window)`: bounded source read; preserve source IDs and timestamps.
3. `normalize(raw)`: map to canonical event/measurement records.
4. `validate(records)`: schema, privacy, size, identity and provenance checks.
5. `batch(records)`: group by integration and enforce record/byte ceilings.
6. `append(batch)`: one database transaction and immutable receipt.
7. `ack(cursor)`: advance cursor only after durable acknowledgement.
8. `project(range)`: produce a read-only surface snapshot from canonical records.

The adapter never owns source truth, scheduling, authorization, dashboard rendering, or merge decisions.

## 9. Workflow orchestration and bounded feedback

Reuse the repository's existing `repo-gate`, `termux-smoke`, `integration-portfolio`, `proposal-lifecycle` and `Agent PR Jules Handoff` surfaces; avoid creating a parallel workflow system.

The current `Agent PR Jules Handoff` workflow is a **handoff receipt and mutation observer**, not a Jules execution adapter: its `@jules` comment path posts a `DISPATCHED` receipt, while its synchronize path records a later PR-head mutation. It does not invoke `google-labs-code/jules-action@v1`. The attached Jules workflow research recommends the official action, test-driven-development, scoped subagents, and reproducible VM setup. Treat those as design inputs, not evidence that Jules ran.

The repository already has root `setup.sh` and `.devcontainer/devcontainer.json` for Python 3.12, Node 20, Rust and GitHub CLI. A disposable Postgres service/test fixture is still a follow-up. Keep production Neon credentials out of Jules/Codespaces jobs; use an ephemeral test database for SQL integration tests.

Workflow ownership is explicit: `.github/workflows/**` is operator-owned under `docs/proposals/AGENTIC-PERMISSIONS.md`. This PR adds no workflow YAML. The focused batch test is authored but not yet wired into an operator-owned CI lane. A provider quota limit, missing review, or pending review is `review_blocked`, never a pass.

Use test-first execution for follow-on source adapters. Delegate only disjoint adapters with explicit file ownership; keep shared schemas, registry, database migrations and projections under one integration owner. A reviewer gate should hold on unresolved medium/high findings; no automatic merge.

**Bounded loop:** `OBSERVE → CHOOSE → ACT → VERIFY → RECORD → REPEAT or STOP`.

- Re-fetch the exact branch/base SHA and fresh run/job/step/artifact state before consequential actions.
- Choose one bounded, reversible unit with a measurable acceptance check.
- Verify under the same recorded conditions; distinguish queued, executed, validated and promoted.
- Record the receipt, hashes, outcome, failure class and remaining work.
- Repeat only when new evidence can change the next action.

Terminal states: `success`, `clean_noop`, `blocked`, `approval_required`, `exhausted`, `stagnated`. Never turn a failed run, exhausted budget or unavailable reviewer into success.

## 10. Historical method reconciliation

| Existing path | Classification | Migration treatment |
|---|---|---|
| Neon `lane_events` | Specialized operational ledger | Preserve; add read-only adapter into normalized event projection |
| `integration-event.schema.json` | Canonical event contract | Preserve; version 1.1.0 clocks |
| `provider-observation/v1` | Provider-specific observation contract | Map known scalar usage/quota fields to measurements; preserve unknown fields only through existing allowlisted provider-metric rules |
| `ops/telemetry/*.jsonl` | Append-only evidence series | Preserve and reference; adapters do not rewrite source lines |
| `telemetry-feed-series.jsonl` and PR-lane series | Snapshot history | Keep as projection history, not raw event ledger |
| `dashboard-surface-feed/v1` JSON | Read-only presentation contract | Rebuild from the read model; retain existing surface-specific shapes |
| HindSight payloads | Retention sink | Independent delivery, independent failure and billing gates |
| Provenance ledger | Attribution/evidence sink | Independent append-only evidence authority |
| Ratatui demo stream | Synthetic UI fixture | Keep test/demo only; never label it production telemetry |

Each compatibility adapter needs a dated census, source schema/version, owner, freshness, idempotency mapping, backfill cursor, coverage receipt and deprecation decision before any historical migration.

## 11. Presentation surfaces

### Web dashboards

Static Pages continue consuming committed, sanitized JSON projections. Browser code receives no Neon credentials and does not query the database directly. A shared projection builder generates the existing per-surface feed contracts from one consistent snapshot/cut.

### Ratatui/Tokio

A normalized read client feeds typed events through bounded Tokio channels into the existing `DashboardState`. Provider parsing and database/network I/O stay outside the UI model. The model remains deterministic and renderer-independent.

### Unix domain socket

A local Termux bridge may expose a versioned, read-only snapshot stream to local consumers. Socket directory permissions, owner-only access, path length, framing, maximum message size, connection lifecycle and peer identity are explicit. It never exposes a database URL or write-capable database client.

### Taria

Taria is an optional semantic accessibility/agent-control adapter above Ratatui, not the event store or ingestion engine. Its published 0.2.0 adapter documents NDJSON snapshots over a Unix socket, acknowledgements, a single bridge client, pre-alpha status, and Rust 1.88+ quick-start requirements. The current TUI crate declares Rust 1.85, so dependency adoption is deferred pending MSRV and security/compatibility review.

### Ratatui TestBackend

Use `ratatui::backend::TestBackend` for deterministic renderer integration tests. Cover normal snapshots, missing/stale values, long labels, empty states, error states, resize and bounded-history rendering. Keep pure model tests separate from renderer tests.

## 12. Rollout sequence

| Phase | Work | Gate |
|---|---|---|
| A | Event/measurement/batch schemas + same-Neon append-only DDL + offline batch writer | Schema fixtures, DDL inspection, idempotency/privacy/size tests |
| B | Compatibility adapters for lane events, provider observations and JSONL histories | Coverage receipts, replay/dedup tests, source authority review |
| C | Shared projection builder for existing Web surfaces | Per-surface parity, same snapshot cut, freshness and gap tests |
| D | Ratatui typed read adapter + local UDS protocol | Bounded channel tests, socket permission tests, TestBackend tests |
| E | Optional Taria experiment and benchmark cohort | Rust MSRV compatibility, protocol/version, single-client limitation, adversarial tests |
| F | Throughput and recovery benchmark | Reproducible p50/p95/p99, throughput, duplicate, loss and cursor evidence |

Promotion requires same-SHA repository gates, independent review and actual runtime receipts. No workflow is marked operational because a schema or PR exists.

## 13. Current implementation entry points

The first foundation slice provides:

```sh
python3 scripts/ops/integration_event.py record \
  --events-file events.jsonl \
  --measurements-file measurements.jsonl \
  --dry-run

LANE_EVENTS_MIGRATION_DATABASE_URL=<operator-provisioned-migration-url> \
  python3 scripts/ops/integration_event.py schema

LANE_EVENTS_WRITER_DATABASE_URL=<dedicated-writer-url> \
  python3 scripts/ops/integration_event.py record \
  --events-file events.jsonl --measurements-file measurements.jsonl \
  --batch-metadata-file batch-cursors.json

LANE_EVENTS_READONLY_DATABASE_URL=<read-only-url> \
  python3 scripts/ops/integration_event.py count
python3 -m unittest discover -s tests -p 'test_integration_event_batch.py' -v
```

Example `batch-cursors.json`:

```json
{
  "event": {
    "github-actions": {
      "cursor_before": "page:4",
      "cursor_after": "page:5"
    }
  }
}
```

The dry run validates records and prints bounded batch plans without resolving credentials or contacting Neon. The schema command requires the operator-provisioned `LANE_EVENTS_MIGRATION_DATABASE_URL` and applies only to the already-existing `lane-events` Neon project/database. The record command requires `LANE_EVENTS_WRITER_DATABASE_URL` or `NEON_API_KEY` resolving an existing dedicated `integration_ingest`/`lane_events_writer` role. It never uses the legacy `LANE_EVENTS_DATABASE_URL`, never falls back to `neondb_owner`, and never auto-applies DDL. Count uses a read-only URL or the dedicated writer role with SELECT.

The initial writer is an adapter primitive, not yet wired to every source or scheduled workflow. Source adapters, dashboard projection wiring and the Termux socket client remain IIS-003 through IIS-005.

## 14. Acceptance and stop conditions

Success requires:
- one canonical event contract and one linked measurement contract;
- one existing Neon project with append-only, idempotent normalized tables;
- bounded, transactional batch ingestion with durable receipts;
- explicit mapping for every adopted legacy source;
- no secret/raw prompt/raw completion ingestion;
- web/TUI/CLI projections reconcile to the same source range;
- measured backpressure, recovery and query performance;
- same-SHA validation and independent review.

Stop as `blocked` if the existing Neon project cannot be verified, schema migration permissions are absent, source identity cannot be mapped safely, or privacy validation cannot be established. Stop as `stagnated` if repeated iterations yield no measurable improvement. Do not create another database or scheduler to bypass a blocker.

## 15. References

- [Integration Adapter Contract](ADAPTER-CONTRACT.md)
- [Integration Event Schema](schemas/integration-event.schema.json)
- [Integration Measurement Schema](schemas/integration-measurement.schema.json)
- [Integration Batch Schema](schemas/integration-batch.schema.json)
- [Telemetry ingestion](../ops/TELEMETRY-INGEST.md)
- [Dashboard surface feeds](../ops/DASHBOARD-SURFACE-FEEDS.md)
- [Ratatui TestBackend](https://docs.rs/ratatui/latest/ratatui/backend/struct.TestBackend.html)
- [taria-ratatui 0.2.0](https://docs.rs/crate/taria-ratatui/0.2.0)
- [Tokio UnixListener](https://docs.rs/tokio/latest/tokio/net/struct.UnixListener.html)
