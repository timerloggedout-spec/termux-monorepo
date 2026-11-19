---
description: "Three-phase build: Opus plans → Sonnet implements with tests → Opus reviews. Iterates until passing. Usage: /build [task description]"
---

Execute a three-phase build for the following task. This is the
full Plan → Implement → Review → Fix loop.

**Task:** $ARGUMENTS

## Setup

```bash
mkdir -p .claude/plans
```

Generate a slug from the task description (lowercase, hyphens, max 30 chars).
All artifacts go in `.claude/plans/[slug]/`.

## Phase 1: PLAN

Delegate to the `planner` subagent:

"Read this project's CLAUDE.md and understand the codebase conventions.
Then generate a detailed implementation plan for the following task:

$ARGUMENTS

Save the plan to .claude/plans/[slug]/plan.md"

Wait for completion. Confirm the plan file exists before proceeding.

## Phase 2: IMPLEMENT

Delegate to the `coder` subagent:

"Read the implementation plan at .claude/plans/[slug]/plan.md
Read the project's CLAUDE.md for conventions.
Implement everything specified in the plan.
Write all test files.
Run the full test suite.
Save your implementation summary to .claude/plans/[slug]/impl-summary.md"

Wait for completion. Confirm the summary file exists.

## Phase 3: REVIEW

Delegate to the `reviewer` subagent:

"Review the implementation against the plan.
Plan: .claude/plans/[slug]/plan.md
Implementation summary: .claude/plans/[slug]/impl-summary.md
Produce your review and save to .claude/plans/[slug]/review-001.md"

Wait for completion. Read the review.

## Phase 4: FIX LOOP

If verdict is **PASS**: Report success. Show summary.

If verdict is **ITERATE**:
- Extract the fix list from the review
- Delegate to `coder` subagent with ONLY the fix list:
  "Apply these fixes. Run tests after each fix. Save updated summary
   to .claude/plans/[slug]/impl-summary-fix-[N].md"
- Re-run reviewer (save as review-002.md, etc.)
- Maximum 3 fix iterations. If still not passing, stop and report.

If verdict is **REPLAN**:
- Show me the review
- Ask for guidance before re-running the planner
- Do NOT auto-replan

## Final Output

Show me:
1. **Verdict:** PASS/ITERATE/REPLAN (and which iteration)
2. **Test results:** X/Y passing
3. **Files created/modified:** List with line counts
4. **Unresolved items:** Any remaining PLAN_GAP or failing tests
5. **Plan location:** .claude/plans/[slug]/

Keep it brief. I can read the full artifacts if I want detail.
