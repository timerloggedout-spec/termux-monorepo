---
name: audit-loop
description: "Run a continuous audit-fix-audit loop that scores a codebase and automatically fixes gaps until a target score is reached. Use when the user asks to \"get us to 10/10\", \"keep improving until perfect\", \"run a continuous improvement loop\", \"audit and fix automatically\", or wants an autonomous cycle of scoring, generating fix tasks, executing them, and re-scoring.\n"
metadata:
  version: "0.1.0"
---

# Audit-Fix Loop

Set up and run a self-sustaining loop that audits a codebase, generates fix tasks for remaining gaps, executes them, and re-audits until the target score is reached.

## How It Works

Each round:
1. **Wait** - polls for any running overnight runner to finish
2. **Audit** - Claude CLI audits the codebase, writes a report, outputs `OVERALL_SCORE=X.X`
3. **Check** - if score >= target (default 10.0), exit success
4. **Generate** - Claude CLI reads the audit, creates a task queue for remaining gaps
5. **Fix** - the overnight runner executes all tasks
6. **Repeat** from step 1

## Starting the Loop

```bash
nohup bash devops/cloud-coder/audit-fix-loop.sh > /tmp/audit-fix-loop.log 2>&1 &
```

## Audit Dimensions

The audit scores 7 dimensions (1-10 each):
Security, Reliability, Observability, Testing, Infrastructure, Code Quality, Compliance

## Key Design Decisions

- Uses claude-sonnet-4-6 for audits and queue generation (fast, cheap)
- Score comparison uses `awk` to avoid bash integer arithmetic issues with decimals
- Each round writes a separate audit file for historical tracking
- The runner runs in foreground within the loop so it blocks until complete
