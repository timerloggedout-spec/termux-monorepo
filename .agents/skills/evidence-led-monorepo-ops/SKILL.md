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

## Current production anchors (2026-09-17T06:23Z)

| Item | State |
|------|-------|
| Master HEAD | `33c186b3` (#573 skill-anchor rebase after #572; prior `d2c890ba` #572 LIVE GitHub MCP URL SSOT) |
| Dual gates last verified | repo-gate 35182262757 success; termux smoke 35182262741 success on ancestor `d2c890ba` |
| Extra-red HOLD | #549 ML (#175) dirty/behind base `6df9b66`; sibling #432 HOLD |
| HOLD mega | #523 #527 #142 #455 #48 #543 #545 |
| Landed prior | #573 skill anchors; #572 MCP URL SSOT; #571 mcp-docker URL-only; #568 skill anchors |
| Comment-storm-skip | Gemini/Jules/ECC `issue_comment` skipped ≠ gate |
| Extra-red non-gate | Vercel deployment rate-limit on #545 and #549 (retry 24h) |
| Non-gates | historical-eval / swe-reference-evaluation fail; mermaid docs-refresh; agent-jules-on-issues / actions-run-watcher startup_failure |
| Live non-gate on HEAD | Historical Evaluation Correlation 35188283151 failure (schedule) |
| Live success on HEAD | Continuous Team Evaluation 35185850905; RECON INTEL 35184666931 |

## Extract recipe

Create branch from current master. Do not force-update dirty branches. #549 remains dirty/behind — do not merge; extract later.

BIUDL. Agent-Identity: Grok (Administrator)
