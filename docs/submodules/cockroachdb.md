# CockroachDB reference and backend-mesh adapter

- **Upstream:** https://github.com/cockroachdb/cockroach
- **Observed upstream pin:** `d30c905fff79ef825adc96bcc647f1872a90f2ff` (GitHub commit search; 2026-09-23)
- **Intended reference target:** `refTemplates/smods/cockroachdb` (shallow gitlink admission pending)
- **Role:** distributed SQL reference for continuity, replicated state and PostgreSQL-wire interoperability.
- **Repository-native adapter:** `scripts/ops/cockroach_lane_event.py`
- **Schema:** `ops/cockroachdb/lane-events-schema.sql`
- **Status:** adapter implementation staged for PR validation; upstream gitlink promotion remains a separate source-pin operation requiring a Git tree update and dual-gate validation.

## Boundary

The upstream repository is reference material. Repository-owned code remains the runtime integration and canonical evidence contract. The CockroachDB projection mirrors the existing append-only `lane_events` identity using the same `event_key`; GitHub JSON/JSONL and immutable SHA/run provenance remain canonical.

## Connection contract

Configure the Actions secret `COCKROACH_DATABASE_URL` with a PostgreSQL-wire connection URI using `sslmode=verify-full` (preferred) or `sslmode=verify-ca`. The writer emits only credential names and status. Local insecure mode is available exclusively to the CI integration test with `CI=true` and `COCKROACH_ALLOW_INSECURE_TEST=1`.

Provision a dedicated database role with `SELECT, INSERT` on `lane_events`; grant schema usage and sequence privileges only where required. Keep `UPDATE` and `DELETE` outside the writer role. Run schema migration as a separately authorized owner role.

## Continuity semantics

- **Projection:** each event is independently inserted into CockroachDB using the canonical idempotency key.
- **Replay:** replay the source JSONL through the same writer; duplicate keys resolve through `ON CONFLICT DO NOTHING`.
- **Failure:** retain the canonical GitHub evidence and report the CockroachDB sink as skipped/degraded. The adapter does not silently redirect Neon traffic or claim cross-provider replication.
- **Promotion:** declare CockroachDB a tested continuity target only after a seeded canary survives a forced primary-path interruption and a restore/readback check.
