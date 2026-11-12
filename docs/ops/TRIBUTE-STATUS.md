# Tribute — Living Status & Human Review

**SSOT board (generated):** `docs/ops/generated/tribute-status.md`  
**Machine:** `docs/ops/generated/tribute-status.json`  
**Receipts:** `docs/ops/generated/tribute-evidence/*.jsonl`  
**Public dashboard:** `apps/tribute-dashboard/` → canonical Pages route `/tribute/`; Vercel **tribute-oversight** remains an implementation/deployment identifier.

Regenerate:

```bash
python3 scripts/ci/tribute_status.py
cp docs/ops/generated/tribute-status.json apps/tribute-dashboard/data/status.json
```

## Why this exists

Help-wanted is an **Oversight + evaluation** arm that also produces real external PRs.
This is **not** MoneyBall admission.

## Working well with others

| Rule | Behavior |
|------|----------|
| Claim idempotent | One claim marker; re-runs skip post |
| Closed issues | Default **skip** |
| Maintainer routing | Prefer upstream / feature fork when directed |
| Stake ≠ fix | Replace stake or close |

## Follow-up loop

1. Scout → claim once → upstream PR (or FALLBACK)
2. Evidence JSONL
3. `tribute_status.py` rebuilds board + dashboard snapshot
4. Vercel serves `apps/tribute-dashboard`

BIUDL. Agent-Identity: Grok (Administrator)

## Outcome SLO

Receipts are not outcomes. `outcomes.actioned/skipped/failed` count lane
receipts (a skip is an "ok" observation), which is how the page could show
"Failed 0" while the lane had zero real merges. The honest numbers come from
`scripts/ci/tribute_outcomes.py`:

- Census: `is:pr author:timerloggedout-spec -user:timerloggedout-spec` in three states (merged, closed-unmerged, open).
- Each merged PR is classified from its diff and merger: **real merge** (foreign maintainer, non-placeholder diff, weight 1),
  **stake-only merge** (only `.github/help-wanted-lane-stake.md`-style files, weight 0, never a win),
  **self merge** (merged by the author into an org the author runs, excluded). Closed-unmerged = failure (weight -1).
- System 1 decisions (latest per thread, from branch `tribute-s1/backfill`) add yielded / retired / dropped counts.
- Windows 7/14/30/90 days; the SLO window is 30 days.

SLO status **FAIL** when any of: zero real merges in 30d; real merge rate
(real / (real + stake + closed-unmerged)) below 10% over at least 10 decided
PRs; last real merge more than 21 days ago. **WARN** when stake-only merges or
closed-unmerged PRs exist. Never "0 failures": `outcome_failures` = SLO
failures + closed-unmerged PRs in the window.

Wiring: `tribute-status-refresh.yml` runs the census and merges
`tribute_outcomes` / `outcome_slo` into `status.json` (the dashboard KPI cards
read them) and writes `docs/ops/generated/tribute-outcomes.{json,md}`.
`tribute-outcome-slo.yml` runs after every refresh and turns a FAIL into a red
run with `::error` annotations. Tests: `tests/test_tribute_outcomes.py`
(fixture = live census snapshot 2026-11-12).
