---
name: write-plan
description: Write zero-ambiguity implementation plans with actual code in every step. Each task has Goal, File (exact path), complete Code block (no placeholders), Verify command, and Checkpoint. Use before /execute-plan to ensure step-by-step clarity.
argument-hint: "[feature or task description] [@path/to/project] [--output=plan.md] [--tdd]"
allowed-tools: Bash(python *)
---

# Write Implementation Plan

Write a detailed, zero-ambiguity plan for implementing a feature. Each task is self-contained and executable.

## Context Extraction

Analyze the codebase to extract framework, language, and patterns:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/plan_writer.py" --phase=analyze --project "$ARGUMENTS"`

## Plan Writing Instructions

Write your plan with this mandatory structure for **every task**:

```markdown
## Plan: [Feature Name]

### Context
- Framework: [detected]
- Language: [detected]
- Integration points: [list]

### Tasks

#### Task 1: [Name]
**Goal:** one sentence describing what this task accomplishes
**File:** exact/path/to/file.py
**Code:**
```python
[actual code — complete functions/classes, NOT pseudocode or "..."]
```
**Verify:** exact command to confirm this task is done (e.g., `pytest tests/test_feature.py -v`)
**Checkpoint:** what you will check before proceeding to Task 2

#### Task 2: [Name]
...
```

## Validation

Validate the plan for completeness:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/plan_writer.py" --phase=validate --plan="$PLAN_TEXT"`

**Blocking rules:**
- Every task MUST have Goal, File, Code block, Verify, Checkpoint
- Code blocks MUST contain actual code — NO "...", "TBD", "[placeholder]", "[TODO]"
- Every task MUST be independently executable and verified

## Estimation

Estimate execution time:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/plan_writer.py" --phase=estimate --plan="$PLAN_TEXT"`

## Next Step

After validating the plan, invoke:
```
/one-shot-prompting:execute-plan [plan-file.md]
```

---

**Superpowers Skill:** Part of structured development methodology. Pairs with execute-plan for task-by-task implementation.
