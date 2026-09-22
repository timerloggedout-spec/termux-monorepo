---
name: stepie-stepwise-ops
description: Stepie AKA StepWise MCP as production planning surface for termux-monorepo. Load when planning milestones, expanding goal 2087, RECON-to-step mapping, dual-gate WAIT loops, or synchronizing Stepie with LANE-MATRIX and adaptive-wait.
---

Canonical: master `.agents/skills/stepie-stepwise-ops/SKILL.md`.

Production planning surface for `timerloggedout-spec/termux-monorepo`. Stepie holds milestones; GitHub holds evidence; dual-gate holds promote.

Operator is **ACTIVE**. Stepie WAIT notes record PR lane state, not operator idle.

| Surface | Owns | Does not own |
|---------|------|--------------|
| **Stepie (this skill)** | Goals, ordered milestones, completion criteria, trigger cues, session plan notes | Code, CI, merge authority |
| **LANE-MATRIX.md** | Tip-first PR classification (PROMOTE / WAIT / HOLD / EXTRACT / OBSERVE / SUPERSEDE) | Personal task lists |
| **adaptive-wait** | Dual-gate before promote; stay-busy disjoint work while CI runs | Goal hierarchy |
| **evidence-led-monorepo-ops** | Session SSOT stamp, mega policy, co-load list | StepWise tool calls |

Primary production goal: **2087** termux-monorepo development. Stepie UI may mark another goal isPrimary; monorepo promote authority stays on 2087 + dual-gate.

Session stamp: 2026-09-22 04:12 PDT — tip `ca7fd7c8`; preferred extract #724 @ `e954e677` dual-gate green, mergeable unstable.
AVOID HITL YOLO YEET AUTOAPPROVE.
Agent-Identity: Grok (Administrator)
