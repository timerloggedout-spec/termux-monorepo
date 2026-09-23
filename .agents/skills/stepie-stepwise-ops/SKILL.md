---
name: stepie-stepwise-ops
description: Stepie AKA StepWise MCP as production planning surface for termux-monorepo. Load when planning milestones, expanding goal 2087, RECON-to-step mapping, dual-gate WAIT loops, or synchronizing Stepie with LANE-MATRIX and adaptive-wait. Triggers on Stepie, StepWise, stepwise planning, goal 2087, insert_steps, session pulse plan.
---

Canonical: master `.agents/skills/stepie-stepwise-ops/SKILL.md`.

# Stepie Stepwise Ops

Production planning surface for `timerloggedout-spec/termux-monorepo`. Stepie holds milestones; GitHub holds evidence; dual-gate holds promote.

## Role in the stack

| Surface | Owns | Does not own |
|---------|------|--------------|
| **Stepie (this skill)** | Goals, ordered milestones, completion criteria, trigger cues, session plan notes | Code, CI, merge authority |
| **LANE-MATRIX.md** | Tip-first PR classification (PROMOTE / WAIT / HOLD / EXTRACT / OBSERVE / SUPERSEDE) | Personal task lists |
| **adaptive-wait** | Dual-gate before promote; stay-busy disjoint work while CI runs | Goal hierarchy |
| **evidence-led-monorepo-ops** | Session SSOT stamp, mega policy, co-load list | StepWise tool calls |
| **help-wanted-lane** | Foreign PR claim → follow-up → dashboard receipts | Primary monorepo goal tree |

Stepie is the **planning utility**. It does not replace dual-gate or LANE-MATRIX. It makes the operator plan queryable, ordered, and evidence-linked.

## Primary goal (production)

- **Goal ID 2087** — `termux-monorepo development` (isPrimary).
- Anchor step title matches the goal; leave anchor description empty or minimal (repo URL only).
- Expand with `insert_steps` before the anchor. Near-term milestones first; distant work thinner.
- Milestone **description** = one short completion criterion only. Methods, links, and RECON go in **notes**.

## Session bootstrap (every admin session)

1. Load this skill + `evidence-led-monorepo-ops` + `adaptive-wait`.
2. `get_overview` — confirm 2087 is primary; count pending steps.
3. RECON via GitHub connector (open PRs, #175, LANE-MATRIX tip, dual-gate status).
4. If plan is stale vs tip or missing near-term extracts, `insert_steps` or `update_step`.
5. Write a RECON note on the session-pulse step (HTML, evidence bullets only).
6. Rewrite `docs/ops/LANE-MATRIX.md` on a feature branch when the tip or lane map moved.
7. Stay busy on disjoint SSOT / skill mirrors while dual-gate runs — do not idle-poll.

## Milestone design rules

- Title: verb + key noun (e.g. `Dual-gate #713 slim ML extract`).
- Description: brief verifiable completion criteria. No how-to, no examples, no resource lists.
- `triggerContext`: 2–4 words max, cue side only (e.g. `🧪 after CI`, `📊 session start`). Omit if no reliable cue.
- Matrix category: use `urgent_important` for dual-gate and tip-blocking work; otherwise leave unset unless operator sets it.
- Prefer EXTRACT children over mega parents (#713 over #682).
- Never auto-complete a step from CI green alone — record the evidence in a note, then mark completed when the criterion is met.

## Tool discipline (Stepie MCP)

| Intent | Tool |
|--------|------|
| Orient | `get_overview` |
| Read plan | `search_step` goalId=2087 responseFormat=detailed |
| Expand plan | `insert_steps` before anchor |
| Record evidence | `create_note` / replace note (merged HTML) |
| Advance status | `update_step` status=completed only after criterion met |
| Goal context | `update_goal` description = full merged replacement |
| Standalone errands | `create_task` (Eisenhower) — not for goal milestones |

Always pass a fresh `operationId` (UUID). For updates, pass accurate `expectedUpdatedAt` when known; use null only when the tool allows and conflict is acceptable risk.

## Fit with other cadences

- **Mayan 13-phase / concurrent lattice (#631)**: Stepie milestones map to phase outcomes; phase parallelism lives in Actions + LANE-MATRIX, not inside one Stepie goal.
- **Help-wanted cadence**: separate goal or tasks; link via notes (PRIMARY/FALLBACK receipts). Do not fold foreign PR claims into 2087 milestones.
- **MoneyBall / live_catalog / model-router**: OBSERVE or EXTRACT lanes in LANE-MATRIX; Stepie only tracks the operator decision milestone if it blocks promote.
- **Codespace agent lane / Bifrost**: host preference documented in ops docs; Stepie does not own runtime hosts.
- **refTemplates / smods / RinDig**: reference pins under CLAUDE.md; Stepie notes may cite them, never treat as promote gates.
- **Session SSOT pulse**: every admin session rewrites LANE-MATRIX and refreshes the Stepie RECON note. Age alone does not promote.

## Maximize utility surface (production)

1. **Single primary goal** for monorepo admin — avoid parallel ops goals that fragment the plan.
2. **Tip-first ordering** — first pending milestone should unblock the current preferred extract.
3. **Evidence in notes** — SHA, PR number, dual-gate conclusion, non-gate rationale.
4. **Co-load contract** — this skill never authorizes YOLO merge; adaptive-wait + dual-gate still gate promote.
5. **Collaborator parity** — canonical path is `.agents/skills/stepie-stepwise-ops/SKILL.md`; local `.grok/skills/` is mirror only.
6. **Inventory** — after land, add row to `docs/ops/SKILLS-INVENTORY.md` under `.agents/skills/` and Admin role load list.
7. **No HITL YOLO YEET AUTOAPPROVE** — Stepie plans do not merge PRs.

## Anti-patterns

- Duplicating LANE-MATRIX tables inside Stepie descriptions.
- Completing milestones because CI is green without recording the criterion evidence.
- Creating new Stepie goals for every PR — use steps under 2087 or independent Matrix tasks.
- Storing secrets, PATs, or raw credential values in goal/step/note content (#184 notes-only).
- Treating Copilot / CodeRabbit / Vercel rate-limit as promote gates.

## Quick references

- Priority hub: Issue **#175**
- Dual-gate: hygiene+portability + agentic termux smoke
- Living lane SSOT: `docs/ops/LANE-MATRIX.md`
- Agent entry: `CLAUDE.md`
- Inventory: `docs/ops/SKILLS-INVENTORY.md`
- Cadence detail: `references/cadence-map.md`

Agent-Identity: Grok (Administrator)
Session stamp: 2026-09-21 15:07 PDT — tip `abaad3da`; preferred extract #713 @ `4ec03d54`.
