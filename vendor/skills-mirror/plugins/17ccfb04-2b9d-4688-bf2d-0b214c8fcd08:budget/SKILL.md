---
description: Manage the monthly token budget (set, check usage, preflight a generation).
argument-hint: "{set-budget|usage|preflight} [--monthly N] [--tokens N] [--label name]"
allowed-tools: Bash(python *)
destructive: false
read-only: true
---

!`python "${CLAUDE_PLUGIN_ROOT}/skills/one-shot-generator/scripts/cost_management.py" $ARGUMENTS`

Examples:
- `set-budget --monthly 100000` -- cap usage at 100k tokens per month.
- `usage` -- show current month tokens used + estimated USD cost.
- `preflight --tokens 800 --label "auth-endpoint"` -- ask if a generation fits in the remaining budget.
