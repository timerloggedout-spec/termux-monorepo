# Onboarding — first hour

## 0. What this is

An agent development monorepo. Runs on Termux (Android) for daily
work, uses a Codespace for heavy compute. Eight subsystems, one agent
loop, a memory stack, and hygiene services that keep it all running.

## 1. See the state (5 minutes)

    mvt-status
    mvt-status --copy
    sv status loop-guard hygiene-watchdog hygiene-reclaim hygiene-reclaim-trigger
    df -h /data

Output tells you what the agent is doing, which services are alive,
whether disk and memory are healthy.

## 2. Read the doctrine (15 minutes)

Order matters:

1. docs/STANDARDS/PROCESS/RECON-FIRST-WORKTREE-DISCIPLINE.md
2. docs/STANDARDS/PROCESS/BRANCH-RETENTION.md
3. docs/STANDARDS/PROCESS/AGENT-ROLES.md
4. deepcli/tools/hygiene/MVT-SYSTEM.md
5. deepcli/tools/hygiene/GPG-STATUS.md

## 3. Dispatch a task (15 minutes)

Task files live in deepcli/tasks/ (gitignored), durable copy in
docs/ops/tasks/.

    deepagent-dispatch ~/deepcli/tasks/<name>.md

The wrapper logs to ~/.deepcli/logs/hygiene/dispatch-*.log, tails the
log live, and hands off notifications via Termux:API.

The agent reads the task, produces PLAN.md if gated, otherwise
creates a worktree, edits, runs tests, opens a PR, and calls finish.

## 4. Watch it work (15 minutes)

    tail -f ~/.deepcli/logs/hygiene/dispatch-*.log
    gh pr list --repo timerloggedout-spec/termux-monorepo --limit 5 --state open

## 5. The continuous loop (5 minutes)

    deepagent-continuous 8

Runs continuous-improve.md in a loop for 8 hours. Each iteration
picks one small improvement, one file per PR, at most 40 LOC, always
adds a test, always opens a PR against the integration branch.

loop-guard pauses the loop if three consecutive iterations fail
identically. Resume by deleting ~/.deepcli/watchdog/loop.paused.

## 6. Breakage troubleshooting

| Symptom          | Where to look |
|------------------|---------------|
| loop stuck       | tail ~/.deepcli/logs/hygiene/continuous-*.log |
| service crashed  | sv status <svc> then tail ~/.deepcli/logs/hygiene/sv-<svc>/current |
| PR won't merge   | gh api repos/.../pulls/<n> --jq .mergeable_state |
| disk full        | reclaim-now; log at ~/.deepcli/logs/hygiene/reclaim-now.log |
| memory low       | hygiene_preflight runs at loop start |
| attribution      | mvt-attribute <session> <path> |

## 7. Contributing

Read CONTRIBUTING.md. Short version:

- Never delete a branch.
- Worktree for any multi-file change.
- Conventional Commits.
- One test per PR minimum.
- Sentinels review, rollup merges.

## 8. Unblock list (human decision required)

- GPG fresh TOTP seed — github.com/settings/security
- gho_ PAT rotation — github.com/settings/tokens
- /storage/emulated/0 inventory — needs MANAGE_EXTERNAL_STORAGE
- master <-> integration branch reconciliation
