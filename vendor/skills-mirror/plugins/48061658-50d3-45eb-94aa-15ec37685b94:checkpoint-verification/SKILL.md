---
name: checkpoint-verification
description: Use when accepting an executor's task or about to claim work done — refuses green tests as proof and requires inspecting the call-site and driving the real runtime path to catch missing wire-ups.
---

# Checkpoint Verification

Green tests are not acceptance. The recurring failure (seen 3+ times) is an
executor building each piece correctly but leaving out the link that wires it
into the runtime — and a full e2e suite still passing because the tests insert
straight into the DB or assert on empty setups.

This extends `superpowers:verification-before-completion`. That skill says
"evidence before assertions"; this one says WHERE the evidence must come from
for delegated work: the call-site and the real operational path.

## The Two Non-Negotiables

1. **Inspect the call-site.** For every new function/handler/field the task
   added, find where it is actually called in production code. A function that
   exists but is never reached from a route/job/startup path is dead — a green
   unit test for it proves nothing.
2. **Drive the real runtime path.** Exercise the feature the way the system
   runs it (real request → route → service → DB → response, real job → event →
   consumer), not through a test harness that bypasses the wiring. Paste the
   observed output.

## Checklist

- [ ] Read the diff, list every new symbol (function, field, enum, route).
- [ ] For each, grep for its call-site in non-test code. Flag any with none.
- [ ] Confirm new fields are actually persisted AND re-hydrated (a default on
      the schema can silently mask a missing write — the model hydrates the
      wrong branch).
- [ ] Run the real path end-to-end, not just the unit test. Capture output.
- [ ] If the repo's e2e requires a specific setup order (e.g. drop DB → seed →
      THEN start service), follow it exactly — init state runs at startup.
- [ ] Only then accept the checkpoint.

## Why Green E2E Is Not Enough

- Tests that `insert` straight into the DB skip the write path that a real
  request would use — a missing `is_signed` write is invisible if the test
  never went through the handler.
- A passing suite can still sit on top of dead code and crash-gaps.
- "435/0" or "650/0" green has hidden both dead error codes and unreached
  recovery paths on this project.

## When Verification Catches What Tests Missed

Green tests plus a real defect means the suite is blind to a whole class of bug —
that is a lesson, not just a fix. Record it in `lessons-ledger` immediately, with
the evidence that exposed it. The same blindness will be there next phase.

## Red Flags

| Thought | Reality |
|---------|---------|
| "Suite is green, accept it" | Green over dead code is still dead code. Check call-sites. |
| "The unit test covers it" | Unit tests bypass wiring. Drive the real path. |
| "The field is in the schema, it's saved" | Schema default masks a missing write. Confirm persist + re-hydrate. |
| "e2e failed once, must be flaky" | Reproduce with the exact setup order before blaming flake. |
