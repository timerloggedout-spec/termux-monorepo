# Backup events as Telemetry measurements

`[MUSEai]@{role:{hindsight-provenance}}` · Owner direction 2026-11-01:
VM workspace backup events are Telemetry **measurement records**,
correlatable with the monorepo commit stream like every other plane.

## Surfaces

| Surface | Owner | Role |
|---|---|---|
| `ops/tracking/backup-relays.jsonl` | Tracking lane (backup-state/v1) | source feed — the render source of record |
| `ops/telemetry/backup-measurements.jsonl` | this lane | measurement records (schema `backup-measurement/v1`), append-only |
| `ops/telemetry/backup-measurements-receipt.json` | this lane | counts receipt |

Telemetry READS the Tracking feed as intake; it never forks its numbers
(the feed stays the render source; coordination: Tracking lane chat).

## Record

`{schema, kind (export | export_failed | …), at, state_hash, export_id,
publish_commit + publish_repo (backup repo), relay_commit + relay_repo
(monorepo), join{by, relay_resolved, stream}, origin, evidence_hash}`

## Join

Each record joins the monorepo commit stream two ways: **by hash** —
`relay_commit` is the master commit that appended the source line
(append-commit resolution, oldest-first over the commits touching the
feed); **by time** — `at` is the event timestamp the relay carries.
`publish_commit` joins OUT to the backup repo's own stream for export
events (null on failed attempts, as recorded).

## Intake discipline

Immutable intake (DoE rule 8): a record is emitted once, keyed by
`evidence_hash` = sha256 of the canonical source line; re-runs are
idempotent and never rewrite history. Relay resolution happens at emit
time only — an unresolved record ships with `relay_resolved: false`
rather than being amended later.

## Backfill of record (2026-11-01)

9 records: 1 export (`exp-20261102T062322Z-65e231`, publish
`34a9dd16b5d9` in `timerloggedout-spec/muse-vm-workspace-backup`) +
8 `export_failed` attempts (the platform exec-write-denial window;
state_hash drifts between attempts because the workspace kept changing).
Relay-resolved 9/9. Live intake runs in `telemetry-ingest.yml`.
