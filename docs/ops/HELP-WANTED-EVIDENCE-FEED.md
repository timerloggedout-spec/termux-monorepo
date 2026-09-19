# Help-Wanted → Evidence Lanes (feed-forward)

**Status:** taxonomy locked; **receipt writer live**.  
**Not a new Scout species.** Execute arm of **Oversight** scout.

## Pipeline

```text
task (external issue)
  → claim / upstream-pr (PRIMARY)
  → receipt (JSONL)
  → correctness / review signal
  → score (CPPH + outcome)
  → feed-forward (SHE / MoneyBall / 3L0 / manager)
```

Scouts propose; managers decide. Receipts do **not** auto-admit to MoneyBall.

## Artifacts

| Path | Role |
|------|------|
| `scripts/ci/help_wanted_evidence.py` | Append-only receipt writer |
| `docs/ops/generated/help-wanted-evidence/YYYY-MM-DD.jsonl` | Daily cohort log |
| `docs/ops/generated/help-wanted-evidence/latest.json` | Last event |
| `docs/ops/generated/help-wanted-scout-bench.json` | Scout cadence bench |
| `docs/ops/generated/help-wanted-daily-budget.json` | Daily production ceiling |

Seed: [vedantnimbarte/zero#81](https://github.com/vedantnimbarte/zero/pull/81) as `upstream_pr` primary success.

## Title

**Oversight scout** + **help-wanted lane** + **evaluation cohort** (#342).  
Not a sixth scout species.

## Related

`SCOUT-MISSIONS.md` · `ACTIONS-METRICS-INTEGRATION.md` · Issues #337 #342 #357

BIUDL. Agent-Identity: Grok (Administrator)
