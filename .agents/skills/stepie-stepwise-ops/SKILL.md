---
name: stepie-stepwise-ops
description: Stepie AKA StepWise MCP as production planning surface for termux-monorepo. Load when planning milestones, expanding goal 2087, RECON-to-step mapping, dual-gate WAIT loops, or synchronizing Stepie with LANE-MATRIX and adaptive-wait. Triggers on Stepie, StepWise, stepwise planning, goal 2087, insert_steps, session pulse plan.
---

# Stepie Stepwise Ops

Production planning surface for `timerloggedout-spec/termux-monorepo`. Stepie holds milestones; GitHub holds evidence; dual-gate holds promote.

Session stamp: 2026-09-22 11:01 PDT — tip `0153acc2`; preferred extract **#724** @ `f992bd49` (rebase onto tip). Pulse branch `ops/session-lane-matrix-20260922-1101` SUPERSEDES #743.

## Live Stepie map (this session)

- Goal **2087** termux-monorepo development: 1/12 complete (Claude↔Grok MCP).
- Next 2087 pending: step 10023 wire icm-cctv && visualization surfaces.
- Primary goal **2149** Games Masters taxonomy — leave primary unless operator reassigns.
- Goal **2152** Fully Automated Agentic Role Moniker Development Environment — evaluation loop adjacent to dual-gate.
- Do not insert duplicate 2087 pulses; add notes on existing steps when evidence changes.

## Cadence

1. RECON GitHub connector + public tip.
2. Classify open PRs: EXTRACT / WAIT / HOLD / OBSERVE / SUPERSEDE / DRAFT.
3. Dual-gate before promote: `python3 scripts/ci/repo_gate.py` + `python3 scripts/ci/termux_smoke.py`.
4. Stay busy: LANE-MATRIX rewrite, skill realign, ML keep-alive preservation.
5. Do not treat WAIT as operator stop.

Operator ACTIVE. HOLD/WAIT/OBSERVE classify PRs, not operator idle.
AVOID HITL YOLO YEET AUTOAPPROVE.
Agent-Identity: Grok (Administrator)
