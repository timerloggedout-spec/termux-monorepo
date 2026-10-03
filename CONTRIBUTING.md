# Contributing

## Before touching anything

1. Read docs/STANDARDS/PROCESS/RECON-FIRST-WORKTREE-DISCIPLINE.md
2. Run `mvt-status` to see current state
3. If a background loop is running, never force any git operation

## Branch policy

Never delete a branch. Not merged, not closed, not conflicted.
Every branch is a training signal.

Forbidden:
- git branch -D
- git push origin --delete
- gh api -X DELETE .../git/refs/heads/*
- gh pr close --delete-branch
- git worktree remove --force

## Commit convention

Conventional Commits. Subject, blank line, body naming what changed,
why, and what it preserves.

Types: feat, fix, docs, chore, refactor, test, perf, build, ci.

## Worktree flow

Every multi-file change:

    git worktree add ~/.deepcli/worktrees/<branch> -b <branch> origin/<base>
    cd ~/.deepcli/worktrees/<branch>
    # edit, test, commit, push, open PR

Clean up only your own worktree.

## Tests

Every PR adds or updates at least one test in deepcli/tests/.

    python3 deepcli/tests/run.py

All tests must pass before a PR opens.

## PR review

Loop-produced PRs are candidates only. Sentinel reviews. Rollup
merges. No direct push to master.

## Credential hygiene

Never print tokens, keys, passwords, or passphrases.

## Hygiene commands

    reclaim-now                          # force a disk sweep
    touch ~/.deepcli/watchdog/reclaim.trigger   # same, async
    rm ~/.deepcli/watchdog/loop.paused          # resume paused loop

## Attribution

Every write is recorded in ~/.deepcli/logs/provenance.jsonl. To trace
a runtime failure to its author session:

    mvt-attribute <failing-session> <path> [<sha-at-failure>]
