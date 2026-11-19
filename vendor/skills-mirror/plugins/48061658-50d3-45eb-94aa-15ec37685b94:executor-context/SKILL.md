---
name: executor-context
description: Use when dispatching work to executors or subagents and the same project conventions keep getting retyped into every prompt — maintains one fixed context file the coordinator writes and updates, so handoffs point at it instead of repeating scope boundaries, code conventions, test rules, and reporting requirements every time.
---

# Executor Context File

Executors and subagents start from zero every time. Without a fixed place to put
project context, the coordinator retypes the same scope boundaries and conventions
into every handoff — expensive, and worse, inconsistent: what gets omitted under
pressure is exactly what the executor then gets wrong.

One file fixes this. **The coordinator owns it**: writes it once, updates it as
conventions emerge, and every handoff points at it.

> Prompt giao việc chỉ cần: *"Đọc `docs/executor-context.md` và `<đường dẫn plan>`,
> thực thi Task N, không commit."*

## Where It Goes

Somewhere the executor can actually open from its working directory — normally
`docs/executor-context.md` at the root the executor is launched in. Verify the
path resolves from *the executor's* cwd, not yours; a file it cannot open is
worse than no file, because the prompt claims context that never arrives.

Keep it short enough to be re-read on every dispatch. Around one screen. It is
loaded far more often than it is written.

## What Belongs In It

Anything true for **every** task in the project. Eight sections, in this order —
each one earned by a real failure mode:

1. **What the project is.** Two or three sentences, plus the stack. Then **the
   handful of facts that govern every decision**, pulled from
   `concept-briefing`'s `system-profile.md`: the real scale, what wins when
   priorities collide, what must never be traded away. Executors over-engineer
   small systems and under-scrutinize critical ones precisely because nobody told
   them which they're in.
2. **Scope boundaries — violating them breaks someone else's work.** A table of
   directories: edit here, read-only there, don't touch that. Plus commands that
   are off-limits (infrastructure, deploys, anything touching shared state).
3. **Code conventions.** Centralized enums, no magic literals, where constants
   live, comment language and style, argument-order traps in shared helpers.
4. **Auto-loading files that must not be edited.** Route registries, test
   runners, anything that discovers files by convention — an executor that
   "registers" a new file manually breaks the mechanism.
5. **Test-group conventions.** How groups declare themselves, what a group must
   never call, which database tests may touch, and the exact commands to run.
6. **How to work.** TDD order if that's the discipline; use the plan's code
   rather than inventing an alternative; **stop and report when the plan is wrong
   instead of improvising**; never edit outside scope just to make lint or tests
   green; commit or don't commit. Role limits and cadence come from the working
   agreement (`project-working-agreement`) — point at its executor part, don't
   copy it.
7. **Running in parallel with other executors.** Whose files are held, and how to
   tell foreign lint/typecheck errors from your own.
8. **What the final report must contain.** Files changed, test results before and
   after with counts, scoped lint result, and — most important — everything that
   looked suspicious or couldn't be decided alone.

Section 6's "stop and report" and section 8's last item are the load-bearing
ones. An executor that quietly fixes what it shouldn't, or files a clean report to
look competent, destroys the finding you most needed.

## On a Multi-Lane Project

Two layers, never two copies. The project file holds what is true for every lane
and is the Chief's (`multi-lane-coordination`). What is true for one lane only —
its scope dirs, its test and build commands — lives in that lane's charter. A
handoff inside a lane points at both by absolute path — the project file sits at the
project root, which in a workspace of several repos is not inside the executor's
repo. Lanes never edit it — a missing convention goes to
the Chief through the outbox.

## What Doesn't Belong

| Content | Where |
|---------|-------|
| Anything specific to one task | That task's handoff prompt |
| The plan itself | The plan file the prompt points at |
| Lessons for one area of the code | `lessons-ledger`, surfaced when work touches that area |
| Current state, what's half-done | `pointer-handoff` |
| Executor invocation commands and quotas | `orchestrating-executors`' roster — that's the coordinator's concern, not the executor's |

The test: **would this apply to every task in the project?** If not, it goes in
the prompt, not here. A context file that accretes task-specific detail stops
being re-readable and starts being skimmed.

## Keeping It Current

**Update the file, not the prompt.** When an executor gets something wrong that
any executor would have gotten wrong, the fix belongs here — adding it to one
prompt fixes one dispatch and leaves the next to repeat it.

Two signals that something must be promoted into this file:

- **The same mistake happened twice**, by any executor. Once is bad luck; twice is
  a missing convention.
- **A lesson in `lessons-ledger` applies to every task**, not just one area. Then
  crystallize it here as a rule — the ledger keeps the evidence and the reasoning,
  the context file carries the imperative. A rule like "never call the test
  runner's stop hook — the groups after it will operate on a closed connection"
  belongs in both: the ledger says why and what proved it, this file just says
  don't.

Conversely, prune what stopped applying. A convention for a module that was
deleted costs attention on every dispatch forever.

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll paste the conventions into this prompt to be safe" | Then the file is dead and the next prompt will omit something. Point at the file; fix the file when it's incomplete. |
| "The executor should have known that" | It starts from zero every time. If it isn't in the file or the prompt, it doesn't exist. |
| "I'll add this task's details to the context file" | Task-specific content makes the file unreadable for every other task. Prompt, not file. |
| "Second executor made the same mistake" | Stop dispatching and write the convention. You are the constant in that pattern. |
| "The path works from my directory" | Check it resolves from the executor's cwd. A path it can't open silently delivers nothing. |
| "It's long but thorough" | It's re-read on every dispatch. Length here is a recurring tax — earn every line. |
