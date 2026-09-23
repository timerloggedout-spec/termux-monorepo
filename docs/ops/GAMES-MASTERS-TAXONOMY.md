# Games Masters taxonomy (seed)

**Session:** 2026-09-22 19:04 PDT  
**Stepie goal:** 2149  
**Status:** seed extract + first assignment map — not a runtime assignment yet

Taxonomy for monorepo lanes. A Games Master (GM) is a **role + duty contract**, not a model brand. Monikers map onto duties; they do not replace evidence gates.

## Roles

| Role | Duty | Lane fit | Promote authority |
|------|------|----------|-------------------|
| Conductor | Select lanes, keep operator ACTIVE, refuse AUTOAPPROVE | LANE-MATRIX / #175 | none — policy only |
| Extractor | Slice mega PRs into dual-gate-sized extracts | #746 vs #682; #48/#69 children | none until dual-gate |
| Sentinel | Integrity / symlink / telemetry hygiene | #597 family | advisory |
| Bolt | Fast-path regex / catalog / perf | #598 family | advisory |
| Linguist | CedrLang / 1337speak / docs codec | #755 | advisory |
| Jules | Bounded builder / escalation | peer branches | advisory |
| Palette | PWA / dashboard UX | #140 / #753 sitemap | advisory |
| Stepie | Goal/step planning surface | goals 2149/2087/2151/2152 | planning only |

## Live assignment map (one primary GM)

| PR | Primary GM | Note |
|----|------------|------|
| #753 | Palette | sitemap + master alias; Conductor owns promote policy |
| #746 | Extractor | slim ML keep-alive |
| #757 and older pulses | Conductor | SUPERSEDE after this pulse dual-gates |
| #597 | Sentinel | do not merge with #598 in one shot |
| #598 | Bolt | telemetry/perf |
| #755 | Linguist | codec surface |
| #48 / #69 | Extractor | dirty parents; child slices only |

## Assignment rules

1. Dual-gate (`hygiene + portability`, `agentic termux smoke`) remains the only promote contract.
2. A GM moniker on a PR does not waive rebase onto live master.
3. WAIT/OBSERVE/EXTRACT describe the **PR**. The operator does not idle.
4. Credential notes stay on #184. Never paste secret values into issues or this file.
5. First experiment lane = help-wanted sitemap / Pages / Vercel alias (#753) plus this taxonomy seed.

## Next evidence

- Dual-gate receipt for #753 HEAD `4968ffdc`.
- Child extract branches for #48 health path and #69 debate TOC.
