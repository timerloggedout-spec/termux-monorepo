# Games Masters taxonomy (seed)

**Session:** 2026-09-22 18:24 PDT  
**Stepie goal:** 2149  
**Status:** seed extract — not a runtime assignment yet

Taxonomy for monorepo lanes. A Games Master (GM) is a **role + duty contract**, not a model brand. Monikers map onto duties; they do not replace evidence gates.

## Roles

| Role | Duty | Lane fit | Promote authority |
|------|------|----------|-------------------|
| Conductor | Select lanes, keep operator ACTIVE, refuse AUTOAPPROVE | LANE-MATRIX / #175 | none — policy only |
| Extractor | Slice mega PRs into dual-gate-sized extracts | #746 vs #682 | none until dual-gate |
| Sentinel | Integrity / symlink / telemetry hygiene | #597 family | advisory |
| Bolt | Fast-path regex / catalog / perf | #598 family | advisory |
| Linguist | CedrLang / 1337speak / docs codec | #755 | advisory |
| Jules | Bounded builder / escalation | peer branches | advisory |
| Palette | PWA / dashboard UX | #140 | advisory |
| Stepie | Goal/step planning surface | goals 2149/2087/2151/2152 | planning only |

## Assignment rules

1. Dual-gate (`hygiene + portability`, `agentic termux smoke`) remains the only promote contract.
2. A GM moniker on a PR does not waive rebase onto live master.
3. WAIT/OBSERVE/EXTRACT describe the **PR**. The operator does not idle.
4. Credential notes stay on #184. Never paste secret values into issues or this file.
5. First experiment lane = help-wanted sitemap / Pages / Vercel alias (#753) plus this taxonomy seed.

## Next evidence

- Map live open PRs to one primary GM each (no double-owners).
- Stand up experiment lane receipt in `docs/ops/generated/` only after a dual-gate green extract lands.
