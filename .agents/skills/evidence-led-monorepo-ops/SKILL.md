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

## Current production anchors (2026-09-18T16:15Z UTC)

| Item | State |
|------|-------|
| Master HEAD | `c082f53379d230f4617f201d32c114f198dd63a1` (`chore(docs): refresh DOCS-BRANCH-INDEX`) |
| Just landed | #590–#595 skill-record chain through `6af1e12`; catalog repair `e24f08d` after truncated `9aa6475` |
| Dual gates last verified | Master dual-gate on `eefc068`: smoke **35301928043** SUCCESS; repo-gate **35301928066** SUCCESS. #594 PR dual-gate on `e124b434`: smoke **35306172380**; hygiene **35306172362** |
| Extract in flight | `feat/ml-pipelines-extract-c082f53` — observe-mode ML pipelines reconstructed from dirty #549 onto live master. Supersedes #549/#432 wholesale. |
| Observe (not merged) | #596 skills-record (unstable). #597 Sentinel symlink. #598 Bolt regex. #583 Grafana MCP (extra-red validate-PR ≠ gate). #584 MVT budget. #589 CedrLang update-branch-conflict. |
| Extra-red HOLD | Dirty #549 (this extract replaces it) / sibling #432 HOLD |
| HOLD mega | #523 #527 #545 #543 #455 #485 #483 #481 #474 #471 #466 #500 |
| Draft | #578 accounting/bidding schema pilot |
| Extra-red non-gate | Historical-eval catalog freshness **35356132030**; merge-promotion-queue inventory; actions-run-watcher / agent-jules-on-issues / swe-reference-evaluation startup_failure; Vercel rate-limit |
| Comment-storm-skip | Gemini/Jules/ECC/`coderabbitai` `issue_comment` cancelled/success mix ≠ gate |

## Extract recipe

Create branch from current master. Do not force-update dirty branches. Reconstruct ML observe-mode from #549 onto live HEAD instead of merging dirty `feat/ml-pipelines-rebase-175`. Catalog regen rides with the extract because `.github/workflows/ml-pipelines.yml` is new. #589 remains extract-later. MoneyBall scores never merge.

## 2026-09-18 addition

Use `.agents/skills/pr-minesweeper` plus `ml_pipelines` for live PR lane overlap.
MoneyBall scores remain decision-support only. Dirty PR #432/#549 are superseded by a
master-reconstructed observe-mode package; do not wholesale-merge the stale branches.

BIUDL. Agent-Identity: Grok (Administrator)
