---
description: Show empirical track record of local + external agents. Surfaces top-rated agents, recent failures, and drift detection — driven by .claude/registry/learnings.jsonl which run_finalize.py writes after every /one-shot.
argument-hint: "[top-agents [--limit N] | rate --agent <id> | export-anonymized]"
allowed-tools: Bash
destructive: true
read-only: false
---

Inspect the cross-agent learnings registry:

!`python "${CLAUDE_PLUGIN_ROOT}/skills/one-shot-generator/scripts/learnings_hub.py" $ARGUMENTS`

## What lives in the registry

Every `/one-shot` run ends with `run_finalize.py` recording one row per
spawned agent in `.claude/registry/learnings.jsonl`. Each row:

```json
{"ts": "...Z", "agent_id": "local/architect",
 "task_keywords": ["shopping", "cart", "discounts"],
 "outcome": "succeeded" | "failed" | "inconclusive",
 "duration_ms": 0, "cost_usd": null,
 "notes": "verdict=SHIPPED;iterations=0"}
```

## Useful queries

```bash
/learnings top-agents --limit 10        # Highest-rated agents
/learnings rate --agent local/architect  # Drill into one agent
/learnings export-anonymized > learnings.json  # For community sharing
```

## Rating formula

```
overall = 0.5 * success_rate
        + 0.3 * sample_factor   (saturates at 10+ samples)
        + 0.2 * recency_factor  (1.0 today → 0.5 after 30 days → ~0 after 180)
```

Use this to spot drift: if `local/architect`'s `overall_rating` drops
below the historical baseline, something changed (a SKILL.md edit, an
agent.md regression, a model swap). Investigate before the next big run.

For raw rows, `cat .claude/registry/learnings.jsonl`. The file is
append-only — never rewrite it; let history speak.
