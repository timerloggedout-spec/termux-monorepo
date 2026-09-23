# LANE-MATRIX (living SSOT)

**Session:** 2026-09-22 23:32 PDT
**Agent-Identity:** Grok (Administrator)
**Live master (base):** `d8ad3521` (`ops(help-wanted): live status refresh 2026-09-23T05:54Z`)
**This PR tip:** `ops/session-lane-matrix-20260922-2332`
**Priority hub:** Issue #175

Rewrite this file every admin session. Copilot is optional peer, not a promote gate. Size ≠ quality. Promote when dual-gate is green **and** the diff is an extract, not a mega. Vercel rate-limit is **non-gate**. Age alone does not promote.

**BIUDL = Broad → Integrate → Validate → Develop → Learn.** Fully Continuous Automated Development Evaluation Environment. **AVOID HITL YOLO MODE YEET AUTOAPPROVE.**

**Status vocabulary (this cycle):** `HOLD` is retired. Use `EXTRACT` (slice then land), `WAIT` (dual-gate named jobs still running or combined status dirty for a non-gate reason), `OBSERVE` (draft / wrong-base / overlapping), or `SUPERSEDE` (older pulse vs live tip). Operator stays ACTIVE. Do not idle.

## Landed this window (evidence)

| SHA | What |
|-----|------|
| `d8ad3521` | help-wanted live status refresh 2026-09-23T05:54Z (Actions bot on master) |
| `cc922521` and later session pulses | prior LANE-MATRIX rewrites; older pulses SUPERSEDE vs this tip |

## Dual-gate contract

1. `hygiene + portability gate` SUCCESS
2. `agentic termux smoke` SUCCESS
3. Vercel rate-limits are **non-gate**
4. Copilot / CodeRabbit / Qodo / Devin = advisory (Devin trial expired is not a gate)
5. GitLab / Mintlify = non-gate
6. Age alone does not promote; dual-gate + rebase onto live master does
7. Size ≠ quality: dual-gate green + 130 files still EXTRACT

## Tip-first active lanes

| PR | Lane | Why |
|----|------|-----|
| **#753** | EXTRACT / WAIT | Vercel master alias in sitemap. Dual-gate named jobs SUCCESS on `4968ffdc`. Combined status `unstable` only from Vercel rate-limit on `termux-monorepo` + `mcp-hub` (non-gate). CodeRabbit later APPROVED. Base SHA `6c4e0c78` is behind live master `d8ad3521` — rebase before promote. |
| **#746** | EXTRACT / WAIT | prior extract sibling; do not double-merge with #753 |
| **#766 / #765 / #759 / #758 / #757 / #754 / #745** | SUPERSEDE | older session pulses vs live tip `d8ad3521` |
| **#764 / #762 / #761** | OBSERVE | drafts |
| **#48** | EXTRACT | wrong-base (`master-staging`). Do not merge as-is. Rebase or child-extract onto master. |
| **#69** | EXTRACT | wrong-base (`feature/proposal-vote-promote`). Same rule. |
| **#587 / #543 / #67 / #81 / #597 / #598 / #617** | OBSERVE | stale or overlapping vs live tip |

## Issue → PR map

| Issue | Role | Linked |
|-------|------|--------|
| **#175** | OPERATOR matrix + dual-gate | #753 extract; session pulses |
| **#184** | Credential inventory (**notes only** — never paste secrets) | OPERATOR token last-used evidence lives in Actions, not issue body |
| #763 | Tailscale hub lane | draft #764 |
| #760 | Desktop Commander fork lane | draft #761 |
| #439 | StepWise MCP | Stepie goals 2087 / 2149 |

## Next cycle

1. Rebase #753 onto `d8ad3521` only if the 4-file extract still applies; then wait dual-gate again.
2. Do not AUTOAPPROVE. Do not merge on Vercel-red combined status without recording the non-gate exception in the promote comment.
3. Stay busy on SSOT / skill upgrades / Stepie notes while CI waits.
4. #48/#69: extract onto master; do not retarget blindly.
