# lane_events ledger

Append-only Neon Postgres ledger with an optional CockroachDB continuity projection for the agentic planning lanes. Repository JSON + PR evidence remain authoritative for dependency phases.

| Piece | Path |
|---|---|
| Schema (idempotent, append-only trigger) | `ops/lane-events/schema.sql` |
| Insert (psql variables, ON CONFLICT DO NOTHING) | `ops/lane-events/insert.sql` |
| Writer (never fails caller) | `scripts/ops/lane_event.py` |
| Reusable step | `.github/actions/lane-event` |
| Wiring (help-wanted + SHE, via workflow_run) | `.github/workflows/lane-events-recorder.yml` |
| CockroachDB projection schema | `ops/cockroachdb/lane-events-schema.sql` |
| CockroachDB writer | `scripts/ops/cockroach_lane_event.py` |
| CockroachDB tests | `tests/test_cockroach_lane_event.py` |
| Tests | `tests/test_lane_event.py` |

Idempotency: `event_key = sha256(lane|workflow|run_id|run_attempt|subject|event_type)`
plus a unique index on `(run_id, run_attempt, coalesce(subject_url, phase_id, ''), event_type)`.

Credentials (repo secrets, names only): `LANE_EVENTS_DATABASE_URL` or `NEON_API_KEY` for Neon; `COCKROACH_DATABASE_URL` for the optional CockroachDB projection. The CockroachDB writer requires `sslmode=verify-full` or `verify-ca`. Each sink writes independently with the same canonical `event_key`; replay from source JSONL reconciles a partial write.

Use from any workflow (after `actions/checkout`):

```yaml
- uses: ./.github/actions/lane-event
  if: always()
  with:
    lane: cadence
    workflow: ${{ github.workflow }}
    run-id: ${{ github.run_id }}
    run-attempt: ${{ github.run_attempt }}
    conclusion: ${{ job.status }}
    database-url: ${{ secrets.LANE_EVENTS_DATABASE_URL }}
    neon-api-key: ${{ secrets.NEON_API_KEY }}
    cockroach-database-url: ${{ secrets.COCKROACH_DATABASE_URL }}
```

Readback: run `python3 scripts/ops/lane_event.py count` in an authorized local
environment with `LANE_EVENTS_DATABASE_URL` or `NEON_API_KEY`; the row count
appears as a `lane-events count` notice annotation. The recorder has no manual
Actions dispatch surface; production writes are driven by watched workflow-run
completion events.
