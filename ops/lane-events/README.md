# lane_events ledger

Append-only Neon Postgres ledger for the agentic planning lanes. It replaces
expiring artifacts and master-pushed status JSON as the durable record; repo
JSON + PR evidence stay authoritative for dependency phases.

| Piece | Path |
|---|---|
| Schema (idempotent, append-only trigger) | `ops/lane-events/schema.sql` |
| Insert (psql variables, ON CONFLICT DO NOTHING) | `ops/lane-events/insert.sql` |
| Writer (never fails caller) | `scripts/ops/lane_event.py` |
| Reusable step | `.github/actions/lane-event` |
| Wiring (help-wanted + SHE, via workflow_run) | `.github/workflows/lane-events-recorder.yml` |
| Tests | `tests/test_lane_event.py` |

Idempotency: `event_key = sha256(lane|workflow|run_id|run_attempt|subject|event_type)`
plus a unique index on `(run_id, run_attempt, coalesce(subject_url, phase_id, ''), event_type)`.

Credentials (repo secrets, names only): `LANE_EVENTS_DATABASE_URL`, or `NEON_API_KEY`
(the writer then finds/creates Neon project `lane-events` in `aws-us-east-2`, a
Neon Realtime region, on the free tier). With neither set every call is a no-op notice.

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
```

Readback: run `lane events recorder` with `workflow_dispatch` command `count`; the
row count appears as a `lane-events count` notice annotation.
