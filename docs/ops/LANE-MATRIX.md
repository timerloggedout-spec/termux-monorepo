# LANE-MATRIX (living SSOT)

**Session:** 2026-09-23 12:06 PDT
**Agent-Identity:** Grok (Administrator)
**Live master (base):** `66ebf5b5`
**This PR tip:** ops/debate-dock-extract-20260923-1206
**Priority hub:** Issue #175

Rewrite this file every admin session. Copilot is optional peer, not a promote gate. Size ≠ quality. Promote when dual-gate is green **and** the diff is an extract, not a mega. Vercel rate-limit is non-gate (#772). Age alone does not promote.

**BIUDL = Broad → Integrate → Validate → Develop → Learn.**
**AVOID HITL YOLO MODE YEET AUTOAPPROVE.**
**HOLD is not a valid state.** WAIT is the promote gate, not idle. Active contributor produces extracts.

## Landed this window (evidence)

| SHA | What |
|-----|------|
| `66ebf5b5` | docs-branch-index refresh (bot) |
| `fec3ac0d` | ATES TDQS + skill-quality + adaptive-wait contract |
| `c9b26a53` | help-wanted live status |
| pending this PR | debate dock extract from #69 |

## Dual-gate contract

1. `hygiene + portability gate` SUCCESS
2. `agentic termux smoke` SUCCESS
3. Vercel rate-limits are **non-gate**
4. Copilot / CodeRabbit / Qodo / Devin = advisory (Devin trial expired; CodeRabbit rate-limited)
5. Age alone does not promote
6. Size ≠ quality: dual-gate green + 73 files still EXTRACT

## Tip-first active lanes

| PR | Lane | Why |
|----|------|-----|
| this | EXTRACT / PROMOTE-CANDIDATE | #69 debate dock onto master. No AGENTS.md edit. |
| #783 | WAIT-for-clean / stale-base | Dual-gate SUCCESS on `9f94f689`; master moved to `66ebf5b5`. |
| #781 | WAIT-for-clean / dirty | Dual-gate SUCCESS; mergeable dirty vs later master. |
| #48 | EXTRACT | Wrong base `master-staging`, dirty, 73 files / 6153+. Do not wholesale merge. |
| #746 | EXTRACT | ML slim keep-alive — still large vs tip. |
| #768 | OBSERVE | Jules sentinel harden — review first. |
| #772 | KNOWN | Vercel rate-limit stalls mergeable_state. Non-gate. |

## Ancient / wrong-base (EXTRACT, not HOLD)

#47 OBSERVE/SUPERSEDED. #48 EXTRACT (hub mega). #69 EXTRACT in this PR (dock only). #73 EXTRACT. Do not close-as-superseded until extract lands.

## Issue → PR map

| Issue | Role | Linked |
|-------|------|--------|
| **#175** | OPERATOR matrix + dual-gate | this PR; #781 #783 |
| #184 | Credential inventory (names only) | secrets hygiene — never paste values |
| #772 | mergeable_state instability | Vercel non-gate |
| #777 | EXTRACT follow-on | agent-review-auto-jules → agent-context-store |

## Stepie (planning surface only)

Goal 2087 `termux-monorepo development` still 2/12. Stepie does not merge. Dual-gate promotes.

## Next cycle

1. Dual-gate this extract; promote only when green + outcome verified.
2. Slice #48 (standalone health + openai_compat only) if needed — never 73-file merge.
3. Close #69 as completed after this extract merges.
4. Stay busy on disjoint extracts while CI waits. No HITL YOLO merge.
