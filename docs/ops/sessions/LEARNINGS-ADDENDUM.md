# Session Learnings — Addendum

## The local-vs-master sync gap

**Symptom:** `gh_worktree action=create` from master returns a worktree
that does not contain files we've been editing locally. Agent sees "file
not found" for `deepagent.py` even though it exists at `~/deepcli/deepagent.py`.

**Root cause:** `deepagent.py`, `agent.py`, `session_store.py`, `_v1_*.py`,
and `logs_sync.py` were developed locally for many rounds and never
committed to master. `gh_worktree` only reflects what's on the remote branch.

**Fix:**
1. Verify before any worktree edit:
   `gh api repos/<owner>/<repo>/contents/<path>?ref=master --jq '.sha'`
   404 means the file isn't on master; worktree edits can't target it.
2. Land local core via a worktree PR (see agent/core-commit branch), merge,
   then pull the merged version back to `~/deepcli/` so local matches master.
3. After merging any PR that touches `deepcli/*`, pull the file(s) back:
   `curl -sS https://raw.githubusercontent.com/<repo>/master/deepcli/<file> -o ~/deepcli/<file>`

## Never use `{owner}/{repo}` literals in `gh api`

The `gh api` CLI does not template `{owner}` / `{repo}` — those are for
JS-style URL templates, not shell. Always pass the real slug:
`gh api repos/timerloggedout-spec/termux-monorepo/contents/...`

## The nested `deepcli/deepcli/` layout

- `~/deepcli/` — project root, contains `deepagent.py`, `agent.py`, `_v1_*.py`
- `~/deepcli/deepcli/` — Python package, contains `core.py`, `cli.py`, `organizer.py`

Any task targeting the agent loop wants the OUTER path. Any task targeting
`core.py` (the web-session client) wants the INNER path. Never conflate.

## Stale branches after a blocked run

When `gh_worktree action=create` fails on `branch already exists`, the local
branch survived a prior aborted run. Clean it:
```

git -C ~ branch -D <branch>
gh api repos/<owner>/<repo>/git/refs/heads/<branch> -X DELETE

```
Then retry.

## Never fabricate the target

When the agent can't find the file the task assumes, the right move is
`finish(validation="deferred")` with the exact evidence. That is what
our agent did — correct behavior. Do not create the file to satisfy
grep checks.

## This learnings mechanism is transitional

Hindsight supersedes static learnings files. This document exists until
the Hindsight integration lands (Phase 2/3 wiring of `_v1_hindsight.py`
into `deepagent.py`). After that, per-session knowledge is retained via
`hindsight_retain` and recalled via `hindsight_recall`.

## ForeSight lane

There is a ForeSight lane already deployed. We are operating in the NOW.
Future-state planning goes to ForeSight; current execution stays here.

## Hard rule: never use /tmp on Termux

There is no /tmp on Termux. Any script, command, or heredoc that writes to
/tmp silently fails or errors. This has bitten us three times.

Rule: all temp files go to `~/.deepcli/logs/` or `$TMPDIR` (= $PREFIX/tmp).
The precheck helper and every generated script enforces this.

Grep check for existing scripts:
  grep -rn '/tmp/' ~/.local/bin/ ~/deepcli/*.py 2>/dev/null | grep -v '$TMPDIR'

## Local Resource Hygiene is 1st Class

Mandatory before heavy operations:
  precheck <estimated_mb> <label>

Floor: 500 MB free. Estimated × 2 headroom. Memory sanity for >200 MB ops.

Wired into: servers-up, agent-keeper, tunnel-keeper-loop. Any future
script that installs, clones, compiles, or writes >100 MB must call precheck.

Periodic reporting:
  disk-report [--notify]

Runs every 100 keeper iterations (~8 min at full speed). Auto-notifies
on the `resource` channel with a 30-min throttle.

## Reclaimable without loss

- ~/.cache/uv, pip, node-gyp, go-build — pure caches, re-downloaded on demand
- ~/.deepcli/worktrees/* — merged PRs; keep only active ones
- ~/.git gc --aggressive — compact git objects

Never delete: ~/.deepcli/{session_store,refs,snapshots,logs,lib},
~/synthegration_exports (ML pipeline data), ~/.password-store, ~/.gnupg
