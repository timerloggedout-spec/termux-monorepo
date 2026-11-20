---
name: pointer-handoff
description: Use at the start of any session on an ongoing project to recover where the work stands, and at the end of a session (or on any significant discovery) to record it — maintains a single short pointer file holding current state and the next action, so a fresh session with empty context resumes without re-deriving months of work from git log.
---

# Pointer Handoff

Long-running work outlives any single session. The **pointer** is one short file
holding *where the work stands right now* and *what to do next* — the first thing
read at the start of a session and the last thing written at the end.

It holds state, nothing else:

- **Not lessons learned.** Those belong in a lessons store, retrieved by topic
  when relevant — a lesson about rollup semantics has no business loading when
  the task is writing user documentation.
- **Not direction or architecture.** Those live in the roadmap and
  `system-profile.md` from `concept-briefing`.
- **Not history.** The pointer is overwritten each time; its history is the git
  history of the file itself.

## The File

Default location `docs/STATUS.md`. If the project already keeps a
pointer somewhere else, use that — one pointer per project, never two (one per
coordinator on a multi-lane project, see below).

```markdown
**Cập nhật:** YYYY-MM-DD · <evidence: version / test counts / HEAD>

## Đang ở đâu
- Giai đoạn: <phase or workstream>
- Nhánh / HEAD: <sha>, đã push chưa
- Trạng thái kiểm chứng: <test x/y, deployed version, health check>

## Đang dở
<What is half-done, in what state, which files. Empty if nothing is.>
<Per dispatched task not yet Done: task · state · executor · run id · where to
read the result · what you do when it lands.>

## Cảnh báo đang mở
<Red tests not yet fixed, decisions taken but unverified, data under suspicion.
Each with the evidence that raised it. Empty if none.>

## Nợ còn lại
1. <deferred work, numbered, each with enough context to act on>

## Việc kế tiếp
<One concrete action, specific enough to start immediately — including "switch
to a different project" when that is the truth.>
```

Prose in the project's working language. Keep it to one screen or so: this file
is read at the start of every session, so its length is a recurring cost.

## Reading It (start of session)

1. **Read the pointer first**, before exploring code — it tells you what the code
   won't: which decisions are already settled, what is under suspicion, what was
   deliberately deferred.
2. **Then reconcile against reality.** `git log` since the pointer's date, branch
   state, whether the deployed version matches. **A pointer is routinely stale by
   a few commits or a few days** — someone finished work and didn't write it
   down, or the session was cut short.
3. **Where they disagree, reality wins** — and fix the pointer immediately, don't
   carry the discrepancy in your head for the rest of the session.
4. If the pointer names documents to read first, read them before starting work.

Never treat the pointer as proof of current state. It is a starting hypothesis
with evidence attached, and the evidence is checkable — that is the point of
recording test counts and SHAs rather than adjectives.

## Writing It (end of session, and mid-session on discovery)

Write at the end of every session, **and immediately when something significant
surfaces mid-session** — a red test, a wrong assumption confirmed, a decision the
user made. A session that ends abruptly loses whatever was only in context.

**Dispatching a task is significant.** Record the run under *Đang dở* as soon as it
is running (states per `orchestrating-executors`), and update it when the state
changes — not on a timer while nothing moves. Waiting for an executor is a good
moment to write. If the executor is running but its monitor failed, write both
facts; a label that hides a live process is how a task gets dispatched twice.

On Claude Code a Stop hook holds the turn once when HEAD is 3+ commits past the
pointer's last update. The reminder is not the update: write the state, or say
why nothing in the pointer changed.

Every claim carries evidence:

| Instead of | Write |
|------------|-------|
| "Fixed the rollup bug" | "Rollup CLI exits cleanly — ran 3 days, exited in 24s, commit `99a80fc`" |
| "Tests pass" | "Full suite 2051 passed / 0 failed on HEAD `<sha>`" |
| "Deployed to dev" | "Dev on `v0.11.1`, `/health/ready` 200" |
| "Data looks better now" | "trades 37.510 → 82.485 after reload; `invalid_rows` 36 → 0" |

An adjective in a pointer is a claim the next session cannot check. Numbers,
SHAs, and command output are.

**Overwrite, don't accumulate.** Replace what is no longer true instead of
appending a new dated section under the old one. When the next session wants
history it reads `git log` on this file — which is why the commit message
matters: `con tro: <what changed>` (or your project's equivalent), one line.

**Close things out explicitly.** A resolved warning gets deleted, not left with
"(fixed)" beside it. A paid-off debt item disappears from the list. Anything
still listed is still live — that contract is what makes the file trustworthy.

## Suggesting a Fresh Session

A long session degrades: early detail crowds out the current task. Once the context
passes **about 300k tokens** (or the threshold the working agreement sets), look for
a clean point to hand over to a new session — but only when the pointer can carry
everything that matters:

- *Việc kế tiếp* is concrete and startable.
- No investigation half-done, no hypotheses held only in context — converge first,
  or write them into *Cảnh báo đang mở* with their evidence.
- The last task is accepted and committed; every running executor is listed.

At that point write the pointer, then **suggest** the new session to the user; the
session does not end itself. Compaction is the strongest signal — suggest it at the
next clean point. `multi-lane-coordination` applies the same rule to headless lane
runs, where the reset happens without asking.

## Multi-Lane Projects

When the working agreement runs several lanes (`multi-lane-coordination`), there is
one pointer **per coordinator**, each with one writer:

- **The Chief's pointer is the project pointer** — same path, same format, plus a
  lane board under *Đang ở đâu*. It holds each lane's state, not its detail:

  ```markdown
  ## Bảng lane
  | Lane | Nhánh @HEAD | Trạng thái | Inbox / outbox | Việc Chief đang nợ |
  |------|-------------|------------|----------------|--------------------|
  | billing | lane/billing @a1b2c3d | chờ job 2 executor | in #7 · out #9 | — |
  | search | lane/search @e4f5a6b | câu hỏi #4 chờ user | in #3 · out #4 | hỏi user về index |
  ```

- **Each lane's pointer** lives in the shared state directory, not in any branch
  (`<project-root>/.crewmarshal/lanes/<name>/STATUS.md`), in the format above plus
  the last inbox entry it has handled. Only that lane writes it; the Chief reads it.

Reconciling works the same way at both levels. The Chief compares each lane's
pointer with the real HEAD of its branches — a branch several commits past its
pointer usually means a run stopped dirty. A lane run reconciles its own pointer
against its branch before trusting it.

## What Doesn't Go In

| Content | Where it belongs |
|---------|------------------|
| Lessons, recurring traps, "don't trust this signal" rules | Lessons store, retrieved by topic |
| Phase structure, what unlocks what | Roadmap (`concept-briefing`) |
| Scale, trade-off priorities, hard boundaries | `system-profile.md` (`concept-briefing`) |
| Design decisions and their rationale | The spec for that work |
| A narrative of what happened this session | Nowhere — record the resulting state |

The temptation is to let the pointer absorb everything, because everything feels
relevant at the moment of writing. It isn't relevant at the moment of *reading*:
next session opens with a specific task, and a pointer carrying every lesson from
every past phase costs context on all the ones that don't apply.

## Red Flags

| Thought | Reality |
|---------|---------|
| "Pointer says the branch is clean, so it is" | Reconcile with `git log` first. Pointers go stale silently. |
| "I'll write the pointer at the end" | Write it when something significant surfaces. Sessions end without warning. |
| "'Fixed the export bug' says it all" | Next session can't check an adjective. Give the number, the SHA, the output. |
| "I'll add a new section for today's session" | Overwrite. The file is state, not a log — git holds the history. |
| "This lesson is important, into the pointer it goes" | Important and *relevant to the next task* are different. Lessons are retrieved by topic, not carried by default. |
| "Leave the old warning with '(resolved)' next to it" | Delete it. Anything still listed reads as still live. |
| "Nothing changed, no need to touch it" | Then confirm the date and evidence still hold. A pointer nobody updated looks identical to a pointer nobody trusts. |
