---
name: systematic-debug
description: 6-phase root cause investigation (mattpocock-inspired diagnose). Build feedback loop → Reproduce → Hypothesize → Instrument → Observe → Fix + Regression Test. Fast, deterministic pass/fail signal is non-negotiable. Generates ranked hypotheses, targeted instrumentation, validates against predictions, fixes only confirmed causes, writes regression tests.
argument-hint: "[error/symptom] [@path/to/project] [--error-log=<file>] [--feedback-method=test|curl|cli|browser]"
allowed-tools: Bash(python *), Read, Write
---

# Systematic Debugging — 6-Phase Diagnosis

**No guessing.** Root cause investigation requires a fast, deterministic feedback loop.
This skill adapts mattpocock's diagnose pattern for generated code failure loops.

## PHASE 0: Build Feedback Loop (CRITICAL)

Before hypothesizing, ensure you have a deterministic pass/fail signal. Ranked by speed:

1. **Failing test** (fastest, deterministic) ✅ Use if available
2. **curl script** (CLI automation)
3. **CLI invocation** (`pytest`, `npm run test`, etc.)
4. **Headless browser** (slower, less deterministic)
5. **Trace replay** (post-mortem analysis)
6. **Throwaway harness** (reproducible code snippet)

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/systematic_debug.py" --phase=build-loop --symptom="$ERROR_DESCRIPTION" --feedback-method="test"`

**[BLOCKED]** If you cannot build a deterministic loop within 2 iterations, escalate: "I cannot construct a reproducible feedback loop for this failure. Recommend HITL [human-in-the-loop] diagnosis."

---

## PHASE 1: Reproduce

Execute the feedback loop and confirm the failure matches user's report:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/systematic_debug.py" --phase=reproduce --feedback-method="test"`

**Checklist:**
- ✅ Error is reproducible (runs consistently)
- ✅ Symptom matches reported behavior
- ✅ Can run loop 100% of the time (not flaky)
- ✅ Document the exact failure signature (line number, assertion, error message)

**[BLOCKED]** Non-deterministic bugs require raising reproduction rate or finding a better signal. If flaky, note: "This test passes ~60% of the time. Need to increase reproduction rate before proceeding."

---

## PHASE 2: Hypothesize

Generate 3–5 ranked hypotheses **before testing**:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/systematic_debug.py" --phase=hypothesize --error="$ERROR_DESCRIPTION" --language="python"`

Output shows ranked hypotheses in **falsifiable format**:
- Hypothesis ID
- Statement: "If <X> is the cause, then changing <Y> will make the bug disappear"
- Confidence (HIGH/MEDIUM/LOW)
- Distinguishing observation (what you'd see if true)
- What you would NOT see if false

**SHARE with user:** Show the 3–5 hypotheses before testing. User can offer domain knowledge that narrows ranking.

**[BLOCKED]** Do not instrument or test until you have documented hypotheses in falsifiable format.

---

## PHASE 3: Instrument

Generate temporary logging code targeting highest-confidence hypothesis:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/systematic_debug.py" --phase=instrument --hypothesis=$HYPOTHESIS_ID --language="python"`

Output shows:
- Logging code (framework-aware: Python logging, structlog, pytest fixtures)
- Exact location to add instrumentation
- **All probes labeled [DEBUG-INSTRUMENT-$ID] for cleanup**

### Apply & Run
1. Add the instrumentation code to suspected location
2. Run the feedback loop (pytest, curl script, CLI)
3. **Copy full output** (stdout + stderr)
4. Proceed to PHASE 4

**RULE:** One variable at a time. If testing multiple hypotheses, do one per iteration.

---

## PHASE 4: Observe

Compare observed output against hypothesis predictions:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/systematic_debug.py" --phase=observe --hypothesis=$HYPOTHESIS_ID --output="$PASTED_LOGS"`

Output shows:
- ✅ **Confirmed hypotheses** (evidence supporting each)
- ❌ **Eliminated hypotheses** (why eliminated)
- Root cause ID
- Recommended fix approach

**[BLOCKED]** Cannot proceed to FIX without one confirmed root cause. If multiple hypotheses tie, instrument the second one and repeat PHASE 3–4.

---

## PHASE 5: Fix + Regression Test

Generate targeted fix **and regression test**:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/systematic_debug.py" --phase=fix --root-cause=$CONFIRMED_CAUSE_ID --language="python"`

Output shows:
- Fix description (why it works)
- Minimal fix code
- Regression test (prevents this specific bug from recurring)

### Apply & Verify
1. **Write regression test FIRST** (before applying fix)
2. Confirm test fails (matches the original bug)
3. Apply the fix (only the confirmed cause)
4. Remove all [DEBUG-INSTRUMENT-*] logging
5. Run full test suite
6. Confirm regression test + all tests pass

---

## PHASE 6: Cleanup + Post-Mortem

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/systematic_debug.py" --phase=cleanup --root-cause=$CONFIRMED_CAUSE_ID`

Output shows:
- Instrumentation removed ✅
- Original reproduction still passes ✅
- Regression test passes ✅
- Post-mortem: what would have prevented this bug?

Document lesson learned: "This bug could have been prevented by: [pattern in code that was missing]"

---

## Iron Rules

1. **BUILD LOOP FIRST** — If no deterministic signal, stop and escalate. Do not hypothesize blindly.
2. **REPRODUCE BEFORE HYPOTHESIZE** — Confirm the bug is real and reproducible before guessing causes.
3. **FALSIFIABLE HYPOTHESES** — Each hypothesis must be testable: "If X is true, then changing Y makes the bug disappear."
4. **ONE VARIABLE AT A TIME** — Change one suspected variable per instrumentation cycle.
5. **HYPOTHESIS RANKING** — Always show user the top hypotheses. Domain knowledge often narrows the cause.
6. **EVIDENCE OVER GUESSES** — Only confirm a root cause after observing predicted logs/state.
7. **REGRESSION TEST BEFORE FIX** — The test that catches the bug should pass only after the fix, not before.
8. **GIVE UP AT 3 CYCLES** — After 3 failed instrument-observe cycles, escalate: "Root cause remains unclear. Recommend HITL review or architectural redesign."

---

**When to invoke:** Skill is triggered when `/one-shot` critic loop encounters test failures or when `/execute-plan` detects unexpected behavior during verification phase.
