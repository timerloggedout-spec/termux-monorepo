
---

## 9 · Blast-radius doctrine
- **DO** print target list before any `-u`, `-r`, `--force`, `-A` flag.
- **DO** refuse destructive verbs when cwd == `$HOME`.
- **DO** require `--confirm` on wrappers for delete-class operations.
- **DO** dry-run any command touching > 50 files.

## 10 · Pre-flight doctrine
- **DO** verify tool exists and version matches expectation.
- **DO** check quota/credits before paid API calls.
- **DO** count files/size before scans.
- **DO** inventory existing resources before creating new ones.

## 11 · Trunk doctrine
- **DO** rebase onto trunk every session.
- **DO** push every commit before moving on.
- **DO** remove worktree at PR merge.
- **DO** cap worktrees at 2 simultaneously.
- **DO** close branches older than 7 days without a PR.

## 12 · State doctrine
- **DO** vault snap before any config/key/creds mutation.
- **DO** verify vault restore works weekly.
- **DO** keep last 20 snapshots, prune older.
- **DO** log every op to `~/.deepcli/vault/logs/ops.jsonl`.

## 13 · Hook doctrine
- **DO** run hooks on every commit, including WIP.
- **DO** fix failing hooks, never bypass.
- **DO** log exceptions to `docs/STANDARDS/EXCEPTIONS.md`.
- **DO** verify hooks fire by planting a test violation weekly.

## 14 · Boundary doctrine
- **DO** treat repo root == HOME as a hazard zone.
- **DO** path-spec everything: `git add <path>`, never `-A`.
- **DO** use worktrees for parallel work, primary for trunk.
- **DO** `cd` into subdirectories for destructive commands.
