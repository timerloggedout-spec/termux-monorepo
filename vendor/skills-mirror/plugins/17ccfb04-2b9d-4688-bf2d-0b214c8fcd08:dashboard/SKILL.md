---
description: Cross-agent learning hub dashboard — trend analysis + drift detection over a rolling window. Shows which agents are degrading (success rate dropping vs prior window) so you investigate before the next big run. Drives off .claude/registry/learnings.jsonl which run_finalize.py writes after every /one-shot.
argument-hint: "[--window-days N] [--drift-threshold F]"
allowed-tools: Bash
destructive: false
read-only: true
---

Surface trends + drift warnings across the cross-agent learnings hub:

!`python "${CLAUDE_PLUGIN_ROOT}/skills/one-shot-generator/scripts/learnings_hub.py" dashboard $ARGUMENTS`

## What the output tells you

For each agent that ran in the last `--window-days` (default 30):

- `recent_success_rate` — fraction succeeded in the recent window
- `prior_success_rate` — fraction succeeded in the PREVIOUS window (same length)
- `drift` — recent minus prior
- `drift_flag` — one of:
  - **`degrading`** ⚠️ — `drift < -0.15` (15-point drop). Investigate the agent / SKILL.md / model swap that caused this BEFORE the next big run.
  - **`stable`** — drift within ±0.15
  - **`warming`** — recent rate higher than prior (15+ point gain)
  - **`no_baseline`** — agent only has data in the recent window

The `overall` block summarises across all agents and surfaces the count
of `agents_degrading`. If that number is > 0, treat it as a soft halt
on `/one-shot` until you've looked at the drift.

## Tuning

```bash
/dashboard --window-days 7     # tighter window — better for high-velocity work
/dashboard --window-days 90    # broader baseline — better for slow-changing flows
/dashboard --drift-threshold 0.10   # be more sensitive to drift
```

## Related

- `/learnings top-agents` — flat leaderboard by overall rating (no time windowing)
- `/learnings rate --agent local/architect` — single-agent drill-down
- `/learnings export-anonymized` — for community sharing
