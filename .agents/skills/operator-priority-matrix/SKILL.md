---
name: operator-priority-matrix
description: Living Issue #175 operator matrix. Classify every open PR into promote/wait/hold/extract/observe. Dual-gate is the only promote path. Rewrite docs/ops/LANE-MATRIX.md every session.
---

# Skill: operator-priority-matrix

Living issue: [#175](https://github.com/timerloggedout-spec/termux-monorepo/issues/175)  
**In-repo SSOT:** [`docs/ops/LANE-MATRIX.md`](../../docs/ops/LANE-MATRIX.md)

## Lanes

| lane | meaning |
|------|---------|
| promote | clean + dual-gate green |
| wait | unstable / in_progress / missing dual-gate |
| hold | dirty, stale, or security-sensitive until rebase |
| extract | prefer when minesweeper overlap or mixed intent |
| observe | Jules/Bolt/Sentinel bots; do not force-merge |

## Operator rules

1. No force-push to master
2. **Size ≠ quality** — mega PRs promote when dual-gate green
3. Dual gates required
4. Reject Class 3/4 artifacts
5. GitLab / Vercel hobby non-blocking
6. Continue-only Jules default
7. **Copilot is peer-optional, never primary promote route**
8. Rewrite `docs/ops/LANE-MATRIX.md` every admin session for Actions visibility

Agent-Identity: Grok (Administrator)
