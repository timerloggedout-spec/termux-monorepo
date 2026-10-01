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

---

## Addendum · DinD in Codespaces is a wall

**Finding:** GitHub Codespaces outer container lacks `CAP_SYS_ADMIN`. The
`unshare` syscall is blocked by seccomp. Docker can pull images but cannot
register layers (`unshare: operation not permitted`).

**Why the devcontainer `docker-in-docker:2` feature works:** it configures
the codespace itself with elevated capabilities (`--privileged`-equivalent
runArgs) at *creation time*. A manually-started dockerd inside a non-feature
codespace cannot cross this boundary.

**Verified on:** Alpine 3.23 outer container, dockerd 29.5.2, vfs storage
driver, `iptables: false`, `bridge: none`. All the daemon-level flags that
work on bare metal — none of them bypass the seccomp filter on `unshare`.

**Correct pattern:** run the target service as a **direct process** in the
codespace (Python venv, Node, Go binary). Skip Docker entirely. The codespace
becomes a leased compute cell for the process, not a container host.

**DO** treat Docker-in-Codespaces as opt-in via the official feature only.
**DO NOT** start dockerd manually and expect `docker run` to succeed.

## Addendum · Codespaces prebuild fallback

GitHub Codespaces falls back to a **previous prebuild** when the new
devcontainer config fails to build. This silently serves the old image.

Confirmed: `.devcontainer/devcontainer.json` said `FROM base:ubuntu`, but
new codespaces landed on Alpine 3.23 (musl). Alpine has no musllinux
wheels for torch/onnxruntime — Hindsight cannot install.

**Workaround:** new devcontainer path `.devcontainer/glibc/devcontainer.json`
has no prebuild history. Fresh path → forced rebuild → Ubuntu base.

**DO** when changing devcontainer config: use a new path.
**DO** verify base after create: `grep PRETTY_NAME /etc/os-release`.

## Addendum · Codespaces 502 pattern

`502 Bad Gateway` from `<codespace>-<port>.app.github.dev` means the port
forwarding is registered but the backend socket isn't accepting. Causes:

1. App still in warm-up. Hindsight issue #4374: `create_app()` lifespan
   awaits `memory.initialize()` before uvicorn accepts connections.
   Window: up to 3 min when local embedding/reranker providers are used.
2. App crashed on startup — port never bound. `tail /tmp/hs.log`.
3. SSH feature missing from devcontainer — health probes silently fail.
   `gh codespace ssh` needs `ghcr.io/devcontainers/features/sshd:1`.

Diagnose order: log tail → `ss -tln | grep PORT` → probe `/health/live`
(DB-free) vs `/health/ready` (DB-gated). A 503 on ready + 200 on live
means the process is up and the DB is still initialising.

Gotcha repeats: `/tmp` doesn't exist on Termux. Always `$TMPDIR`.

## Addendum · gh-status gate

`gh` CLI prints `check your internet connection or https://githubstatus.com`
when API calls fail for reasons other than the local network. The message
does not distinguish GitHub platform degradation from local auth or
rate-limit failure.

**DO** run `gh-status check` before retrying any failed gh/git-push/git-fetch.
Exit codes: 0=operational, 1=degraded, 2=outage, 3=fetch-error.
**DO** wrap destructive GitHub operations with `gh-status gate -- <cmd>`.
**DO** review `gh-status history` when correlating a failure window.

Endpoints: /api/v2/{status,summary,components,incidents/unresolved}.json
Cache: 60s at ~/.deepcli/cache/gh-status-*.json
Log: ~/.deepcli/logs/gh-status/history.jsonl

## Addendum · Unpushed-commit masquerading as prebuild staleness

**Symptom:** every new codespace landed on Alpine despite
`.devcontainer/devcontainer.json` specifying a Debian base.

**Misdiagnosis:** prebuild cache fallback. Spent ~40 minutes on
prebuild API calls, delete-all, delete-prebuilds, non-canonical paths.

**Actual cause:** `.devcontainer/*` files existed in local HEAD
(`fbba4709`) but were never pushed to `origin/feat/...`. Codespaces
clones from origin. When origin lacks the config, Codespaces falls back
to a default image — which happens to be Alpine-based for this repo.

`git ls-tree -r origin/<branch> -- .devcontainer/` returning empty
was the diagnostic signal. My prior blocks didn't run that check.

**DO** after any commit that changes `.devcontainer/`:
    git push origin HEAD:<branch>
    git ls-tree -r origin/<branch> -- .devcontainer/ | wc -l   # must be > 0

**DO NOT** attempt prebuild invalidation until origin-verify is green.
**DO NOT** delete codespaces as a workaround before verifying origin.

**Fix confirmed 2026-10-01:** after `f2e1d91b` landed on origin, fresh
create produced `Debian GNU/Linux 12 (bookworm)` + `Python 3.11.17` +
`GLIBC 2.36` — post-create log captured in codespace creation output.

Footgun sequence:
  1. Commit locally
  2. Assume Codespaces reads local
  3. See old image → blame prebuilds
  4. Delete codespaces / prebuilds
  5. Recreate → same fallback because origin still lacks files
  6. Repeat

Break the loop with one line: `git ls-tree -r origin/<branch> -- <path>`.

## Addendum · Archive doctrine

Replace `rm -rf` with `archive.sh --reason "..."`. Targets move to
`~/.deepcli/archive/<UTC-stamp>/<original-path>`; a row is appended to
`~/.deepcli/logs/destructive.jsonl` with sha256, size, reason.

`rm` is permitted only for `$TMPDIR/*`. `rm-safe` remains for
intentional single-file removal. `archive.sh` is the default verb for
anything with recovery value.

**DO** archive before destructive verbs.
**DO NOT** `rm -rf` any path not proven cache, duplicate, or git-managed.

## Addendum · Hang awareness — monitoring patterns that don't lie

### The 55-minute perceived hang
Two stacked causes:
1. `watch -n 15 'gh codespace ssh ...'` spawns a new SSH session every
   15s. Each handshake takes 5-15s. Under load, sessions queue — the loop
   never catches up. Looks like a hang; is actually SSH backpressure.
2. The offload was in a Gemini 429 retry loop. Hindsight's LLM wrapper
   uses exponential backoff. Every retain → 429 → sleep → retry. Silent.

### Rule: monitor via log tail, not via SSH watch
**DO NOT** `watch 'gh codespace ssh ...'` — each tick creates a session.
**DO** ship a monitor script once, run it inside the codespace, tee to a log.
**DO** tail that log from Termux: `gh codespace ssh -c $CS -- 'tail -f /tmp/run.log'`.
Or run inside codespace tmux and poll `tmux capture-pane`.

### Rule: retry loops must log
Every retry prints one line to /tmp/hs.log with attempt#, code, backoff.
If a run has been silent >2 min, it's stuck in a loop.

### Rule: model rotation is logged per-attempt
Each provider/model attempt appends a row to
~/.deepcli/logs/model-rotation/<provider>__<model>.jsonl with health result.
Successful model on a task category is the leaderboard entry.
