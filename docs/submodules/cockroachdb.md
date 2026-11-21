# CockroachDB reference and backend-mesh adapter

- **Upstream:** https://github.com/cockroachdb/cockroach
- **Observed upstream pin:** `d30c905fff79ef825adc96bcc647f1872a90f2ff` (GitHub commit search; 2026-09-23)
- **Reference target:** `refTemplates/smods/cockroachdb` (shallow gitlink pinned to `d30c905fff79ef825adc96bcc647f1872a90f2ff`)
- **Role:** distributed SQL reference for continuity, replicated state and PostgreSQL-wire interoperability.
- **Repository-native adapter:** `scripts/ops/cockroach_lane_event.py`
- **Schema:** `ops/cockroachdb/lane-events-schema.sql`
- **Status:** upstream CockroachDB is pinned as a shallow submodule; repository-native adapter remains independently maintained and is validated through the CockroachDB contract workflow.

## Boundary

The upstream repository is reference material. Repository-owned code remains the runtime integration and canonical evidence contract. The CockroachDB projection mirrors the existing append-only `lane_events` identity using the same `event_key`; GitHub JSON/JSONL and immutable SHA/run provenance remain canonical.

## Connection contract

Configure the Actions secret `COCKROACH_DATABASE_URL` with a PostgreSQL-wire connection URI using `sslmode=verify-full` (preferred) or `sslmode=verify-ca`. The writer emits only credential names and status. Local insecure mode is available exclusively to the CI integration test with `CI=true` and `COCKROACH_ALLOW_INSECURE_TEST=1`.

Run `ops/cockroachdb/lane-events-writer-grants.sql` as a cluster administrator. It creates the isolated `lane_events` database and `lane_events_writer` login, removes default PUBLIC access, and grants the writer `CONNECT`, schema `USAGE`, and table `SELECT, INSERT` with matching default privileges. Apply `ops/cockroachdb/lane-events-schema.sql` through `COCKROACH_SCHEMA_DATABASE_URL` using a migration identity. Set the runtime Actions secret `COCKROACH_DATABASE_URL` to the dedicated writer identity. The writer role receives no `UPDATE`, `DELETE`, or DDL grants.

## Continuity semantics

- **Projection:** each event is independently inserted into CockroachDB using the canonical idempotency key.
- **Replay:** replay the source JSONL through the same writer; duplicate keys resolve through `ON CONFLICT DO NOTHING`.
- **Failure:** retain the canonical GitHub evidence and report the CockroachDB sink as skipped/degraded. The adapter does not silently redirect Neon traffic or claim cross-provider replication.
- **Promotion:** declare CockroachDB a tested continuity target only after a seeded canary survives a forced primary-path interruption and a restore/readback check.
