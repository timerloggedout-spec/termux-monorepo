# LANE-MATRIX (living SSOT)

**Session:** 2026-09-21 16:13 PDT  
**Agent-Identity:** Grok (Administrator)  
**Live master (base):** `cb995e76`  
**This PR tip:** ops/biudl-claude-primary-deprecate-agents-20260921  
**Priority hub:** Issue #175

Rewrite this file every admin session. Copilot is optional peer, not a promote gate. Size ≠ quality. Promote when dual-gate is green **and** the diff is an extract, not a mega. Vercel rate-limit is non-gate. Age alone does not promote.

**BIUDL = Broad → Integrate → Validate → Develop → Learn.** Fully Continuous Automated Development Evaluation Environment. **AVOID HITL YOLO MODE YEET AUTOAPPROVE.**

**Status change (this cycle):** Root `CLAUDE.md` is sole primary agent entry. Root `AGENTS.md` is **deprecated** (Linguist / CedrLang / Jules redirect-only). Content folded. All lanes (Jules, Linguist, Sentinel, Bolt, help-wanted, Codespace, ecc-tools, Stepie) load `CLAUDE.md` first.

## Landed this window (evidence)

| SHA | What |
|-----|------|
| (pending dual-gate) | CLAUDE.md BIUDL expanded + AGENTS.md deprecated redirect |
| (pending) | REFTEMPLATES directive corrected (no YOLO/YEET) |
| `cb995e76` | prior tip |

## Dual-gate contract

1. `hygiene + portability gate` SUCCESS
2. `agentic termux smoke` SUCCESS
3. Vercel rate-limits are **non-gate**
4. Copilot / CodeRabbit / Qodo / Devin = advisory
5. GitLab / Mintlify = non-gate
6. Age alone does not promote; dual-gate + rebase onto live master does
7. Size ≠ quality: dual-gate green + 130 files still EXTRACT

## Tip-first active lanes

| PR | Lane | Why |
|----|------|-----|
| #682 | EXTRACT / WAIT | ML keep-alive DAG (#175). 130 files. Prefer slimmer `ml/pipelines/` child. |
| this | SSOT / BIUDL | CLAUDE primary + AGENTS deprecate + directive hygiene |
| #680 / #708 | OBSERVE | Bolt live_catalog_feed family (Jules). Overlapping catalog work — do not double-merge. |
| #702 | OBSERVE | Gravitee observatory seed |
| #684 | HOLD / REBASE | unify Actions cadence; dirty vs tip |
| #685 | OBSERVE | arrhythmic-zero-token-search |
| #630 | EXTRACT | Jules dashboard rich UI — minesweeper |
| #432/#549/#601 | EXTRACT | ML wholesale family — keep-alive is #682 tree |

## Ancient / wrong-base HOLD

#47 OBSERVE/SUPERSEDED. #48 HOLD (base master-staging). #69 HOLD (feature base). #73 HOLD. #81 OBSERVE. #92 EXTRACT security slice. Do not close-as-superseded until extract lands.

## Issue → PR map

| Issue | Role | Linked |
|-------|------|--------|
| **#175** | OPERATOR matrix + dual-gate | #432 #549 #601 #682 (ML); #630 minesweeper |
| #184 | Credential inventory (notes only) | secrets hygiene |
| #117 | Agent2Agent / MCP Agent Mail | #143 |
| #88/#91/#94 | routing | #48 family |
| #50 | termux-smoke / master-staging gate | dual-gate ancestry |

## Next cycle

1. Dual-gate this PR; promote only when green + outcome verified.
2. Leave #682 EXTRACT until sliced.
3. Stay busy on SSOT / skill upgrades while CI waits. No HITL YOLO merge.
4. Jules / Linguist: confirm AGENTS.md is redirect-only.
