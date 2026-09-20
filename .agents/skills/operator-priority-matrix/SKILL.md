---
name: operator-priority-matrix
description: Living Issue #175 operator matrix. Classify every open PR into promote/wait/hold/extract/observe. Dual-gate is the only promote path.
---

# Skill: operator-priority-matrix

Living issue: [#175](https://github.com/timerloggedout-spec/termux-monorepo/issues/175)

## Lanes

| lane | meaning |
|------|---------|
| promote | clean + dual-gate green |
| wait | unstable / in_progress / missing dual-gate |
| hold | dirty, stale, or security-sensitive until rebase |
| extract | mega / minesweeper / ML wholesale |
| observe | Jules/Bolt/Sentinel bots; do not force-merge |

## Operator rules still in force

1. No force-push to master
2. Small green rebased PRs
3. Dual gates required
4. Reject Class 3/4 artifacts
5. GitLab non-blocking
6. Continue-only Jules default
7. Maximize Actions; skip-reason on quota
