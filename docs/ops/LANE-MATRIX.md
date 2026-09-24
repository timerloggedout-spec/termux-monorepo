# LANE-MATRIX (living SSOT)

**Session:** 2026-09-24 10:07 PDT  
**Agent-Identity:** Grok (Administrator)  
**Live master (base):** `fdc5d534` (#808 MERGED — agent-quality-lane post-merge trigger)  
**Priority hub:** Issue #175  
**Credential SSOT:** Issue #184 (names only; never paste secrets)

Rewrite this file every admin session. Copilot / CodeRabbit / Devin / Qodo are **advisory peers**, not promote gates. Vercel rate-limit is non-gate (#772). Age alone does not promote.

**BIUDL = Broad → Integrate → Validate → Develop → Learn.**  
**Operating posture:** Continuous Fully Automated Agentic Development. Agents auto-promote when dual-gate + task-outcome evidence is verified on the candidate SHA.  
**Sovereignty:** ArchWiz cockpit + chat remain the human goal/constraint surface.

## Policy realign (still in force from 05:39 PDT)

| Rule | Correct reading |
|------|-----------------|
| **Mega-merge** | **Allowed** when dual-gate SUCCESS + mergeable on the candidate SHA. |
| **CodeRabbit ~100 files** | **Advisory review capacity** — not a repository promote ban. |
| **Size ≠ quality** | File count is **context only**. |
| **dirty / conflict** | **Hard block** until rebase/re-cut onto live base. |
| **Vercel rate-limit** | Non-gate (#772). |
| **HOLD / OBSERVE / WAIT** | Not idle parking. WAIT = collect evidence → promote when ready. |

## Status this cycle

- **#808 MERGED** `fdc5d534` — Agent Quality Lane now runs on `push` to `master` and `master-staging`. Dual-gate on `cbb6a3be`: repo-gate run `36024573291` SUCCESS, termux-smoke run `36024572948` SUCCESS. Combined `mergeable_state=unstable` was Vercel rate-limit only.
- **#807 MERGED** `28cd7b24` — mega-merge + CodeRabbit advisory policy.
- **#805 MERGED** `def12264` — llm-api-hub standalone core from #48 provenance.
- **#810** pulse on superseded tip `28cd7b24` — close as SUPERSEDED after this pulse is dual-gated.
- **#48** still open, base `master-staging`, `mergeable_state=dirty` → **not ready**. Remainder EXTRACT; core already on master via #805.
- #69 SUPERSEDED after #784. #787 dirty EXTRACT until re-cut.

## Landed this window (evidence)

| SHA / PR | What |
|----------|------|
| `fdc5d534` / #808 | post-merge Agent Quality Lane trigger |
| `28cd7b24` / #807 | mega-merge policy realign |
| `def12264` / #805 | llm-api-hub standalone extract |
| `7ec65ebe` / #797 | prior LANE-MATRIX pulse |
| `2982f05e` / #794 | FOSS foresight extract |
| #784 | Debate-dock; supersedes #69 |

## Dual-gate contract

1. `hygiene + portability gate` / `repo gate` SUCCESS on **this** SHA
2. `agentic termux smoke` / `termux smoke` SUCCESS on **this** SHA
3. Vercel rate-limits are **non-gate**
4. Copilot / CodeRabbit / Qodo / Devin = advisory only
5. GitLab / Mintlify = non-gate
6. Age alone does not promote
7. **Mega OK** when dual-gate + mergeable; CodeRabbit 100-file limit is advisory
8. `mergeable_state=dirty` **or merge conflict** blocks promote — rebase/re-extract
9. Dual-gate SUCCESS on an older head does not authorize promote after master moves
10. Combined commit status SUCCESS is not dual-gate; bind named jobs to **this** SHA

## Tip-first active lanes

| PR | Lane | Why |
|----|------|-----|
| #808 | **MERGED** | post-merge quality lane; dual-gate on `cbb6a3be` |
| #807 | **MERGED** | policy |
| #805 | **MERGED** | hub standalone |
| #48 | WAIT / conflict | dirty vs `master-staging`; extract remainder |
| #810 | SUPERSEDE | pulse on pre-#808 tip |
| #787 | WAIT / conflict | stale dual-gate SHA; re-cut onto tip |
| #788 | open | TER-15 Linear; base `master-staging` |
| #785 | open | Wingman submodule |
| #69 | SUPERSEDED | Closed after #784 |

## Issue → PR map

| Issue | Role | Linked |
|-------|------|--------|
| **#175** | OPERATOR matrix + dual-gate | #808 MERGED; #48 dirty WAIT; this pulse |
| #184 | Credential inventory (names only) | OPERATOR / ARCHWIZ / GH_PAT / VERCEL_TOKEN names |
| #772 | Vercel rate-limit non-gate | mergeable_state instability |
| #50 | termux-smoke / master-staging gate | dual-gate ancestry |

## Next cycle

1. Dual-gate this policy pulse; promote if both named jobs SUCCESS on **this** SHA.
2. #48: do not mega-merge while dirty. Remainder extract only.
3. Close #810 as SUPERSEDED once this pulse is open (this PR).
4. Re-cut #787 onto live tip when capacity allows.
5. Stay busy on SSOT / production while CI waits — WAIT is not idle.
