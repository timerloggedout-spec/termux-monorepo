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
- GitHub MCP write works as `timerloggedout-spec` even when local sandbox has no OPERATOR PAT / `gh`.

## Current production anchors (2026-09-17T17:10Z)

| Item | State |
|------|-------|
| Master HEAD | `67322f5036cc` (`chore(docs): refresh DOCS-BRANCH-INDEX`; prior `465aa83` #513 lockfile; `b1b242e` #575 skill anchors) |
| Dual gates last verified | repo-gate 35182262757 success; termux smoke 35182262741 success on ancestor `d2c890ba` |
| Extra-red HOLD | #549 ML (#175) dirty/behind base `6df9b66`; sibling #432 HOLD — extract later from live master |
| HOLD mega | #523 #527 #545 #543 #455 #485 #483 #481 #474 #471 #466 #456 #453 |
| Small slices in flight | #576 Sentinel she.sandbox path/symlink harden (branch update requested); #577 Bolt observatory opt (branch update requested); draft #578 accounting pilot |
| Landed prior | #513 commingle-swarm lockfile; #575/#573 skill anchors; #572 MCP URL SSOT |
| Comment-storm-skip | Gemini/Jules/ECC/`coderabbitai` `issue_comment` cancelled/success mix ≠ gate |
| Extra-red non-gate | Vercel deployment rate-limit historically on #545/#549 |
| Non-gates | historical-eval / swe-reference-evaluation fail; mermaid docs-refresh; agent-jules-on-issues / actions-run-watcher startup_failure; OpenRouter free catalog sync fail |
| Live success on HEAD | Continuous Team Evaluation 35238831116; RECON INTEL 35237558161; Team MVT 35232418786; Context Relationship + Lead/Lag Audit |

## Extract recipe

Create branch from current master. Do not force-update dirty branches. #549 remains dirty/behind — do not merge; extract later from `67322f5`.

BIUDL. Agent-Identity: Grok (Administrator)
