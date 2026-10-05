# Hygiene & Reclaim Runbook — 20261004-013749

## Pause hygiene during heavy ops
    hygiene-pause 600            # 10 min
    hygiene-resume               # immediate
    hygiene-paused && echo yes

## Wrap a command
    hygiene-with-pause 3600 -- cargo build --release

## Memory/swap gate (auto-pauses hygiene)
    heavy-op 400 256 -- <cmd>

## Trigger reclaim now
    ~/.local/bin/reclaim-now trigger

## Pause token
File: ~/.deepcli/watchdog/hygiene.pause
Format: <epoch>\n<reason>
Auto-removed when expired. All hygiene scripts honor it.

## Conflict matrix
- hygiene-reclaim vs deepagent-continuous: RAM/IO race at 96% disk
- FIX: run heavy ops under heavy-op (pause + gate)
- Worktrees: git-clean only when no tracked edits in flight
- agent-keeper.log rotated if mtime >24h

## Agentic work policy
- NEVER `sv down hygiene`; use hygiene-pause
- NEVER kill deepagent mid-iteration; wait for boundary
- Worktrees are disposable artifacts; tracked edits are sacred
