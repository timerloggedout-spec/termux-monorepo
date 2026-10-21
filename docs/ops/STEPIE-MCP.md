# Stepie / StepWise MCP — Ops Contract (SSOT)

**Stepie plans. Monorepo ships. Dual-gate promotes.**

Stepie AKA StepWise is an external planner (syworkshop.cn). Goal/step/matrix data live in their cloud only. This monorepo does **not** mirror Stepie rows into git as product SSOT.

## Live MCP (operator)

| Item | Value |
|------|--------|
| Product | StepWise / Stepie |
| Vendor contact | support@syworkshop.cn |
| MCP entry | https://stepwiseplanner.com/en-US/mcp/ (vendor-published) |
| Connector (this agent) | `Stepie AKA: StepWise` |
| Auth | Host/connector OAuth; no monorepo secret for default plan writes |

Probe and tool schemas change on vendor side. Prefer live tool discovery over hardcoding.

## Separation of planes

| Plane | Owns | Does not |
|-------|------|----------|
| Stepie | Goals, steps, notes, matrix tasks, core memory | Merge PRs, Actions, code |
| termux-monorepo | Code, workflows, docs, evidence, dual-gate | Invent Stepie completion |
| LANE-MATRIX / Sweep | Board classification | Session-pulse PRs from Stepie |

Policy one-liner (skill): Stepie must not emit session-pulse PRs or #175 comment floods.

## Known failure modes (vendor + MCP)

Observed 2026-09-22 … 2026-09-24 (operator email to support@syworkshop.cn + MCP writes):

1. **Silent no-op create** — UI/MCP reports progress narrative; Goals / Steps / Tasks / Priority Matrix often do not materialize (partial success: one task).
2. **Quota / Server Busy** — rapid `retry` on notification regeneration → quota message after create failures.
3. **`update_step` Conflict** — matrixCategory (and other updates) require accurate `expectedUpdatedAt`; `search_step` may omit it → Conflict Exception when `null` is sent.
4. **Memory restore** — prior-version memory recovery path unclear; open with vendor.

Mitigations on our side:

- After every write: re-`search_goal` / `search_step` / `search_task` and assert IDs exist before claiming success.
- Do not spam retry; back off on quota.
- For matrix updates: fetch a response that includes `updatedAt` before `update_step`, or set matrix in-app.
- Keep durable product state in monorepo git; treat Stepie as planning surface only.

## Live goals bound this cycle (2026-09-24 MCP)

| ID | Title | Anchor | Notes |
|----|--------|--------|-------|
| **2157** | Custom Classifiers from Scratch | 10044 | Steps 10046–10050; note 1302 resources (Laya/Jev/sysone-bench) |
| **2158** | Termux Orchestration Hub | 10045 | Steps 10051–10054; note 1303 hub_mcp / B160V envelope |
| **2087** | termux-monorepo development | 9774 | Existing; primary product goal in Stepie |
| **2149** | Games Masters … | 10007 | Primary goal; MoneyBall / classifier parity feeds 2157 |

### Steps (2157)

| ID | Title |
|----|--------|
| 10046 | Distill classifier spec from parity EVAL |
| 10047 | Build training dataset pipeline |
| 10048 | Train first from-scratch classifier |
| 10049 | Optimize multi-environment builds |
| 10050 | Run comparative classifier EVALS |

### Steps (2158)

| ID | Title |
|----|--------|
| 10051 | Map hub capability && capacity budget |
| 10052 | Re-verify hub_mcp boundary docs |
| 10053 | Wire hub dispatch to remote layers |
| 10054 | Land local decision layer on device |

### Open tasks

| ID | Title | Matrix |
|----|--------|--------|
| 1223 | Verify TYPESAFE_API_KEY in GH Environment secrets | urgent_important |
| 1224 | Locate awesome-list curation paths for Stepie handoff | not_urgent_important |
| 1222 | Support ticket: export prior Stepie data for reintegration | not_urgent_important |

## Execution layers (planning context)

Actions, CodeSpaces, Environments, Colab, Render; future GCP/AWS/Azure free-tier research lane. Device hub = constrained (BLU B160V); heavy work remote.

## Agent rules

1. Create/update Stepie only when the operator explicitly authorizes a write.
2. After write: verify by search; never claim success from narrative alone.
3. Do not open session-pulse or heartbeat PRs from Stepie activity.
4. Product code for classifiers / hub lives in monorepo PRs under dual-gate — not in Stepie notes.

## Related

- Skill: `.agents/skills/stepie-stepwise-ops/SKILL.md`
- Board policy: `.agents/skills/stepie-stepwise-ops/references/BOARD-VS-LEDGER.md`
- GitHub MCP live URL (different host): `docs/ops/GITHUB-MCP-LIVE-URL.md`

Agent-Identity: Grok (Administrator)
Session: 2026-09-24
