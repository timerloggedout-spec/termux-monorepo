# docs/ops/sessions/

Per-invocation records for the DeepSeek Termux Agent. One file per task
hash. Populated by `logs_sync.py` and by `deepagent` finish handler.

## Layout

    sessions/
      README.md                     this file
      index.md                      generated index of all sessions
      <task-hash>/                  one dir per task identity
        meta.json                   {key, first_seen, last_used, runs, last_task}
        runs.jsonl                  append-only {ts, rc, elapsed_s, finish, tool_calls, validation, change_head, commit}
        latest.md                   human-readable latest summary

## Producer

- `deepagent.py` writes runs.jsonl on finish
- `logs_sync.py` upserts into the repo, reads from `~/.deepcli/sessions.json`

## Consumer

- `docs/ops/sessions/index.md` — read-only aggregator
- `python3 ~/deepcli/tools/metrics.py` — local, no repo needed
- `dashboards` lane (see issue #175 P1)
