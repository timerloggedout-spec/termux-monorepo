# LANE-MATRIX (living SSOT)

**Session:** 2026-09-21 10:09 PDT  
**Agent-Identity:** Grok (Administrator)  
**Live master:** `2e4f59aa` — #707 Sentinel nexuscli squash onto `2d464c1b`  
**Priority hub:** Issue #175

Rewrite this file every admin session. Copilot is optional peer, not a promote gate. Size ≠ quality. Promote when dual-gate is green **and** the diff is an extract, not a mega. Vercel rate-limit is non-gate. Age alone does not promote.

## Landed this window (evidence)

| SHA | What |
|-----|------|
| `2e4f59aa` | #707 Sentinel: nexuscli symlink-safe export/config |
| `2d464c1b` | help-wanted live status 15:20Z |
| `044716f0` | help-wanted follow-up evidence 15:20Z |
| `98db978b` | DOCS-BRANCH-INDEX refresh |

#705/#706/#709 are stale session rewrites vs this tip — SUPERSEDE once this dual-gate is green.

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
| #682 | EXTRACT / WAIT | ML keep-alive DAG (#175). 130 files. Dual-gate SUCCESS on prior head. Prefer slimmer `ml/pipelines/` child. |
| #680 / #708 | OBSERVE | Bolt live_catalog_feed family (Jules). Overlapping catalog work — do not double-merge. |
| #702 | OBSERVE | Gravitee observatory seed |
| #684 | HOLD / REBASE | unify Actions cadence; dirty vs tip |
| #685 | OBSERVE | arrhythmic-zero-token-search |
| #695 | OBSERVE | AlphaEvolve + Dream-RSI Paper2Agent |
| #543 | OBSERVE | skill definition quality lane |
| #630 | EXTRACT | Jules dashboard rich UI — minesweeper |
| #432/#549/#601 | EXTRACT | ML wholesale family — keep-alive is #682 tree |
| #705/#706/#709 | SUPERSEDE | session SSOT rewrites on older tips |

## Ancient / wrong-base HOLD

#47 OBSERVE/SUPERSEDED. #48 HOLD (base master-staging). #69 HOLD (feature base). #73 HOLD. #81 OBSERVE. #92 EXTRACT security slice. Do not close-as-superseded until extract lands.

## Issue → PR map

| Issue | Role | Linked |
|-------|------|--------|
| **#175** | OPERATOR matrix + dual-gate | #432 #549 #601 #682 (ML); #630 minesweeper; #707 landed |
| #184 | Credential inventory (notes only) | secrets hygiene |
| #117 | Agent2Agent / MCP Agent Mail | #143 |
| #88/#91/#94 | routing | #48 family |
| #50 | termux-smoke / master-staging gate | dual-gate ancestry |
| #21 | oldest production backlog | pre-matrix |

## Next cycle

1. Leave #682 EXTRACT until sliced.
2. Pulse #175 (done 10:09 PDT, comment 5764466607).
3. Wait dual-gate on this session PR before promote.
4. Stay busy on SSOT / skill upgrades while CI waits. No HITL YOLO merge.
