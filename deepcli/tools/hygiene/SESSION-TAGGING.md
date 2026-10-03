# Session tagging — MVT exclusion and annotation

Sessions carry tags that change how MVT DOE 3L0 treats them.

## Tag vocabulary

| Tag | Meaning | Effect |
|---|---|---|
| `personal` | Private — user's own chat, not a test | Excluded from MVT scoring |
| `private` | Alias for personal | Excluded |
| `test` | Test run, do not score | Excluded |
| `archive` | Old, no re-scan | Excluded |
| `draft` | WIP, may be scored later | Scored + flagged |
| `mvp` | Reference candidate | Scored with priority |

## Three ways to apply a tag

### 1. Inline marker in first message

Sessions where the *first* message begins with a marker are tagged on scan:

    #personal   this chat is private
    #test       dry run, don't score
    #draft      WIP
    #archive    old
    #mvp        reference candidate

Markers are only detected on the first message. Adding `#personal` at
message 50 does not retag — use method 2 or 3.

### 2. Retroactive via CLI

    mvt-tag <sid> personal          # add tag
    mvt-tag <sid> -personal         # remove tag
    mvt-tag <sid> personal mvp      # multiple
    mvt-tag list                    # all tagged sessions
    mvt-tag list personal           # sessions with that tag
    mvt-tag markers                 # show marker patterns

### 3. Via TUI bookmark (planned)

`/bookmark personal` in the TUI will write a bookmark AND apply the tag
to the session. Format documented in `~/.deepcli/watchdog/BOOKMARK-FORMAT.md`.
Requires a `tui.py` patch — not yet shipped.

## Storage

- `~/.deepcli/watchdog/session-tags.json` — current state, one entry per sid
- `~/.deepcli/watchdog/session-tag-events.jsonl` — append-only event log
- `~/.deepcli/watchdog/mvt-exclude.json` — pattern-based fallback

## How mvt-score applies tags

At the top of `score_session()`, after loading the first message:

    if mvt_exclude.is_excluded(sid, first_msg_content):
        return []

The `is_excluded()` check reads:
1. `session-tags.json` — any of {personal, private, test, archive}
2. `mvt-exclude.json::sids` — explicit SID blacklist
3. `mvt-exclude.json::title_patterns` — regex on conversation title
4. `mvt-exclude.json::first_msg_patterns` — regex on first message
5. Inline `#personal` / `#private` / `#test` / `#archive` prefix

Any hit → session is skipped entirely. No trials emitted, no time cost.

## Scope-change semantics

Session-level tag wins. Mid-session markers append an event but do not
retroactively retag. Per-message exceptions belong in bookmarks (see
BOOKMARK-FORMAT.md), not tags.

## Auto-scan

`~/.local/bin/mvt-tag-scan` (or run manually) walks all sessions,
detects markers in first messages, and persists them with
`source="auto-marker"`. Run after importing new sessions.
