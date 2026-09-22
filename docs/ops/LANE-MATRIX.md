# LANE-MATRIX (living SSOT)

**Session:** 2026-09-22 14:04 PDT  
**Agent-Identity:** Grok (Administrator)  
**Live master (base):** `4ae5bb29` (#748 dashboard sitemap surfaces)  
**This PR tip:** `ops/session-lane-matrix-20260922-1404`  
**Priority hub:** Issue #175  
**Credentials:** Issue #184 notes-only — never paste secrets.

Rewrite this file every admin session. Copilot / CodeRabbit / Qodo / Devin are advisory, not promote gates. Size ≠ quality. Promote when dual-gate is green **and** the diff is an extract, not a mega. Vercel rate-limit is non-gate. Age alone does not promote.

**BIUDL = Broad → Integrate → Validate → Develop → Learn.**  
**AVOID HITL YOLO MODE YEET AUTOAPPROVE.**

**Vocabulary:** `WAIT` and `OBSERVE` classify **PRs and bases**, never the operator. The operator is ACTIVE. `HOLD` is retired — wrong-base PRs are **EXTRACT** or **SUPERSEDE**.

## Landed this window (evidence)

| SHA | What |
|-----|------|
| `4ae5bb29` | #748 dashboard sitemap surfaces + crawler policy |
| `7a05922c` | help-wanted live status refresh 2026-09-22T19:54Z |
| `cfa07a95` | help-wanted follow-up evidence 19:54Z |
| `cf8d124` | #742 Action Effectiveness → replay history |
| `9a5beae` | #741 evolutionary replay corpus projection |
| `187e2f9` | #695 Paper2Agent + AlphaEvolve / Dream-RSI |
| `bf45b3e` | #733 help-wanted control surface v2 |
| `4fa585e` | #732 EPS telemetry-first |

## Dual-gate contract

1. `hygiene + portability gate` SUCCESS
2. `agentic termux smoke` SUCCESS
3. Vercel rate-limits are **non-gate**
4. Copilot / CodeRabbit / Qodo / Devin = advisory
5. GitLab / Mintlify = non-gate
6. Age alone does not promote; dual-gate + rebase onto live master does
7. Size ≠ quality: dual-gate green + 100+ files still EXTRACT
8. Wrong base (`master-staging`, stacked feature) cannot promote to `master` — extract instead
9. Combined commit status may be `failure` solely from Vercel; inspect named dual-gate jobs

## Tip-first active lanes

| PR | Lane | Why |
|----|------|-----|
| **#746** | EXTRACT / WAIT dual-gate | Slim `ml/pipelines/` + ICM-CCTV. Dual-gate jobs SUCCESS this cycle. `validate-pull-request` FAILED. Behind tip by #748. Do not YOLO-merge. |
| **#747** | SUPERSEDE | Session pulse vs prior tip `7a05922c` |
| **#724 / #745 / #744 / #729 / #727 / #723** | SUPERSEDE | Older extracts / pulses |
| **#740** | OBSERVE (draft) | Laya / CADENCE / Jev experiment lanes |
| **#739** | EXTRACT | HITL control plane |
| **#717** | EXTRACT | Gantt / PM consolidation |
| **#714** | EXTRACT | stepie-stepwise-ops skill |
| **#630** | EXTRACT | Jules dashboard rich UI minesweeper |
| **#583** | EXTRACT | Grafana MCP boundary |
| **#543** | EXTRACT | skill quality lane |
| **#455** | EXTRACT | mmdc mermaid |
| **#48** | EXTRACT | Base `master-staging` — re-extract hub slice onto live master |
| **#69** | EXTRACT | Base `feature/proposal-vote-promote` — re-extract debate-dock onto live master |
| **#682 / #432 / #549 / #601** | EXTRACT | Wholesale ML family — keep-alive is #746 |

## Issue → PR map

| Issue | Role | Linked |
|-------|------|--------|
| **#175** | OPERATOR matrix + dual-gate | #746 keep-alive; #748 landed sitemap; #48/#69 EXTRACT |
| #184 | Credential inventory (notes only) | OPERATOR PAT is Actions secret |
| #337 | gh-Actions continuous evaluation | dual-gate + validate-PR |
| #439 | StepWise MCP | Stepie goal 2087 / primary 2149 |
| #50 | termux-smoke / master-staging gate | dual-gate ancestry |

## Next cycle

1. Rebase or update-branch #746 onto `4ae5bb29`; wait dual-gate **and** `validate-pull-request`; promote only when green + extract.
2. Open child extracts for #48 and #69 onto live master. Do not retarget ancient bases.
3. Close/supersede stale session pulses after this SSOT lands.
4. Stay busy on skill upgrades + ICM-CCTV (Stepie 10023) while CI waits. No HITL YOLO merge.
5. Stepie: primary goal remains **2149**. Goal 2087 is ops surface only.
