# Help-Wanted → Evidence Lanes (feed-forward)

**Status:** taxonomy locked; calculation wire thin/partial.  
**Not a new Scout species.** This lane is the **execution arm** of the existing **Oversight** scout.

## Where it sits

From `docs/ops/SCOUT-MISSIONS.md`:

| Scout | Mission | Manager input |
|-------|---------|---------------|
| **Oversight** | Bug Bounty, **Help Wanted**, CTF, skills, performance-test targets | **evaluation opportunities** |
| Performance | Correctness/performance experiments | **MVT proposals/results** |
| Provider Research | Models/quotas/free-trial | candidate roster |
| Code Recon | Commits/PRs/history | implementation evidence |
| Regression | Known-good vs current | regression signal |

Issue **#342** (Evaluations / LeaderBoards / 3L0): Help Wanted becomes a **task family / cohort**, not a random agent label.

Pipeline intent:

```text
task (external issue)
  → claim / upstream-pr (PRIMARY)
  → result (PR URL, merge/close, CI on target)
  → correctness / review signal
  → score (CPPH + outcome)
  → feed-forward (SHE / MoneyBall / 3L0 / manager)
```

Scouts **propose**; managers **decide**. Help-wanted-execute does not grant routing authority.

## What feeds calculations today

| Artifact | Produced by | Feeds |
|----------|-------------|--------|
| `help-wanted-catalog.json` | scout workflow (2h) | selection + CPPH ranking |
| `help-wanted-scout-bench.json` | scout workflow | workbench cadence tuning |
| `help-wanted-daily-budget.json` | execute budget gate | daily production ceiling |
| Upstream PR + claim comments | execute (OPERATOR PAT) | **external outcome evidence** |
| Actions job timestamps | durable GHA API | SHE `job_timestamps` / failure rates |

**Gap (honest):** benches are not yet auto-ingested into SHE priority matrix or MoneyBall score tables. Hex (free trial) was a **visualization** path once; durable calc path is **SHE + Actions runs/jobs + dated artifacts** (`ACTIONS-METRICS-INTEGRATION.md`), not a third-party BI trial.

## MVT / DOE relationship

| Layer | Role |
|-------|------|
| Oversight (this lane) | Supplies **evaluation tasks** (real FOSS issues) |
| Performance scout | Proposes **MVT/DOE experiments** on providers/models |
| MoneyBall / 3L0 | Scores repeated success → admission |

External help-wanted work is a **live evaluation cohort**: same agent/provider can be scored on claim→PR→accept latency and correctness. That is DOE-relevant **task material**, not a separate scout title.

## Title guidance

| Use | Do not use |
|-----|------------|
| **Oversight scout** (population) | “Help-Wanted Scout” as a 6th species |
| **help-wanted lane** (execute arm) | New parallel scout roster row without manager policy |
| **evaluation cohort / task family** (#342) | Treating CPPH score as MoneyBall admission |

CPPH ranks **issues**. MoneyBall ranks **providers/agents after repeated task success**.

## Next wire (thin)

1. On execute success/fail → append event to dated evidence JSON under `docs/ops/generated/`.
2. Optional: SHE observer row from budget ledger (used/success/fail).
3. Manager policy: promote top external outcomes into continuous-evaluation cohorts.
4. Keep Hex/BI as optional human view only — no dependency for scoring.

## Related

- `SCOUT-MISSIONS.md` · `SCOUT-ROSTER.md`
- `HELP-WANTED-LANE.md` · `HELP-WANTED-PARALLEL.md`
- `ACTIONS-METRICS-INTEGRATION.md`
- Issues #337 Continuous Evaluation · #342 Evaluations/3L0 · #357 attribution

BIUDL. Agent-Identity: Grok (Administrator)
