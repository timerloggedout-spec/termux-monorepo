# Agent roles

Seven modes. Each triggered by context, not by identity. Either
account (primary / account-2) can hold any role.

| # | Role | Moniker | Trigger | Output |
|---|---|---|---|---|
| 1 | Pathfinder | `recon`     | unfamiliar state         | read-only inventory |
| 2 | Architect  | `plan`      | REVIEW REQUIRED gate     | PLAN.md, no edits |
| 3 | Builder    | `forge`     | second dispatch          | worktree + tests + PR |
| 4 | Critic     | `sentinel`  | PR before merge          | CLEAN/DIRTY/BLOCKED/LOOP |
| 5 | Merger     | `rollup`    | Critic returns CLEAN     | squash-merge |
| 6 | Hygienist  | `🪥`        | floor breach or trigger  | reclaim, prune |
| 7 | Chronicler | `scribe`    | post-run                 | tags, events, doctrine |

## Invariants

- **Nothing deleted.** Branch retention is absolute
  (`BRANCH-RETENTION.md`).
- **Every role logs.** No silent action.
- **Roles are modes, not identities.** `deepagent.py` selects role by
  the task file's gate header, the caller's flags, or the workflow's
  dispatch name.

## Session resume vs fresh — accountability

Every `loop()` call writes one line to
`~/.deepcli/logs/hygiene/session-decisions.jsonl`:

    {"ts": ..., "key": "...", "sid": "...", "decision": "resume|fresh",
     "reason": "cached|forced|no-key", "task": "...", "role": "..."}

The resume decision is deterministic from `session_store.task_key`
(content hash of the task + path). `--fresh` forces the fresh path.
