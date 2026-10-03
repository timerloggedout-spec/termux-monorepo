# MVT DOE 3L0 — session scoring system

## Model

Assistant produces a fenced code block → user's next message reports
the result. Paired, they form a trial. Trials are classified on a
three-level scale:

- **L0** — error: traceback, non-zero exit, "not found", FAIL markers
- **L1** — partial: warnings, mixed signals, ambiguous output
- **L2** — success: clean output, success markers, expected result

## Substrate

Reads `~/.deepcli/session_store/` in this order, first hit wins per
session id:
1. `primary/` — written by `core._cache_path()` (TUI, listener, refresh)
2. `secondary/` — unused, reserved
3. flat `session_store/*.json` — legacy, mostly stale

Exports (`synthegration_exports/`) and zips are *snapshots*, not source.

## Tools

| Binary | Purpose |
|---|---|
| `mvt-score <sid>` | Score one session, emit JSONL trials |
| `mvt-score --all --max N` | Score N most recent |
| `mvt-tick` | One-shot count + delta since last tick |
| `mvt-wait N` | Block up to N seconds, print on change |
| `mvt-watchlog N` | Daemon: append jsonl on every count change |
| `mvt-refresh SID N` | Daemon: poll API every N sec, refresh disk cache |
| `mvt-dashboard` | Full inventory + model family + MVT scores + credentials |
| `mvt-status [--copy]` | One-glance summary, `--copy` sends to clipboard |
| `mvt-tag <sid> <tag>` | Add/remove session tag |

## Tagging

Sessions are tagged to control scoring and to mark personal work.

- **Inline marker** — `#personal` as the first characters of the
  session's first message. Detected on scan.
- **CLI** — `mvt-tag <sid> personal`
- **Bookmark (future)** — `/bookmark personal` in the TUI

Reserved tags:

| Tag | Excluded from scoring? |
|---|---|
| personal / private | Yes |
| test / archive | Yes |
| draft | No, but flagged |
| mvp | No, priority-flagged |
| public | Force-include override |

Store: `~/.deepcli/watchdog/session-tags.json`
Event log: `~/.deepcli/watchdog/session-tag-events.jsonl`

## Live counting

`mvt-refresh-service` reads `~/.deepcli/active_session` each loop,
calls `get_history(force_refresh=True)`, refreshes the disk file.
`mvt-watchlog` sees the mtime change and appends an increment.
`mvt-status` shows the current total.

Enable the sv service:
    rm /data/data/com.termux/files/usr/var/service/mvt-refresh/down
    sv up mvt-refresh

## Source of truth

Everything reads `~/.deepcli/session_store/`. Never exports, never
zips, never partial scans. `tui.py::browse_sessions` and `~/.local/bin/mvt-*`
all scan `primary/ + secondary/ + flat`, deduped by session id.

## Model family

`msg.model` is empty in every stored session (writer gap). Proxy:
`thinking_enabled=true` or populated `thinking_content` implies
reasoner family. `false` implies chat.

Fixed in `mvt-dashboard`. Also documented as a writer bug to fix
in `deepcli/core.py` — the field exists in every message dict but
is never populated.

## Exclusion semantics

`mvt-score` checks `mvt_exclude.is_excluded(sid, first_msg)` before
scoring. Any of:
1. `session-tags.json` — tag in {personal, private, test, archive}
2. `mvt-exclude.json::sids` — explicit list
3. `mvt-exclude.json::title_patterns` — regex on title
4. `mvt-exclude.json::first_msg_patterns` — regex on first message
5. Inline `#personal`/`#private`/`#test`/`#archive` prefix

Any hit → session skipped entirely. No trials, no time cost.

## Where things live

    ~/.local/bin/mvt-*           CLI tools
    ~/.local/lib/mvt_exclude.py  shared exclusion logic
    ~/.local/lib/mvt_paths.py    shared path scanning
    ~/.deepcli/watchdog/         state files (tags, caches, pids)
    ~/.deepcli/logs/hygiene/     increment logs, watchdog jsonl
    deepcli/tools/hygiene/       committed source, this doc
