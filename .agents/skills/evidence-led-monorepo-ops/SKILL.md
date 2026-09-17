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
- Identity: `Agent-Identity: Grok (Administrator)`.

## Current production anchors (2026-09-17T00:40Z)

| Item | State |
|------|-------|
| Master HEAD | `f6009939` (#564 squash; prior `820ecd2f` #562, `f1d59dc5` #560) |
| Dual gates on `f6009939` | repo-gate 35165001073 success; termux smoke 35165001074 success |
| Extra-red HOLD | #549 ML (#175); #432 sibling; #563 Jules linguist (1-file + Vercel rate-limit) |
| HOLD mega | #523 #527 #142 #455 #48 #543 #545 |
| HOLD generated drift | #561 Jules catalog-only; not lane SSOT |
| Observatory | full checkout SHA pinned in #562 |
| Comment-storm-skip | Gemini/Jules/ECC `issue_comment` skipped ≠ gate |
| Non-gates | historical-eval 35165001101 fail; mermaid docs-refresh — not dual-gate |

## Extract recipe

Create branch from current master. Do not force-update dirty branches.

BIUDL. Agent-Identity: Grok (Administrator)
