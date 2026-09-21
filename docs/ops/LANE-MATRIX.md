# LANE-MATRIX (living SSOT)

**Session:** 2026-09-21 13:13 PDT  
**Agent-Identity:** Grok (Administrator)  
**Live master:** `16fb9ca9` — help-wanted live status on top of `1bfcad2` (#710) / `2e4f59aa` (#707)  
**Priority hub:** Issue #175

Rewrite this file every admin session. Copilot is optional peer, not a promote gate. Size ≠ quality. Promote when dual-gate is green **and** the diff is an extract, not a mega. Vercel rate-limit is non-gate. Age alone does not promote. No HITL YOLO to master.

## Landed this window (evidence)

| SHA | What |
|-----|------|
| `16fb9ca9` | help-wanted live status 19:27Z (bot, current tip) |
| `1bfcad2` | #710 session SSOT after #707 |
| `2e4f59aa` | #707 Sentinel nexuscli squash |

#711 is the prior 12:16 PDT session pulse (base `1bfcad2`, mergeable_state=unstable while dual-gate settles). This file supersedes the 10:09 and 12:16 matrix text vs current tip.

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
| #711 | WAIT | 12:16 session pulse; 4 files; rebase onto `16fb9ca9` then dual-gate |
| #682 | EXTRACT / WAIT | ML keep-alive DAG (#175). ~130 files. Prefer slimmer `ml/pipelines/` child onto this tip. `ml/` still absent on master. |
| #680 / #708 | OBSERVE | Bolt live_catalog_feed family. Do not double-merge. |
| #702 | OBSERVE | Gravitee observatory seed |
| #684 | HOLD | unify Actions cadence; dirty vs tip |
| #685 / #695 | OBSERVE | proposal + Paper2Agent research |
| #543 | OBSERVE | skill definition quality lane |
| #630 | EXTRACT | Jules dashboard rich UI — minesweeper |
| #432/#549/#601 | EXTRACT | ML wholesale family — keep-alive is #682 tree |
| #705/#706/#709 | SUPERSEDE | older session rewrites vs post-#710 tip |

## Ancient / wrong-base HOLD

#47 OBSERVE/SUPERSEDED. #48 HOLD (base master-staging). #69 HOLD (feature base). #73 HOLD. #81 OBSERVE. Do not close-as-superseded until extract lands.

## Issue → PR map

| Issue | Role | Linked |
|-------|------|--------|
| **#175** | OPERATOR matrix + dual-gate | #432 #549 #601 #682 (ML); #630 minesweeper; #707/#710 landed; #711 WAIT |
| #184 | Credential inventory (notes only) | secrets hygiene |
| #117 | Agent2Agent / MCP Agent Mail | #143 |
| #50 | termux-smoke / master-staging gate | dual-gate ancestry |
| #21 | oldest production backlog | pre-matrix |

## Next cycle

1. Leave #682 EXTRACT until a slimmer `ml/pipelines/` child is cut onto `16fb9ca9`.
2. Wait dual-gate on this session PR before promote. Do not merge #711 until rebased + green.
3. Stay busy on SSOT / skill mirrors / extract inventory. No HITL YOLO merge.
