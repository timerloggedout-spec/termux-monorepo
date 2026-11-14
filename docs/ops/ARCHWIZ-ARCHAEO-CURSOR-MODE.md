# Archaeo cursor mode — spec for the context_relationships publisher

Status: SPEC (archwiz-recon lane, 2026-11-01). Lands as a PR on the existing
context-relationship publisher; **no new tool** is created. The collector
leg (honouring the cursor inside `github_collector.py`) is the follow-on
implementation item for the context_relationships owner; until it lands,
the cursor is carried as workflow input + env and the publisher behaves
exactly as today (full bounded reconciliation).

## Why

`archwiz/archaeo_sweep.py` + `workspace/llm_map/archaeologist.py` implement
incremental provenance scanning on device: per-file mtime state
(`archwiz/archaeo_state.json`) plus a metadata epoch — re-scan only what
changed, and re-scan everything when a metadata source moves. The concept
is sound; the universe (device-home state files, cli-synthegration
provenance) is not. The repo-side descendant already exists:
`archwiz/context_relationships/` + `.github/workflows/context-relationship-*.yml`.
What it lacks is archaeo's increment semantics as a first-class, committed
cursor. This spec adds exactly that.

## Cursor

State file (committed, single-writer = the publisher workflow):

```
workspace/llm_map/context_relationships/cursor.json
{
  "schema": "context-relationships-cursor/v1",
  "last_commit_sha": "<master head at last successful publish>",
  "last_run_at": "<ISO, from the run's HEAD commit time>",
  "metadata_epoch": "<sha256 of sorted (path, blob) pairs of the metadata
                      sources below, truncated to 16 hex>",
  "items_seen": {"issues": 0, "pull_requests": 0, "commits": 0}
}
```

Metadata sources (epoch inputs — the repo analogs of archaeo's
METADATA_FILES): the collector's own config surfaces —
`archwiz/context_relationships/**` non-output files and
`scripts/ci/context_relationship_index.py`. Any change ⇒ epoch moves ⇒
next run is a full reconciliation regardless of cursor age.

## Semantics

1. Run starts: read cursor. Missing/corrupt ⇒ full build, cursor created.
2. `full_refresh: true` (existing input) ⇒ ignore cursor for this run;
   cursor still advances on success.
3. Incremental run: collect only items whose `updated_at` is after
   `last_run_at` (issues/PRs) and commits after `last_commit_sha`;
   merge into the existing index (upsert by stable id), never rebuild
   from zero.
4. Epoch moved ⇒ full build (metadata change can reinterpret old items —
   archaeo's rule).
5. Cursor advances **only** after the publish commit succeeds; a failed
   run leaves the cursor untouched, so the next run re-covers the window
   (at-least-once, upserts make it idempotent).
6. Bounds stay: `max_items` / `max_commits` inputs still cap a run; a
   capped incremental run must NOT advance the cursor past un-collected
   items — it records the oldest un-collected `updated_at` as the next
   window edge instead.

## Workflow delta (this PR)

- `workflow_dispatch` gains input `cursor_mode` (choice: `incremental` |
  `full`, default `incremental`); `full_refresh: true` implies `full`.
- The build step receives env `CONTEXT_CURSOR_MODE` and
  `CONTEXT_CURSOR_FILE` (the state path above). Until the collector leg
  lands, the collector ignores the env — behaviour unchanged, contract
  visible in the workflow.
- A header comment on the workflow points here.

## Non-goals

- No new workflow, script, or schedule.
- No change to the index schema or outputs.
- No device-state import: `archwiz/archaeo_state.json` (committed device
  state) is not migrated; the cursor starts fresh.
