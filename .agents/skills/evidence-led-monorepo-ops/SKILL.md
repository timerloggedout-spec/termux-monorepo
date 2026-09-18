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

## Current production anchors (2026-09-18T16:10Z UTC / 09:10 PDT)

| Item | State |
|------|-------|
| Master HEAD | `c082f53379d230f4617f201d32c114f198dd63a1` (`chore(docs): refresh DOCS-BRANCH-INDEX` by github-actions[bot]) |
| Just landed | #576–#595 chain; #595 merged 2026-09-18T06:27:38Z as `ops(skills): record #594 landing onto d79562d1` (`6af1e12c`). Bot docs-index then advanced master to `c082f533`. |
| Dual gates last verified | #595 PR dual-gate on `d91294b9`: smoke **35309791148** SUCCESS; hygiene **35309791199** SUCCESS. #594 PR dual-gate on `e124b434`: smoke **35306172380** SUCCESS; hygiene **35306172362** SUCCESS. Master dual-gate on `eefc068`: smoke **35301928043** SUCCESS; repo-gate **35301928066** SUCCESS. |
| Observe (not merged) | #583 Grafana MCP dual-gate green + extra-red validate-PR ≠ gate. #584 MVT context-safe budget. #587 Jules date-only audit. #589 CedrLang placeholder: update-branch CONFLICTed vs `01083fcc`. #597 Sentinel symlink; #598 Bolt regex/telemetry. |
| Extra-red HOLD | #549 ML (#175) dirty/behind base `6df9b66` head `d4f3faf8`; sibling #432 HOLD — extract later from live master `c082f533`. |
| HOLD mega | #523 #527 #545 #543 #455 #485 #483 #481 #474 #471 |
| Draft | #578 accounting/bidding schema pilot |
| Superseded extract | #596 record-#595 onto `6af1e12c` — behind `c082f533`, mergeable_state unstable. #599 automation catalog regen — dirty vs master. |
| Non-gates | Historical Evaluation Correlation freshness fail; merge-promotion-queue inventory fail; mermaid docs-refresh; comment-storm-skip |

## Extract recipe

Create branch from current master. Do not force-update dirty branches. Do not wholesale-merge HOLD mega. #549/#432 remain extract-later. #589 update-branch conflicted — extract CedrLang placeholder from live master if still valuable. #599 catalog freshness: regenerate on live master, do not merge dirty head.

BIUDL. Agent-Identity: Grok (Administrator)
