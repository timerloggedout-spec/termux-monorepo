---
description: Undo the most recent /one-shot --apply mutation. Restores .osp.bak files, git-stashes uncommitted work first, asks before reverting migrations. Spawns the rollback agent to execute. Safe — never edits beyond what the last session mutated.
argument-hint: "[--session-id <id>] [--keep-stash]"
allowed-tools: Read, Bash, Edit, Task
destructive: true
read-only: false
---

Invoke the **rollback** agent:

/one-shot-prompting:rollback $ARGUMENTS

The rollback agent reads `.beads/sessions.jsonl` for the last entry's
wire-stage paths, `git stash`-es uncommitted work first, restores
`.osp.bak` files, removes generated directories. Migration reverts
require explicit user yes.

Default: rolls back the most recent session. Pass `--session-id` to
target a specific one.
