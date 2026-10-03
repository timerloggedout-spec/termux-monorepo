# termux-monorepo

Autonomous agent development on Android / Termux, with a GitHub
Codespace as the compute-heavy tier.

Status: live, loop-driven.

## Subsystems

| Area          | Path                                | Role |
|---------------|-------------------------------------|------|
| DeepAgent     | deepcli/deepagent.py                | agent loop, tool dispatch |
| DeepCLI       | deepcli/deepcli/                    | DeepSeek web wrapper |
| Hindsight     | deepcli/tools/hindsight-lifecycle/  | memory stack |
| ArchWiz       | archwiz/                            | forensic toolchain |
| Synthegration | cli-synthegration/                  | session export + harvest |
| Observatory   | deepcli/deepcli/observatory/        | MVT framework |
| Hygiene       | deepcli/tools/hygiene/              | scoring, preflight, reclaim |
| Tests         | deepcli/tests/                      | unittest suite |

## Quick start

    mvt-status
    deepagent-dispatch ~/deepcli/tasks/<task>.md
    deepagent-continuous 8

## Doctrine

Read in order:

1. docs/STANDARDS/PROCESS/RECON-FIRST-WORKTREE-DISCIPLINE.md
2. docs/STANDARDS/PROCESS/BRANCH-RETENTION.md
3. docs/STANDARDS/PROCESS/AGENT-ROLES.md
4. docs/ONBOARDING.md
5. CONTRIBUTING.md

## Branching

- master                     default, promotion-only
- feat/dashboard-lanes-v2    integration branch (loop targets this)

## Never

- Delete a branch
- Force-push a shared ref
- Print a token
