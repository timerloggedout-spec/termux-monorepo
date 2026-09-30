# Retrospective — 2026-09-30 sweep cascade

**Incident:** ~4 hours of perceived data loss, GPG keyring loss, 20-minute
scans, three codespace recreations, self-bypassed commits.

**Root:** Zero blast-radius discipline on destructive commands, plus a repo
whose root IS $HOME.

## The cascade — 10 triggers

1. `git stash push -u` at `~/` — swept every untracked file in HOME
2. No vault existed — zero rollback capability
3. `grep -c PAT || echo 0` — arithmetic test aborted recovery loop
4. `detect-secrets` on 2660 files — 16 min GIL-bound wall
5. devcontainer on `python:3.12` — DinD fails, docker missing
6. `git -c core.hooksPath=/dev/null` — every commit bypassed hooks
7. Codespace create without `-b` — all cells on master
8. Hindsight retain without quota check — 402 wall mid-harvest
9. DeepAgent kimi-recon ran 5x — never completed, no DoD
10. No codespace inventory before create — 5 cells, 4 idle

## How each was avoidable FROM THE START

### 1 · Pre-flight over post-mortem
**DO** print target list before any `-u`, `-r`, `--force`, `-A` flag.
**DO** refuse destructive verbs when cwd == `$HOME`.
**DO** require `--confirm` on wrappers for delete-class.
**DO** dry-run commands touching > 50 files.

### 2 · Own the boundary
Repo root == `$HOME` means home-wide blast radius.
**DO** use worktrees for every non-trivial task.
**DO** path-spec every git verb; never `-A`, never stash at root.

### 3 · Establish vault before mutation
**DO** vault snap is step zero of any session touching creds/configs/keys.

### 4 · Size-bound every scan
**DO** K > 200 files dispatches to CI. Device does staged-diff only.
**DO** exclude `.git`, models, exports, caches.

### 5 · Verify tool before tool runs
**DO** validate `devcontainer.json` with `devcontainer up --workspace-folder .`
before remote create. Feature logs first, assumptions never.

### 6 · Hooks are load-bearing
**DO** never bypass `commit-msg` or `pre-commit`.
**DO** log every exception to `docs/STANDARDS/EXCEPTIONS.md`.

### 7 · Codespace config is code
**DO** every codespace create goes through `cs-hindsight create` wrapper.

### 8 · Quota before write
**DO** any paid-API write path checks remaining balance first.

### 9 · Agent tasks need DoD
**DO** every agent task has deliverable + max_steps + completion predicate.

### 10 · Codespace inventory before create
**DO** `cs-hs status` before `cs-hs create`. Reuse stopped cells first.

## Trunk evaluation

**Short-lived lanes** — feat/N lives 1-3 days, rebased daily, pushed every
commit, merged fast, branch+worktree deleted same day.

| Anti-pattern | Trunk-correct |
|---|---|
| 1221-ahead branch | rebase + squash within 3 days |
| 5 worktrees, 2 unpushed | 1 worktree per active task, PR-open |
| 10 commits ahead of origin | push after every commit |
| stale worktree 15 days | auto-prune at PR merge |

## DO Framework extensions §9-§14

- **§9 Blast-radius** — print targets; refuse at HOME; confirm on delete
- **§10 Pre-flight** — verify tools, quotas, counts, inventory
- **§11 Trunk** — rebase daily; push always; remove at merge; cap 2 worktrees
- **§12 State** — vault-first; verify weekly; log every op
- **§13 Hook** — run hooks; never bypass; log exceptions; weekly proof-fire
- **§14 Boundary** — HOME is a minefield; path-spec; subdir for destructive

## What went RIGHT

- Git objects persist — zero bytes lost, all recoverable
- Vault created mid-incident — caught second wave
- `git-stash-safe` guard installed
- Recovery improvised but effective
- Doctrine written into standards

**Meta-lesson:** the vault existed *because* the incident happened.
Correct order is the reverse — vault first, then work.

## First principles

| Principle | Application |
|---|---|
| Blast radius | Print targets; refuse cwd==HOME; cap 50 files |
| Tool verify | Version + feature logs + local dry-run |
| Resource inventory | Count codespaces, credits, disk first |
| State protocol | Vault before mutation; verify restore after |
| Trunk discipline | Rebase daily; push always; kill at merge |
| Hook integrity | No bypass; log exceptions; weekly proof-fire |
| Boundary | HOME is a minefield; path-spec every git verb |

**Perfect RECON:** inventory → classify → plan → verify → execute → verify → log
**Perfect Trunk:** short lane → rebase daily → push always → merge fast →
delete branch+worktree same day → snapshot trunk
