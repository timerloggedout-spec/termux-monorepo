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

## Current production anchors (2026-09-18T23:27Z PDT)

| Item | State |
|------|-------|
| Master HEAD | `6af1e12c5afb2caf` (`ops(skills): record #594 landing onto d79562d1` #595) |
| Just landed | #576–#595 chain through `6af1e12c` |
| Dual gates last verified | #595 PR dual-gate on `d91294b9`: smoke **35309791148** SUCCESS; hygiene **35309791199** SUCCESS. #594 PR dual-gate on `e124b434`: smoke **35306172380** SUCCESS; hygiene **35306172362** SUCCESS. Master dual-gate on `eefc068`: smoke **35301928043** SUCCESS; repo-gate **35301928066** SUCCESS. Master push dual-gate on `6af1e12c` admitted (in flight at record). |
| Observe (not merged) | #583 Grafana MCP (dual-gate green on `a2d8415a` but `validate-pull-request` extra-red FAIL ≠ gate). #584 MVT context-safe budget. #587 Jules date-only audit bump. #589 Jules CedrLang placeholder: update-branch CONFLICTed vs `01083fcc` — extract later |
| Extra-red HOLD | #549 ML (#175) dirty/behind base `6df9b66`; sibling #432 HOLD — extract later from live master `6af1e12c` |
| HOLD mega | #523 #527 #545 #543 #455 #485 #483 #481 #474 #471 #466 |
| Draft | #578 accounting/bidding schema pilot |
| Comment-storm-skip | Gemini/Jules/ECC/`coderabbitai` `issue_comment` cancelled/success mix ≠ gate |
| Extra-red non-gate | actions-run-watcher / agent-jules-on-issues / swe-reference-evaluation startup_failure ≠ gate |
| Non-gates | mermaid docs-refresh; OpenRouter free catalog sync fail; merge-promotion-queue inventory fail |

## Extract recipe

Create branch from current master. Do not force-update dirty branches. #549 remains dirty/behind — do not merge; extract later from `6af1e12c`. #589 update-branch conflicted — extract CedrLang placeholder change from live master if still valuable.

BIUDL. Agent-Identity: Grok (Administrator)
