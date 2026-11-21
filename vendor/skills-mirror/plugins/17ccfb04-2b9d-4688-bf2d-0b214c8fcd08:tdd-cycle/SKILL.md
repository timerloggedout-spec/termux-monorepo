---
name: tdd-cycle
description: Strict TDD via tracer bullets (mattpocock-inspired). Plan → RED (failing test) → GREEN (minimal impl) → REFACTOR (align conventions) → repeat per behavior. No code before test. Behavior-driven via public interfaces. Vertical slicing prevents hollow test suites. Gates enforce completion before advancing.
argument-hint: "[feature description] [@path/to/project] [--phase=plan|red|green|refactor|repeat]"
allowed-tools: Bash(python *), Read, Write
---

# TDD Cycle — Tracer Bullets via Red-Green-Refactor

**Behavior-driven, not implementation-coupled.** Strict vertical slicing prevents
writing all tests upfront then all code (hollow test suite anti-pattern).

Each feature = one tracer bullet cycle. Repeat per observable behavior.

## PLAN Phase: Align on Behavior

Before writing ANY test, align with stakeholders on observable behaviors:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/tdd_cycle_enforcer.py" --phase=plan --feature="$FEATURE" --cwd="$PROJECT_PATH"`

Output shows:
- **Public interfaces** affected (functions, endpoints, class methods)
- **Testable behaviors** (prioritized by user value)
- **Anti-pattern check:** Are we coupling tests to implementation?
- **Tracer bullet:** Which single behavior should the first test drive?

**Checklist:**
- ✅ User confirms the top priority behavior
- ✅ Test will use ONLY public APIs (no private/internal methods)
- ✅ Test should survive internal refactoring unchanged
- ✅ Behavior is observable (user-facing, not internal mechanics)

**[BLOCKED]** If test would verify implementation details (e.g., "must call _internal_helper()"), redesign before proceeding.

---

## RED Phase: Write Failing Test

Generate a **minimal, focused failing test** before any implementation:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/tdd_cycle_enforcer.py" --phase=red --behavior="$PLANNED_BEHAVIOR" --cwd="$PROJECT_PATH"`

Output shows:
- Test file + location
- Test code (minimal, behavior-focused, no implementation assumptions)
- Expected failure signature
- Run command

### Gate: Confirm Test Fails Correctly
!`[run test command from above]`

**MUST see:**
- ❌ Test fails (not passes, not skipped)
- Correct failure mode (e.g., `NotImplementedError`, `AttributeError`, assertion failure)
- Failure signature matches expected

**ANTI-PATTERN:** If test passes immediately, your test is wrong. Rewrite it to actually test the behavior.

**[BLOCKED]** Cannot proceed to GREEN without confirming test fails for the right reason.

---

## GREEN Phase: Minimal Implementation

Generate the **simplest code** to make the failing test pass. No extra features, no optimization:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/tdd_cycle_enforcer.py" --phase=green --test-file="[test from RED]" --cwd="$PROJECT_PATH"`

Output shows:
- Implementation code (minimal)
- Verify command

**RULE:** Write the bare minimum to make the test pass. If the test only checks "return 5", return 5 (not a parametric function).

### Gate: Confirm Test Passes
!`[run verify command from above]`

**MUST see:**
- ✅ Failing test now passes
- ✅ All other tests still pass (no regressions)
- ✅ Clean test output (no warnings, skips, or errors)

**[BLOCKED]** Cannot proceed to REFACTOR without all tests passing.

---

## REFACTOR Phase: Align with Conventions

**Only after all tests pass:** improve code to match codebase conventions. No behavior changes:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/tdd_cycle_enforcer.py" --phase=refactor --impl-file="[impl file]" --cwd="$PROJECT_PATH"`

Output shows:
- Refactored implementation
- Conventions applied
- Verify command

### Gate: Confirm Tests Still Pass
!`[run verify command]`

**MUST see:**
- ✅ All tests still pass (including the one you wrote)
- ✅ No behavior changed (test names, assertions unchanged)
- ✅ Code is clearer/simpler, not more complex

**GUARD AGAINST:** Premature refactoring. If you refactored too much, revert and try smaller steps.

---

## REPEAT Phase: Next Behavior

After REFACTOR passes, the feature is not done. Proceed to next observable behavior:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/tdd_cycle_enforcer.py" --phase=plan --feature="$FEATURE (next behavior)" --cwd="$PROJECT_PATH"`

**Cycle:** Go back to PLAN and repeat RED → GREEN → REFACTOR for each behavior.

**Example:**
- ✅ DONE: User can create a Todo
- ⏳ NEXT: User can mark a Todo complete  
- ⏳ NEXT: Completed Todos have a timestamp

---

## Iron Rules

1. **PLAN FIRST** — Align on observable behaviors with stakeholders before writing any test.
2. **NO CODE BEFORE TEST** — Test always comes first. If you write code before the test, delete it and start over.
3. **BEHAVIOR OVER IMPLEMENTATION** — Test public interfaces (what users see), not internal mechanics (how it works).
4. **MINIMAL IMPLEMENTATION** — Simplest code to pass the test. No extra features, no optimization, no guessing.
5. **ONE BEHAVIOR PER CYCLE** — If your test name has "and", split it into two tests + two cycles.
6. **VERTICAL SLICING** — Complete one behavior end-to-end (RED → GREEN → REFACTOR) before starting the next. Never write all tests upfront then all code.
7. **VERIFY AT EACH GATE** — Run tests after RED, GREEN, and REFACTOR. Do not proceed without passing.
8. **REFACTOR ONLY AFTER GREEN** — Never refactor before all tests pass.

---

**When to invoke:** Triggered by `/one-shot` implementer + test-author agents, or manually during `/execute-plan` for feature-driven development.
**Pairs with:** [[systematic-debug]] for when tests fail unexpectedly.
