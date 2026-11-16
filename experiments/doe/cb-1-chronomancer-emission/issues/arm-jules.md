<!-- campaign: cb-1-chronomancer-emission | arm: arm-jules | framing: live-1 A-implement-only (held) -->
<!-- Route: apply label `jules` after creation. Stamp sha256[:12] of this title+body in the campaign record at dispatch. -->

**Implement** a ChronoMancer record emitter in `scripts/doe/chronomancer_emitter.py`, with tests in `tests/test_chronomancer_emitter.py`. Change NO other files.

- **Target:** `run_history` SQLite DBs written by `harmony_hub/workspace/agent/chronomancer.py` (read it on master first). Its schema: `session_id, account, timestamp, validated, target_file, attempt_number, patch_content, verdict`. Fork rows are inserted with `target_file='chronomancer-fork'`, `verdict='time_loop'`, `validated=1`, and `session_id` = the NEW forked session id.
- **Outcome:** running the emitter over such a DB produces one EXPERIMENT record (per `docs/ops/corpus/EXPERIMENT.schema.json`) per fork event plus one per continuation, deterministically.
- **Contract:**
  - CLI: `chronomancer_emitter.py <db_path> <out_dir> --baseline-sha <40-hex>`; open the DB read-only (sqlite URI `mode=ro`); never write to it.
  - Scan `run_history` ordered by `(timestamp, rowid)`. For each fork row emit a FORK record. Its CONTINUATION is the earliest later row with `session_id` = the fork row's `session_id` and `target_file != 'chronomancer-fork'`; if one exists emit a paired CONTINUATION record; if none, the fork record carries `pairing=pending` and no continuation is invented.
  - Record fields: `schema_version` "1.0"; `suite` "doe-family:cb-1-chronomancer-emission"; `cohort` = account; `experiment_id` = `cb1-chrono-<fork rowid>-fork` / `-cont`; `observed_at` = the source row's timestamp normalized to ISO-8601 UTC (source-derived, never wall-clock); `baseline_sha` = `candidate_sha` = the `--baseline-sha` argument; `treatment.manager_policy_id` = "chronomancer/time-loop-fork"; `treatment.arm` = "fork" | "continuation"; `treatment.instance` = null; `status` = "observed"; `provenance` = "other"; `confidence` = "medium".
  - `metrics`: `pair_id` = `cb1-pair-<fork rowid>` (shared by the pair), `session_id`, `account`, `verdict`, `source_rowid`, `fork_policy` = "NOT ESTABLISHED", `injected_summary_sha256` = "NOT ESTABLISHED".
  - Output: one JSON file per record in `<out_dir>`, canonical JSON (sorted keys, fixed separators), filename = `<experiment_id>.json`.
  - Stdlib only (sqlite3/json). Do NOT import `chronomancer.py` or deepcli. No network.
- **Tests:** build a fixture DB in a tmp dir with at least: 2 fork rows each followed by a continuation row for the forked session, 1 fork row with no continuation, and >=2 non-fork rows that are not continuations. Assert: exactly 5 records; every record validates against `docs/ops/corpus/EXPERIMENT.schema.json`; pairing exact (no orphan continuations); a second run produces byte-identical files; the fixture DB hash is unchanged by the run.
- **Scope:** only the two files named above.
- **Acceptance evidence:** report the test command and its exact output, the changed paths, remaining risks, anything not verified.
- **Stop / escalation:** stop + explain if the change crosses the stated scope or an approval boundary.
