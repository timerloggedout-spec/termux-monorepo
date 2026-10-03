# Operating model

## Layers

    Model     DeepSeek          the LLM (chat or API)
    Process   deepagent         one loop, one task, one session
    Roles     recon, plan, forge, sentinel, rollup, hygienist, scribe, orchestrator
    Skills    recon-first-worktree-discipline, hindsight-memory-architect, find-skills, termux-hygiene
    Accounts  primary, account-2 (symmetric)

## Roles

- recon       read-only inventory before action
- plan        produce PLAN.md, no edits
- forge       worktree, edits, tests, PR
- sentinel    PR verdict: CLEAN, DIRTY, BLOCKED, LOOP
- rollup      squash-merge, never delete branches
- hygienist   reclaim, prune
- scribe      journal, doctrine
- orchestrator  sequences the rest

## Invariants

- Nothing deleted. Branch retention is absolute.
- Every role logs. No silent actions.
- Roles are modes, not identities.

## Services

| Service                   | Interval   | Purpose |
|---------------------------|------------|---------|
| hygiene-watchdog          | 30s        | mem/boot/cpu sample |
| hygiene-reclaim           | 6h         | reclaim caches |
| hygiene-reclaim-trigger   | 10s poll   | on-demand reclaim via marker |
| loop-guard                | 60s        | pause on failure cascade |
| mvt-refresh               | 15s        | API poll, cache refresh |
| mvt-watchlog              | 5s         | increment log on count change |

## Task files

Every task file carries:

    # REVIEW REQUIRED — first iteration produces PLAN.md

    (or)

    # Task: <name>

    ## Steps
    1. read_file ...
    2. gh_worktree create ...
    3. edit ...
    4. run tests
    5. gh_worktree commit_push_pr
    6. finish with summary

The gate prefix decides the role: gated tasks produce PLAN.md first;
ungated tasks execute.

## Attribution

Every write to a file is journaled to
~/.deepcli/logs/provenance.jsonl with before/after shas, author
session, tool, and commit. When a runtime failure appears, walk the
ledger back to the author.

    mvt-attribute <failing-session> <path> [<sha-at-failure>]
