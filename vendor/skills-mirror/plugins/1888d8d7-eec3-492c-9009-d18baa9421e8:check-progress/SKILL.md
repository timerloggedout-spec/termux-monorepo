---
name: check-progress
description: "Check the progress of running Cloud Coder tasks. Use when the user asks \"what's the progress\", \"how's the overnight run going\", \"check on the runner\", \"status update\", \"what tasks are done\", or wants to see which tasks have completed, which are running, and what's left.\n"
metadata:
  version: "0.1.0"
---

# Check Progress

Monitor the status of running Cloud Coder task queues and audit-fix loops.

## Quick Status Check

```bash
# Is the runner still going?
ps aux | grep -E "run-local-overnight|audit-fix-loop|claude" | grep -v grep

# How many tasks completed?
cat devops/cloud-coder/logs/completed.txt 2>/dev/null | sort -u | wc -l

# Latest runner output
tail -30 /tmp/overnight-*.log 2>/dev/null

# Latest loop output
tail -30 /tmp/audit-fix-loop.log 2>/dev/null

# Latest audit score
grep -r "OVERALL_SCORE" backend/docs/prod-readiness-audit-*.md 2>/dev/null | tail -1
```

## Report to the user:
1. Runner status - running or finished
2. Tasks completed - count of unique IDs in completed.txt
3. Current task - most recently started task (from runner log)
4. Failures - any tasks that exited non-zero
5. Score progression - if audit loop is running, show score history across rounds
