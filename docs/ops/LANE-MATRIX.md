# LANE-MATRIX (living SSOT)

**Session:** 2026-09-24 05:39 PDT  
**Agent-Identity:** Grok (Administrator)  
**Live master (base):** `def12264` (#805 MERGED — llm-api-hub standalone)  
**Priority hub:** Issue #175  
**Credential SSOT:** Issue #184 (names only; never paste secrets)

Rewrite this file every admin session. Copilot / CodeRabbit / Devin / Qodo are **advisory peers**, not promote gates. Vercel rate-limit is non-gate (#772). Age alone does not promote.

**BIUDL = Broad → Integrate → Validate → Develop → Learn.**  
**Operating posture:** Continuous Fully Automated Agentic Development. Agents auto-promote when dual-gate + task-outcome evidence is verified on the candidate SHA.  
**Sovereignty:** ArchWiz cockpit + chat remain the human goal/constraint surface.

## Policy realign (Operator 2026-09-24 05:39 PDT)

| Rule | Correct reading |
|------|-----------------|
| **Mega-merge** | **Allowed** when dual-gate SUCCESS + mergeable on the candidate SHA. Collaborators routinely hold 100k→1M+ token context. |
| **CodeRabbit ~100 files** | **Advisory review capacity** — not a repository promote ban. Prefer slices when review bandwidth is tight; do not refuse a dual-gate-green mega solely on file count. |
| **Size ≠ quality** | File count is **context only**. It does not block promote and does not force EXTRACT. |
| **dirty / conflict** | **Hard block** until rebase/re-cut onto live base — even if an older SHA had dual-gate green. |
| **Vercel rate-limit** | Non-gate (#772). |
| **HOLD / OBSERVE / WAIT** | Not idle parking. WAIT = collect evidence → promote when ready. |

**Prior drift corrected:** wording that treated “extract not mega” as a hard promote rule is **retired**. EXTRACT remains a useful *tactic* for conflicted or review-bound work; it is not mandatory solely because a PR is large.

## Status this cycle

- **#805 MERGED** `def12264` — llm-api-hub standalone core (6 files) from #48 provenance. Dual-gate on `cd74d607`: repo-gate run `35998910325` SUCCESS, termux-smoke run `35998910398` SUCCESS.
- **#48** still open, base `master-staging`, `mergeable_state=dirty` → **not ready**. Mega-merge fine in principle; conflicts must clear first (update-branch / re-cut).
- #794 / #797 prior production land. #69 SUPERSEDED. #787 dirty EXTRACT until re-cut.

## Landed this window (evidence)

| SHA / PR | What |
|----------|------|
| `def12264` / #805 | llm-api-hub standalone extract MERGED |
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
| #805 | **MERGED** | hub standalone; dual-gate on `cd74d607` |
| #48 | WAIT / conflict | Mega allowed when ready; currently **dirty** on `master-staging` |
| #787 | WAIT / conflict | Stale dual-gate SHA; re-cut onto tip |
| #788 | open | TER-15 Linear; base `master-staging` |
| #785 | open | Wingman submodule |
| #69 | SUPERSEDED | Closed after #784 |

## Issue → PR map

| Issue | Role | Linked |
|-------|------|--------|
| **#175** | OPERATOR matrix + dual-gate | #805 MERGED; #48 dirty WAIT; this pulse |
| #184 | Credential inventory (names only) | OPERATOR / ARCHWIZ / GH_PAT / VERCEL_TOKEN names |
| #772 | Vercel rate-limit non-gate | mergeable_state instability |
| #50 | termux-smoke / master-staging gate | dual-gate ancestry |

## Next cycle

1. Dual-gate this policy pulse; promote if both named jobs SUCCESS on **this** SHA.
2. #48: resolve dirty vs `master-staging` (update-branch or conflict-safe re-cut) → mega-merge when dual-gate green + mergeable.
3. Re-cut #787 onto live tip when capacity allows.
4. Stay busy on SSOT / production while CI waits — WAIT is not idle.
5. Do not treat CodeRabbit file-count as a hard promote block.
