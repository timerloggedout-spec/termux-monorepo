---
name: stepie-stepwise-ops
description: Stepie AKA StepWise MCP as production planning surface for termux-monorepo.
---

Stepie plans. Sweep writes the board. Dual-gate promotes product PRs.
Stepie must not emit session-pulse PRs or #175 comment floods.

## Contract

Full ops SSOT: `docs/ops/STEPIE-MCP.md`

- External planner only (syworkshop.cn). No goal/step rows in git as product SSOT.
- After every MCP write: re-search and assert IDs before claiming success.
- Known failures: silent create, quota on retry-spam, `update_step` Conflict without `expectedUpdatedAt`.

## Live bind (2026-09-24)

| Goal | ID |
|------|-----|
| Custom Classifiers from Scratch | 2157 |
| Termux Orchestration Hub | 2158 |
| termux-monorepo development | 2087 |
| Games Masters (primary) | 2149 |

Tasks: 1223 TYPESAFE_API_KEY (UI); 1224 awesome-list handoff (NUI).

## Session

2026-09-24. Branch `feat/stepie-mcp-ops-20260924`. Tip base `95b19e4a`.
Agent-Identity: Grok (Administrator)
