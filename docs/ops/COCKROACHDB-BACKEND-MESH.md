# CockroachDB — Backend Mesh Integration and Continuity Contract

**Status:** IMPLEMENTATION SLICE — native writer + CI integration test; hosted-cluster admission pending an owner-managed connection secret and a forced continuity drill.

## Decision

Use CockroachDB as an independently operated distributed-SQL continuity projection for the existing lane-events evidence stream. Preserve the current Neon route and the canonical repository evidence spine. Keep each provider independently addressable and observable.

CockroachDB speaks the PostgreSQL wire protocol and supports most PostgreSQL syntax. Its default transaction isolation is SERIALIZABLE, and application clients must handle retryable SQLSTATE `40001` where multi-statement transactions require client-side retry. This integration uses single-statement idempotent inserts, reducing the retry surface.

## Mesh topology

```text
Canonical GitHub JSONL + immutable SHA/run provenance
                    |
                    v
          lane-event composite action
             /                 \
            v                   v
       Neon projection     CockroachDB projection
       existing writer      new native writer
            |                   |
            +---------+---------+
                      v
              continuity receipts
         {sink, status, event_key, run_id}
```

The providers remain independent stores. A CockroachDB write does not imply Neon replication, and a Neon write does not imply CockroachDB replication. The source JSONL and event keys support deterministic replay into either sink.

## Runtime surface

| Surface | Path | Function |
|---|---|---|
| CockroachDB schema | `ops/cockroachdb/lane-events-schema.sql` | Idempotent table/index creation |
| CockroachDB insert | `ops/cockroachdb/lane-events-insert.sql` | Append event by canonical event key |
| Writer grants | `ops/cockroachdb/lane-events-writer-grants.sql` | Isolated database and least-privilege runtime identity |
| Writer | `scripts/ops/cockroach_lane_event.py` | TLS-verified connection, schema, record and count |
| Tests | `tests/test_cockroach_lane_event.py` | URI security, canonical event identity, explicit skip |
| Reference record | `docs/submodules/cockroachdb.md` | Upstream provenance and submodule admission boundary |

## Admission and health states

- `UNCONFIGURED`: `COCKROACH_DATABASE_URL` is absent; the optional sink emits a skip notice.
- `READY`: TLS-verified connection succeeds and schema/read/write/readback probes pass.
- `DEGRADED`: connection, schema or insert probe fails; canonical GitHub evidence remains authoritative.
- `CONTINUITY_TESTED`: the canary has been read back after a forced failure of the primary path, with a receipt containing source SHA, event key, timestamps and observed result.

## RPO / RTO evidence

Record observed values from drills. The design target is an independently replayable event projection; measured RPO/RTO remain `null` until a real test produces timestamps and readback evidence. A second provider name alone earns no continuity credit.

## Security and operations

1. Run `ops/cockroachdb/lane-events-writer-grants.sql` with the cluster administrator to create `lane_events_writer` for runtime inserts and `lane_events_migrator` for schema DDL.
2. Apply the versioned schema with a migration identity through `COCKROACH_SCHEMA_DATABASE_URL`.
3. Store the dedicated writer URI only as the Actions secret `COCKROACH_DATABASE_URL`.
4. Use `sslmode=verify-full` or `verify-ca` for hosted clusters.
5. Keep the runtime role on SELECT/INSERT; reserve DDL, UPDATE and DELETE for the migration owner.
6. Replay from canonical JSONL using the existing event key.
7. Capture sink outcome and run identity in workflow logs and receipts.
8. Run a restore drill before assigning a production continuity grade.

## Validation

The dedicated workflow runs two disposable contracts. The adapter contract starts a TLS-secured single-node cluster, provisions the least-privilege writer, applies the schema, verifies insert/readback, checks UPDATE/DELETE denial and runs offline unit tests. The replicated-continuity contract starts three TLS-secured nodes, writes through node one, verifies node-two readback, stops node one, verifies continuity through node two, then backs up, drops and restores the lane-events database from node-local test storage. This exercises one-node failure tolerance and database restore in an ephemeral cluster; hosted multi-region availability and external-storage disaster recovery remain separate drills.

## Upstream references

- https://www.cockroachlabs.com/docs/stable/developer-basics.html
- https://www.cockroachlabs.com/docs/stable/architecture/overview.html
- https://github.com/cockroachdb/cockroach
