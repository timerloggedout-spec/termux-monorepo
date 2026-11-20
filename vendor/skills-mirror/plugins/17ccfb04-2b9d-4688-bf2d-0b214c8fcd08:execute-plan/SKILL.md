---
name: execute-plan
description: Execute implementation plans task by task. Loads a Markdown plan, executes each task, verifies with provided command, stops on failures. Resumable — if blocked, fix and resume from the failing task. Maintains session state in .one-shot-execute-session.json.
argument-hint: "[plan-file.md] [--start-task=N] [--stop-on-blocker]"
allowed-tools: Bash(python *)
---

# Execute Implementation Plan

Load and execute a plan file task by task. Each task is verified before proceeding to the next. Execution is resumable.

## Load Plan

Parse and validate the plan:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/plan_executor.py" --phase=load --plan "$ARGUMENTS"`

This outputs:
- Task list (JSON)
- Session state initialized at `.one-shot-execute-session.json`

**BLOCKING RULE:** If any task is missing a verify command, execution stops with error message.

---

## Execute Plan (Implemented by Claude)

For each task in the plan:

### 1. Announce
Output: `=== Task [N]/[Total]: [Task Name] ===`

### 2. Implement
Write the file specified in the plan using the **exact code** from the task. Do not improvise or add features — use only what the task specifies.

### 3. Verify
Run the task's verify command:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/plan_executor.py" --phase=verify --task=$TASK_ID --command="$VERIFY_COMMAND" --cwd="."`

**On PASS:** Proceed to checkpoint.
**On FAIL:** STOP immediately. Output the failure. Do not proceed. Pause execution.

### 4. Checkpoint
Mark task complete:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/plan_executor.py" --phase=checkpoint --task=$TASK_ID`

### 5. Next
- If more tasks: `Proceeding to Task [N+1]`
- If all complete: Invoke verify-before-complete before claiming done

---

## Resume After Blocker

If execution pauses due to a failed verify:

1. Fix the issue that caused the failure
2. Resume with: `/one-shot-prompting:execute-plan [plan-file] --start-task=N`

Session state persists, so resuming continues from where it left off.

---

## Completion Gate

Before claiming the plan is complete, invoke:

```
/one-shot-prompting:verify-before-complete @. --gate=all
```

Output must show `overall_status: CLEAR` before task is considered done.

---

**Superpowers Skill:** Pairs with write-plan. TDD/systematic-debug can be invoked mid-execution for specific tasks.
