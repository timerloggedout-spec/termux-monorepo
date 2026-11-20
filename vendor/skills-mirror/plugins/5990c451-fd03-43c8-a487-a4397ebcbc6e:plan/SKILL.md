---
description: "Explore, think, and output a structured plan before executing anything. Usage: /plan [task]"
model: opus
---

You are in PLAN MODE. Do not execute any changes. Do not write, modify, or delete any files.

**Task:** $ARGUMENTS

## Step 1: Explore
Use tools freely to understand what's relevant:
- Read files, configs, and existing code related to the task
- Run read-only commands (ls, cat, grep, find, git log, git diff, etc.)
- Check dependencies, interfaces, and constraints
- Do NOT write files or run commands that change state

## Step 2: Plan
Based on your exploration, output:

1. **Goal** — one sentence restatement
2. **What I found** — key files, patterns, constraints discovered
3. **Steps** — ordered list of everything required to complete the task
4. **Risks / ambiguities** — anything uncertain or needing a decision
5. **Complexity** — simple / moderate / complex, with brief reason

## Step 3: Stop
End with exactly: `Plan complete. Reply /build to execute, or ask questions first.`

Do not begin execution. Do not make changes. Wait for confirmation.
