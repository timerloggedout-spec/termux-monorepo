---
description: Manage your plugin autonomy level (operator → collaborator → consultant → approver → observer). Each level relaxes user-approval gates. Promotion is suggested after 5/20/50 clean sessions.
argument-hint: "[get-level | suggest-next | set-level --level <name> [--lock]]"
allowed-tools: Bash
destructive: true
read-only: false
---

Manage autonomy level:

!`python "${CLAUDE_PLUGIN_ROOT}/skills/one-shot-generator/scripts/autonomy_level.py" --repo-root . $ARGUMENTS`

The 5 levels (from Anthropic's autonomy framework):

| Level | Gates relaxed | Recommended after |
|---|---|---|
| **operator** | nothing | first 5 sessions |
| **collaborator** | dry-run auto-approved | 5+ clean sessions |
| **consultant** | --apply auto-approved (non-migration) | 20+ clean sessions |
| **approver** | migrations auto-approved | 50+ clean sessions |
| **observer** | full autonomy | explicit opt-in only |

Destructive operations (rm, drop tables, force-push) always require
explicit yes — even at observer level.
