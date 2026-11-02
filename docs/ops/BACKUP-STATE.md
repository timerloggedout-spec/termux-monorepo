# BACKUP-STATE — the dashboard records the backups (backup-state/v1)

Owner order (2026-11-01, via main): the dashboard records the backups.
Tracking lane owns the record. **Metadata only** — export history
{id · at · T0/T1 counts · state hash}, drill verdicts, and the current
marker. Never file paths, never manifest content, never backup content.

## The record

| Piece | Path |
|---|---|
| Canonical record | `ops/tracking/backup-state.json` (`backup-state/v1`) |
| Dashboard twin | `apps/help-wanted-dashboard/data/backup-state-feed.json` (byte-identical; pages consume the twin only) |
| Generator | `scripts/tracking/backup_state.py` (offline; committed sources only) |
| Single-writer | `.github/workflows/repo-tracking-collect.yml` (same writer as the tracking surface) |
| Tests | `tests/test_backup_state.py` |

## Schema (backup-state/v1)

```
{
  schema: "backup-state/v1",
  generated_at, generated_by,
  spec: {doc, metadata_only},
  sources: [{id: relays, path, records}, {id: snapshot, path, status, read_at}],
  marker: {state_hash, export_id, source},   // the last-export fingerprint
  exports: [{id, at, t0, t1, manifest_only, excluded, bytes,
             gates_pass, publish_commit, state_hash}],   // newest first
  failed_attempts: [{export_id, at, state_hash, reason}],  // relayed
                                                 // kind=export_failed; state_hash =
                                                 // the unexported state; never
                                                 // move the marker
  drills: [{report, export_id, verdict,
            t0: {checked, mismatched, excluded_absent},
            t1: {checked, consistent, missing},
            restored_bytes, mode}],
  summary: {exports, drills, last_export_at, last_export_id,
            last_drill_verdict},
  gaps: [..],
}
```

## Sources

1. `relays` — `ops/tracking/backup-relays.jsonl`: export outcomes
   relayed from the hook runs that perform the exports (the
   `vm-backup-state-watch` cadence). One JSON object per line:
   `{kind: "export", export_id, at, publish_commit, state_hash}` —
   plus `{kind: "export_failed", export_id, at, reason}` for failed
   attempts (the hook wiring of record, 2026-11-01): failed attempts
   surface in `failed_attempts[]` and never move the marker.
   The state hash and the marker live VM-side (the exporter's
   stat-only T0 fingerprint, `ops/vm-backup/state_hash.py`); relays
   are the only channel that carries them into the record. The marker
   = the newest relay's state hash.
2. `snapshot` — `scripts/tracking/backup_snapshot.json`: stamped,
   fail-soft API extract of the private backup repo
   (`timerloggedout-spec/muse-vm-workspace-backup`) written by
   `fetch_snapshots.py`: EXPORT.json counts/gates (the 18MB manifest
   is never read), `reports/*.json` drill verdicts, and export/drill
   commit subjects (commit rows seed history rows for exports whose
   EXPORT.json has since been overwritten — EXPORT.json holds only the
   latest export). A failed refresh preserves last-good data and
   records its status; the generator names staleness in `gaps[]`.

Merge rule: exports are keyed by `export_id`; every source fills only
fields the others left null. Verdicts and counts are the sources' own,
verbatim (a drill verdict of `fail` is recorded as recorded — the
2026-11-01 drill's T1 leg read 46,773/46,774 consistent, a live-source
append during the drill: drift, not defect; the record carries the
verdict and the leg counts, readers judge).

## Rules

- **Metadata only.** Counts, hashes, verdicts, timestamps, commit
  SHAs. No paths from the backup, no manifest rows, no content.
- **Single-writer.** Only `repo-tracking-collect.yml` writes the
  record + twin. Relays are appended by the hook-run lane through its
  normal commit route; lanes never hand-edit the outputs.
