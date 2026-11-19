---
description: "Plan-then-dispatch: discovers file:line targets before spawning agents. Prevents context exhaustion from vague scoping. Usage: /dispatch [task description]"
---

Before dispatching any agents, complete the discovery and scoping steps below.

**Task:** $ARGUMENTS

## Step 1: Discovery

Do this yourself — do not delegate discovery to agents.

1. Read the relevant files and identify:
   - Which files need to change
   - What specifically needs to change in each (line numbers)
   - Which changes are independent (can parallelize) vs dependent (must sequence)

2. **Verify existence claims.** If you believe a file, API, convention, or
   config path exists or doesn't exist, check with Glob/Grep/Read before
   building a plan around that belief.

## Step 2: Complexity Check

If discovery reveals any of the following, stop and recommend `/build` instead:
- More than 10 files need changes
- Changes have complex interdependencies across modules
- You'd describe the task as "fix the bugs" rather than "apply these specific fixes"
- Understanding the codebase is a prerequisite for knowing what to change

Tell me why you're recommending `/build` and wait for my decision.

## Step 3: Scope Agents

For each agent you're about to spawn, verify:
- [ ] The prompt includes specific file paths and line numbers
- [ ] The agent touches a small number of files (prefer ≤5; more is fine if files are small)
- [ ] No two parallel agents edit the same file
- [ ] The task is specific enough that the agent won't need to explore to understand it

If a check fails, re-scope: split into smaller agents or sequence instead of parallelize.

## Step 4: Dispatch

Spawn agents with the scoped prompts.
- Prefer ≤3 parallel agents for file-editing tasks. More is fine when tasks
  are trivially independent and touch non-overlapping files.
- If tasks share files, run them sequentially.

## Step 5: Report

Show me:
1. **Agents dispatched:** count, parallel vs sequential
2. **Scoping rationale:** why you split/grouped tasks this way
3. **File map:** which agent touches which files (confirm no overlaps)
4. **Complexity note:** if this was close to the `/build` threshold, say so
