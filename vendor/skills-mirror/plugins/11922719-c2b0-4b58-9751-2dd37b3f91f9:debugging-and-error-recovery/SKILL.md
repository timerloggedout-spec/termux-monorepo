---
name: debugging-and-error-recovery
category: Engineering
description: "Root-cause debugging. Use when a test fails, a build breaks, behavior doesn't match expectations, or any unexpected error appears. Builds a loop that goes red on the failure before theorising, ranks falsifiable hypotheses, and ends with a regression test.\n"
---

# Debugging and Error Recovery

When something breaks: stop adding features, preserve the evidence, and find the
root cause before touching the fix. The sections below are ordered by what
actually goes wrong here — the instrument lying to you, the symptom being scoped
to the wrong layer, and a hypothesis that explains only part of the picture — all
of which precede the mechanical triage loop.

## The Stop-the-Line Rule

When anything unexpected happens:

```
1. STOP adding features or making changes
2. PRESERVE evidence (error output, logs, repro steps)
3. DIAGNOSE using the triage checklist
4. GUARD FIRST — write a failing regression test that pins the bug, and watch it fail
5. FIX the root cause (turn that test green)
6. RESUME only after verification passes
```

**Don't push past a failing test or broken build to work on the next feature.** Errors compound. A bug in Step 3 that goes unfixed makes Steps 4-6 wrong.

## Check the instrument before believing the measurement

The most expensive debugging sessions in this repo's history all share one shape:
**the measurement was wrong, not the system.** Before forming a hypothesis about
the code, establish that the thing telling you something is broken is itself
working.

Recorded instances, each a real hour-plus detour:

- A query API read an **index that lags ingest** — it returned 0 results for the
  last 60s while the pipeline was perfectly healthy. Nearly reported as "I broke
  ingestion."
- A service appeared in the tracing UI **as soon as its SDK connected**, having
  emitted zero spans — presence in the list proved nothing.
- A test runner **reported SUCCESS for something that never ran** (wrong config
  root, zero tests collected, green exit code).
- A delegate reported a dependency missing; it was a genuinely incomplete install
  in the shared `node_modules`, not the sandbox limitation it pattern-matched to.

**Rails:**

- Ask "what would this tool show me if the system were healthy?" — if the answer
  is "the same thing," the tool cannot support your conclusion.
- Prove your detector on a **known-good** case before trusting it on the suspect
  one. A grep that finds nothing may have a broken pattern; a suite that passes may
  have collected nothing. Check the count, not just the exit code.
- A result that contradicts a diagnosis you're confident in is a reason to check
  whether the tree was stable when you measured, not to abandon the diagnosis.
- **Two bumps is the smell that you're guessing.** If raising a limit "fixed" it
  once and you're reaching for the dial again, you never found the cause.

## Scope the symptom before you debug it

Before opening the thing that reported the error, establish *what layer owns the
symptom* and *whether the input ever arrived*. Both of these have cost whole sessions.

- **Ask which layer owns the symptom, not which tool you were handed.** The tool that
  surfaced an error is frequently innocent; debugging it means debugging the messenger.
  Name the layers the symptom crosses and find the one that can actually produce it.
- **Check the input exists before debugging the machine.** A pipeline that reports
  nothing may be perfectly healthy with an empty inbox — a timeout on an effect whose
  cause never fired carries no information at all, and cannot distinguish a broken
  system from an un-started one. Confirm the trigger before instrumenting the effect.
- **When a symptom CHANGES with no code change, suspect ordering and shared state — not
  drift.** A test or endpoint that fails differently on each run is telling you about
  sequence and shared mutable state, and chasing it as a moving regression will not
  converge.
- **Mass-skipped tests are the tell for a load artifact, not a regression.** A sudden
  cliff of skips (rather than failures) usually means the environment fell over, not that
  behavior changed.
- **"Can't reproduce" plus "the tool works now" means the ENVIRONMENT changed.**
  Timestamp the original report against the config's git log — the fix often already
  landed, and the mystery is a stale report rather than a live bug.

## Hypothesis discipline

- **Two failed fixes on one premise: test the premise.** When two fixes rest on the
  same assumption and both fail the same check, write the assumption down and test it
  directly before attempting a third. (Adapted 2026-10-17 from pstack's
  `principle-attack-the-premise`, MIT.)

- **A theory that explains SOME observations is not the cause.** Partial explanatory
  power is the most common way a debugging session commits early to the wrong mechanism.
  Require the theory to account for *every* observation, including the inconvenient ones,
  before acting on it.
- **When a symptom has two candidate mechanisms, find the ONE artifact that separates
  them** — don't reason from the symptom, which is by definition consistent with both.
- **A dismissed hypothesis that returns with new evidence needs its OWN fresh check.**
  "I already ruled that out" was true against the *old* evidence; the new evidence is
  exactly what invalidates the earlier dismissal. Re-test it rather than reusing the
  verdict.
- **Rank 3–5 falsifiable hypotheses before probing any of them.** Write each as a
  prediction — "if X is the cause, then changing Y makes the bug disappear" — most
  likely first, and change one variable per probe. A hypothesis with no prediction
  cannot be ruled out, so it never leaves the list; a single hypothesis anchors you
  on it.
- **Prefer non-mutating observation first — the probe can BE the fix.** A read-only look
  at real state frequently resolves the question outright, and never leaves you unable to
  tell your own change from the original behavior.
- **Verify library internals against the installed source, never from memory.** Read the
  actual code in `node_modules` (or the vendored copy). Versions differ from your
  recollection, and a confident wrong belief about a dependency's behavior is expensive.
- **When an error names a missing symbol, read the symbol tables** rather than inferring
  from backtraces — the direct evidence is available and unambiguous.

## The Triage Checklist

Once the sections above have not explained it, work the loop in order.

1. **Build a red loop.** The step is done when ONE command, which you have run and
   watched, goes red on the user's *exact* symptom — not a nearby failure. No red
   loop, no hypotheses: theorising first is the failure this checklist exists to
   prevent. Make the loop *tight* — seconds, deterministic, runnable unattended —
   because its speed caps how fast every later step goes. Pick the cheapest shape
   that reaches the bug: a failing test, a `curl` against the running service, a CLI
   invocation diffed against expected output, a headless-browser script, a replayed
   request or trace, a throwaway harness around one function, a fuzz loop, a bisect
   script, or a differential run (old build vs new on the same input). A flake's goal
   is a higher reproduction rate, not a single repro: run the trigger 100× in a loop
   or in parallel, add load, or narrow the timing window with injected sleeps.
   Classify a non-reproducing bug before chasing it — timing-dependent,
   environment-dependent (diff versions, env, and *data* — empty vs populated), or
   state-dependent (isolation vs after other operations; shared caches and
   singletons). "Truly random" is usually one of those three not yet found. If no
   loop can be built from here, stop and ask for what is missing — access, an
   artifact (a log, a HAR, a dump), or permission to run something — rather than
   debugging blind.
2. **Localize.** Name the layer that owns the symptom before opening anything —
   see *Scope the symptom* above. For a regression, `git bisect run <test-cmd>`
   answers "which commit" faster than reading will.
3. **Reduce.** Strip to the minimal failing case: remove one element at a time
   (an input field, a config line, a step, a dependency), re-run the loop, and keep
   the cut only if it stays red. Done when every remaining element is load-bearing.
   A minimal reproduction is what makes the root cause obvious instead of arguable.
4. **Write the failing regression test FIRST and watch it fail** — red before
   green, for the bug's *exact* symptom. Mechanics and the proof that the test is
   load-bearing live in [tdd-skill](../tdd-skill/SKILL.md); do not re-derive them here.
5. **Fix the root cause, not the symptom.** Before editing a shared function,
   grep every caller: one fix in the shared code beats a patch at each call site, and
   the caller list is what else your fix changes.

## Instrumentation Guidelines

**Logging conventions defer to the [monitoring](../monitoring/SKILL.md) skill** — discover the project's
logger and mirror it (structured logger, levels, request context). Bare
`console.log` is never the answer.

Add instrumentation when you cannot localize to a line, when the issue is
intermittent, or when several components interact. Remove it once the bug is
fixed and a test guards it — and always remove anything carrying sensitive data.
Error reporting, API error logging with request context, and key-flow metrics are
permanent and stay.

**Tag every temporary probe** with one session-unique prefix (`[DEBUG-a4f2]`) so the
cleanup is a single grep, not a hunt. When Codex adds the probes, the brief names the
tag, and the review greps the returned diff for it before anything lands.

**Performance regressions take numbers, not logs.** Measure a baseline on the
known-good revision with the same input, then bisect against that number; a log line
tells you where time *seemed* to go, a measurement tells you where it went. Before
claiming a speed-up: name what limits the speed (why isn't it twice as fast?); alternate
the A and B runs, at least five of each, and report median and range; confirm the work
actually ran inside the timed region; and cap any claimed saving at the changed piece's
share of the whole run. (Adapted 2026-10-17 from pstack's `benchmark-checklist`, MIT.)

## Verification

After fixing a bug:

- [ ] Root cause is identified and documented
- [ ] A regression test was written and watched fail BEFORE the fix (red), then passed after it (green)
- [ ] Fix addresses the root cause, not just symptoms
- [ ] All existing tests pass
- [ ] Build succeeds
- [ ] The original bug scenario is verified end-to-end
- [ ] `grep` for the debug tag comes back empty, and throwaway harnesses are deleted
- [ ] The commit or PR message states the confirmed cause, not just the change
- [ ] If no honest seam exists for the regression test (the only reachable one is too
      shallow to fail on this bug), that is recorded as a finding — a test that cannot
      go red on the bug gives false confidence

## Related skills

- [source-driven-development](../source-driven-development/SKILL.md): verify library behavior against the installed source and docs, never from memory.
- [code-quality](../code-quality/SKILL.md): a fix is a diff like any other — the hard rules apply, and *Reviewing a diff* says how error paths are written.

<!-- Red-loop gate, loop menu, ranked hypotheses, debug tags and the no-seam finding are adapted from mattpocock/skills `diagnosing-bugs` (MIT, (c) 2026 Matt Pocock). -->
