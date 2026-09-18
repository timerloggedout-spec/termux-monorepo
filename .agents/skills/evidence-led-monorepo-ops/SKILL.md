---
name: evidence-led-monorepo-ops
description: Continuous evidence-led admin ops on timerloggedout-spec/termux-monorepo (and similar agentic monorepos). Triggers on priority matrix, master gates, SHE progress, Manus/provider RE, dirty PR triage, Actions hygiene, or when the operator says continue, BIUDL, maximize actions, or /continue. Use for live state pulls, dispositions, small-green extracts, adaptive WAIT, and iterative process improvement documented as skills. Load this skill in every admin session.
---

# Skill: evidence-led-monorepo-ops

**Owner:** ArchW1z / Grok Administrator continuous admin on timerloggedout-spec/termux-monorepo.

**Canonical paths (keep in sync):**
- `.agents/skills/evidence-led-monorepo-ops/SKILL.md` ← **agent load path**
- `docs/ops/skills/evidence-led-monorepo-ops/SKILL.md` ← human/docs mirror
- `docs/ops/SKILLS-INVENTORY.md` ← full skill table + adaptive WAIT

**Primary agent entry:** `CLAUDE.md`.

## Posture

- Evidence over anecdote. Extract-only. Dual-gate before merge.
- Extra-red ≠ dual-gate. Behind-master dual-gate green ≠ auto-merge.
- **comment-storm is a FAILURE**, not skippable noise. Mitigate with concurrency groups + `cancel-in-progress: false` on SHA-bound ledgers. Do not treat cancelled ledger runs as green.
- Identity: `Agent-Identity: Grok (Administrator)`.
- GitHub MCP write works as `timerloggedout-spec` even when local sandbox has no OPERATOR PAT / `gh`.

## Current production anchors (2026-09-18T18:08Z UTC)

| Item | State |
|------|-------|
| Master HEAD | `20de2a5458698d805f97e77c8c2d4c204077a60a` (#604 skills after #603) |
| Just landed | #604 skill record; #603 ledger event_name + cancel-in-progress:false |
| This extract | peer-orch concurrency split by `github.event_name` (comment-storm was still cancelling collect) |
| Observe | #605 Paper2Agent draft. #583 Grafana. #584 MVT. Jules #597/#598. |
| Extra-red HOLD | #601 ML extract dirty/behind (`c082f533` vs live `20de2a54`). #549/#432 HOLD extract-later. |
| HOLD mega | #523 #527 #545 #543 #455 #485 #483 #481 |
| Draft | #578 accounting; #605 Paper2Agent |

## Extract recipe

Create branch from current master. Do not force-update dirty branches. Do not wholesale-merge HOLD mega or #601/#549/#432.

CodeRabbit `queue: max` on GHA concurrency is **not a valid key** (only `group` + `cancel-in-progress`). Do not apply.

BIUDL. Agent-Identity: Grok (Administrator)
