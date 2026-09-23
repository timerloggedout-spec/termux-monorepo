# LANE-MATRIX (living SSOT)

**Session:** 2026-09-22 20:00 PDT  
**Agent-Identity:** Grok (Administrator)  
**Live master (base):** `6c4e0c78`  
**This PR tip:** `ops/session-lane-matrix-20260922-2000`  
**Priority hub:** Issue #175

Rewrite this file every admin session. Copilot is optional peer, not a promote gate. Size ≠ quality. Promote when dual-gate is green **and** the diff is an extract, not a mega. Vercel rate-limit is non-gate. Age alone does not promote.

**BIUDL = Broad → Integrate → Validate → Develop → Learn.** Fully Continuous Automated Development Evaluation Environment. **AVOID HITL YOLO MODE YEET AUTOAPPROVE.**

**Status change (this cycle):** Operator ACTIVE at 20:00 PDT. #753 remains EXTRACT on live master (`4968ffdc`). Combined status `failure` is Vercel rate-limit on `termux-monorepo` + `mcp-hub` only — **non-gate**. help-wanted-dash + help-wanted-oversight deployed. CodeRabbit approved (advisory). Devin trial expired (advisory). mergeable_state `unstable`. No AUTOAPPROVE. HOLD remains retired as operator idle — WAIT/OBSERVE classify PRs only.

## Landed this window (evidence)

| SHA | What |
|-----|------|
| `6c4e0c78` | live master tip |
| `4968ffdc` | #753 HEAD after master merge; 4 files |
| `b87eb48a` | #758 19:04 pulse (SUPERSEDE after this pulse dual-gates) |
| (pending dual-gate) | #753 Vercel master alias sitemap extract |

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
| **#753** | EXTRACT / WAIT | On live master. Vercel non-gate failures. Promote only after dual-gate jobs named above are SUCCESS on `4968ffdc`. 4 files. |
| **#746** | EXTRACT / WAIT | Slim ML keep-alive + ICM-CCTV. Do not mega-merge #682. |
| **#758** | SUPERSEDE | Prior 19:04 session pulse. |
| **#757/#756/#754/#751/#749/#747/#745** | SUPERSEDE | Older session pulses. |
| **#750 / #755** | OBSERVE | Jules/Linguist peers. |
| **#740** | OBSERVE (draft) | Laya / CADENCE / Jev — keep draft until extract slice. |
| **#617** | OBSERVE | proposal registry manifest gate. |
| **#597 / #598** | OBSERVE | Sentinel/Bolt telemetry family. |
| **#48** | EXTRACT | Dirty vs `master-staging`; 73 files / 6k+ LOC. Slice llm-api-hub health path; do not retarget mega to master. |
| **#69** | EXTRACT | Dirty stacked on `feature/proposal-vote-promote`. Slice `docs/DEBATE` + hygiene onto master. |
| **#81** | OBSERVE | ancient CI promote; wrong-era base. |
| this | SSOT pulse | LANE-MATRIX + skill mirrors + GM assignment map |

## Ancient / wrong-base

#47 OBSERVE/SUPERSEDED. #73 OBSERVE. Do not close-as-superseded until extract lands. #184 credentials = notes only (never paste secret values).

## Issue → PR map

| Issue | Role | Linked |
|-------|------|--------|
| **#175** | OPERATOR matrix + dual-gate | #746 #753 #682 (ML family) |
| #184 | Credential inventory (notes only) | secrets hygiene; OPERATOR PAT in Actions secrets |
| #117 | Agent2Agent / MCP Agent Mail | #— |
| #88/#91/#94 | routing | #48 family |
| #50 | termux-smoke / master-staging gate | dual-gate ancestry |

## Stepie sync

- Goal **2149** Games Masters (primary): taxonomy seed + assignment map present; operator ACTIVE on Conductor duty.
- Goal **2087** termux-monorepo: 1/12 (MCP step done). Next: ICM-CCTV dashboard wire.
- Goal **2151** Marketing: #753 is the Vercel alias extract; still WAIT dual-gate.
- Goal **2152** Agentic moniker env: spec + inventory pending.

## Next cycle

1. Confirm dual-gate job names on #753 HEAD `4968ffdc`; promote only if both SUCCESS.
2. Keep #746 EXTRACT; do not merge #682 mega.
3. Cut #48/#69 child extracts onto master instead of retargeting dirty parents.
4. No HITL YOLO merge. No AUTOAPPROVE.
