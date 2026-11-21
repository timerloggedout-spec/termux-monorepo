---
name: handoff
category: Workflow
description: "Durable session handoff with a resume prompt. Use when pausing or ending work at a real boundary (a phase or PR done, a blocker, a pivot, a drained queue) or when the user says \"hand off\" or \"we'll continue later\". Saves state outside the chat plus an exact resume point, never just a chat summary. No new resume prompt needed? Use done.\n"
---

# Session Handoff

Goal: a brand-new session (possibly a weaker model) can resume this work with zero
re-discovery. The test of a good handoff: could someone who never saw this chat
pick up the exact next action and trust what's already done? Chat history does not
survive — anything not written to memory, a handoff file, or the repo is lost.

## Write-through, not stop-at-a-threshold

The old "hand off at ~50% context remaining" rule is retired: every session boundary
costs the user an action (this install's resume surfaces are in `LOCAL.md` beside this
skill, when your copy keeps one, *Why a session boundary costs a click*).

Compaction is only lossy when the durable state lives in the chat. So keep it out
of the chat: **write state through to memory / the handoff file / the repo
continuously, as decisions land and units complete — not in a burst at handoff
time.** With state already written, an auto-compact is a non-event: the summary
was never the record. This is the structural fix that lets one session run long
and cross many queue items before a real boundary.

**The discipline (do this DURING the work, every session):**

- The moment a decision is made, write it (+ rationale) to the durable record.
- The moment a unit lands, commit it and note status/verification in the record.
- The moment you defer something, put it in the follow-ups tracker.
- The moment a lesson lands (a gotcha, a disproven assumption, a better approach),
  append it to the relevant skill's `LEARNINGS.md` — same turn, not at handoff. In
  a long session, a lesson from hour one can be compacted away before any handoff
  runs; the end-of-session pass cannot harvest what context no longer holds.
  **Then commit + push that append immediately** — if your project has a fast path
  for append-only journals (e.g. direct to `main`, `git add <that file> && git
  commit && git pull --rebase && git push`, with `merge=union` absorbing concurrent
  appends), use it; this install's rule is in `LOCAL.md` beside this skill, when your
  copy keeps one (*Committing a learning append*). A learning written but not pushed
  is durable on one machine only.
- **Re-consult the relevant skills at each queue-item pickup.** A skill read at
  session start may have been compacted away by item #4 — session ≠ task anymore,
  so skill loading is per-item, not per-session. Never rely on a skill consulted
  before an earlier compaction.
- Never let "what we already tried / ruled out / decided" exist only in context.

Do NOT stop making progress at a context percentage. Let auto-compact happen and
keep working — the write-through record carries across it. The one thing to avoid
is being mid-edit at a compaction: land or WIP-commit the in-flight unit, then
continue.

## When to actually hand off (a real boundary, not a timer)

- The user says to stop, hand off, or switch focus.
- A multi-phase program completes a phase, or the work hits a blocker that needs
  the user.
- The queue is drained, or you're pivoting to unrelated work.
- Genuine context exhaustion where write-through can't keep the thread coherent —
  rare, and a symptom of state leaking into chat rather than a routine trigger.

**The trigger is "did this session learn something the next one needs?", not "did
files change?"** A session with zero commits still needs the full record — and is
often the one that needs it most, because it leaves no artifact in the repo to
reconstruct from. A pure sysadmin session over SSH produced no diff and yet held a
permanent constraint (a package that can never build on that OS version), a version
pin that would silently break later, and two hours of environment gotchas that would
otherwise be rediscovered identically. Git being clean is a fact to *state* in the
handoff, not a reason to skip it — and never manufacture a commit to feel
productive. Record how a working system **breaks**, not just that it works.

## Reconcile with reality before you write the record

The single most repeated failure in this journal: writing the handoff against the
remembered state instead of the true one. After a compaction, or alongside a
concurrent session, **the disk is routinely ahead of your in-context narrative.**

- **Open the handoff by re-querying git and PR state**, before writing any status
  and before any reset or force-push: `git fetch`,
  `git log --oneline -10 origin/main`, `git rev-parse HEAD origin/<branch>`, `gh pr list`. The in-chat story once
  said "1.3 not started" while `git log` showed 1.3a merged and 1.3b committed.
  Another session wrote "Phases B & C remaining" when other sessions had already
  merged both — handing that off would have sent someone to rebuild finished work.
- **A PR can merge mid-handoff.** "Build complete, awaiting review" becomes "merged"
  between your last push and the wrap-up, and the whole framing (resume vs done)
  hinges on it. Worse, a sweep commit made *after* the merge on the now-merged branch
  is orphaned — it needs a fresh branch off `origin/main` and its own PR.
- **Treat the end-of-work git/PR sweep as a fact-check, not cleanup — and run it
  BEFORE writing status into memory.** One session drafted "PR green, awaiting the user's
  merge"; the sweep revealed the user had already merged it, and three memory files plus
  the index asserted the stale state.
- **Re-probe a precondition you probed earlier in the same conversation.** They flip
  mid-session: a "blocked on Node v12" finding was v22 by the handoff turn, because
  the app had relaunched the conversation under a fresh process. The honest answer
  may be "already unblocked — land the unit instead of handing it off."
- **Any claim about deployment, environment, or another repo rots within days.**
  Timestamp it and say how to re-verify: "NOT deployed (as of `<date>`; re-verify:
  `<command>`)". A brief asserting "the team's config repo is a git repo with no
  remote" was false by pickup, which changed both what was possible and what was
  *confidential* to write (the original example: `LOCAL.md` beside this skill, when
  your copy keeps one, *Stale environment-claim example*). When a handoff's premise is a deploy or env state, the resume step's first
  action is the re-verify command, not the action.
- **`git merge-base --is-ancestor` cannot prove merged-ness in a rebase-merge
  repo** — SHAs are rewritten, so it reports "not merged" for branches that are.
  Compare content (`git diff origin/<branch> origin/main`) or read the PR state, and
  when in doubt don't delete.

## You are not the only session in this repo

Concurrent sessions share the checkout, the trackers, and sometimes the worktree you
think is yours. Every rail here is a collision that actually happened.

- **`git fetch` before the FIRST edit to a shared file, not before the commit.** By
  commit time you have authored against a fiction and the rebase is a section-sized
  conflict. One session edited a plan's `## Workstream 2` outline that another had
  already replaced with a full spec — the Edit tool matched cleanly because the local
  base was consistent, so nothing warned until the rebase.
- **Know which drift each guard catches.** The Edit tool's "modified since read"
  guard fires on **local file** drift only. Git-tracked files whose drift is on
  `origin` look clean to it — nothing is locally modified. **Memory file → the Edit
  guard; plan file in git → `git fetch`.** Neither covers the other.
- **Treat every shared-tracker edit as read-modify-write** and reconcile the other
  session's entries rather than clobbering them. Reading the follow-ups tracker at
  handoff once surfaced an entire concurrent program whose slices invalidated
  standing instructions in every brief written that night.
- **`git worktree list` reveals the other sessions and where they are.** Run it
  first. "Isolated" worktrees can silently host two sessions; check `git status` for
  sequencer state (rebase in progress, `MERGE_MSG`) before any git mutation, and if
  another session's operation is in flight, stop touching the tree.
- **The branch, plus its last pushed SHA, is the durable resume pointer — the
  worktree path is advisory.** Worktrees get commandeered, deleted, and swept out
  from under you; recovery is trivial *only* because the branch was fully pushed.
- **Sweep what you created; surface the rest.** Do not prune other sessions'
  worktrees, branches, or databases. Anything you did not just create is occupied.
- **Once you post a resume chip, finish your handoff from the main checkout.** A
  successor started immediately, ran its own end-of-work sweep, and removed the
  predecessor's worktree mid-handoff — the shell's cwd vanished. Prefer sweeping
  *then* chipping.

## What makes a handoff claim trustworthy

A handoff is read by someone with no way to check you. Its claims must carry their
own evidence.

- **Distinguish what THIS session verified, and by what method, from what it
  INHERITED.** A brief said in bold *"Root cause is VERIFIED, don't re-derive"* — and
  it was half wrong: a different element was broken. The claim had been copied
  forward and re-bolded across three handoffs, and the instruction not to re-derive is
  exactly what stopped anyone noticing; the disproving check took three minutes.
  "Verified 2026-07-14 by reading the compiled CSS" is auditable; a bare "VERIFIED" is
  an appeal to authority that outlives its evidence. **A claim copied forward gaining
  emphasis but never a new measurement is the highest-risk line in the brief —
  re-measure it *because* it is load-bearing.** Scope "don't re-derive" to expensive
  research, never to the diagnosis a fix depends on.
- **State the verification method, not just the result.** "2 modules committed, 135
  tests green" reads as finished; "green against mocks, never live-run" is the truth,
  and the live proof belongs in the resume points. Say which path/theme/case you
  actually checked — "verified dark theme only, here's why, residual risk low" beats a
  reflexive "both" that quietly isn't true.
- **Record what is UNVERIFIED as loudly as what is done.** If a missing credential
  makes the happy path silently degrade to a fallback, that is a blocker, not a
  footnote — it makes a broken feature look successful.
- **Write corrections in place, as corrections.** "An earlier draft said X; that was
  wrong, because Y" is worth more than the corrected fact, because otherwise the next
  session re-derives the wrong version from the same sources. Strike a stale claim **in
  the block where it lives**, not only where you noticed it — a correction filed
  elsewhere leaves a booby-trapped paragraph for whoever finds the original first.
  Mark superseded lines; don't delete the reasoning.
- **Measure, don't estimate — and label estimates as estimates.** Verify sub-agent
  claims before propagating them: three agents disagreed on a file count (12 vs 34)
  and a one-line grep said 39. Agents are a research multiplier, not an authority.
- **Close entries in the same pass that finishes the work.** A stale "🔴 IN PROGRESS"
  is the costliest handoff failure: the index still said the live tier was red and
  being fixed after it was fixed, merged, and green. A follow-ups tracker is only
  trustworthy if items *leave* it — one stale 🔴 devalues every other one. Search
  memory for the task's own framing before closing out, since the stale claim is
  usually phrased in the words of the ticket you were handed. And record **why** it
  stayed open, not just that it's shut.

## The handoff sequence

Run these in order — each step protects the next session from a specific loss.

### 1. Land the in-flight unit — never hand off mid-edit

Finish or cleanly park the current unit of work: code compiles, tests you ran are
noted, changes are **committed** on the work branch (uncommitted edits in a shared
tree can be destroyed by another session switching branches). If the unit can't be
finished, commit it as clearly-marked WIP and say exactly what's incomplete.

### 2. Sweep loose ends the same turn you notice them

Anything deferred, undecided, or orphaned goes into the project's follow-ups
tracker (e.g. an `open-followups` memory/file) NOW — not "later". Deferred items
that live only in your head are deleted with your context.

### 3. Write the handoff record

Update the durable record — a memory file (Claude Code auto-memory) and/or
`.ai/handoffs/<task-or-branch>.md` in the repo when that convention exists
(per-project locations that differ are in `LOCAL.md` beside this skill, when your
copy keeps one, *Where handoff records live*). It
must contain, concretely:

- **Status** — what is DONE (and verified how) vs IN PROGRESS vs NOT STARTED.
- **Decisions + rationale** — every decision made this session and why, so the
  next session doesn't re-litigate or silently reverse it.
- **Changed files and commits** — branch name, commit hashes, PR links/numbers.
- **Verification results** — what was tested/run and the outcome; explicitly list
  what is UNVERIFIED.
- **Blockers** — with exactly what input/event unblocks each.
- **The exact next action** — a command or edit the next session can execute
  first, not "continue the work". Vague resume points are the #1 handoff failure.
- Convert relative dates ("yesterday", "next week") to absolute dates.

The record's skeleton, with step 6's Skills Review as its last section:

```markdown
# Handoff: <task or branch> (<YYYY-MM-DD>)

## Status
- DONE: <item>, verified by <command or check, and its result>
- IN PROGRESS: <item>, <exactly where it stands>
- NOT STARTED: <item>

## Decisions
- <decision>. Why: <rationale>

## Changes
Branch `<branch>`; commits `<sha>` <subject>; PRs <link or number>; files <paths>

## Verification
- Ran `<command>`: <outcome>
- UNVERIFIED: <what was not tested or run>

## Blockers
- <blocker>. Unblocked by: <the exact input or event>

## Next action
<the command or edit to execute first, never "continue the work">

## Skills Review
- ✅ / ⚠️ / ❌ <skill>: <one-line finding>
```

### 3b. Refresh the project-atlas vault note (when the user keeps one)

Some users keep a cross-project atlas — e.g. an Obsidian vault holding one note per
project. Its location is whatever the user's profile or settings record (this
install's location, note path and schema: `LOCAL.md` beside this skill, when your
copy keeps one, *Project-atlas vault note*); if no atlas is recorded, skip this step.
If the session materially changed any documented project — feature/phase/PR
landed, status or blockers shifted, production/tracker/people/conventions
changed — update that project's note the same turn you write the handoff
record:

- Refresh the **Status** section and any changed open-item callouts (the
  user-owned blockers lists especially — the atlas doubles as their cross-project
  "waiting on me" view).
- Bump the note's last-updated date — it is what a staleness view over the atlas
  keys on.
- Keep the note's frontmatter schema intact — any index or query over the atlas
  depends on it.
- A project with no note yet: create one following an existing note's shape and
  link it from the atlas's home note.
- When the atlas is an LLM-compiled wiki (the LLM-knowledge-base pattern: raw
  records compiled into linked pages with an index), also file the session's durable
  decisions and lessons into it from their raw records, then run its lint.

This is a summary-level refresh from what the session already knows — do NOT
launch repo-wide research for it. (A full re-research sweep is a separate,
user-requested "refresh the atlas" task.)

### 4. Shut down what you started

Kill dev servers, watchers, and local services this session launched. A handoff
means bringing the environment down to neutral — the next session will bring up
what it needs.

**Sequence this AFTER your last gate, not before.** Step 4 once ran while the
session's own full test suite was still executing and killed it at 301/294 files
with zero failures — destroying the summary block and leaving the branch's headline
gate unconfirmed. The trigger is "nothing is still running that I need a result
from": let in-flight gates finish, or explicitly record what they had proven at the
moment you killed them.

**The inventory is wider than dev servers.** Each of these outlived a session:

- **Daemons spawned by CLI tools you invoked**, not just servers you started — one
  call to a delegate agent's CLI can silently start a broker, an app-server, and a
  helper host. `ps aux | grep <tool>` before archiving, and identify ownership by the
  daemon's `--cwd`/pid-file args: concurrent sessions run identical binaries, so
  only kill your own.
- **Background wait-loops.** They have no port and no output, so nothing reminds
  you. 🚨 `until ! pgrep -f "agent exec"; do sleep 5; done` **can never exit** — the
  loop's own shell has that string in its command line, so `pgrep -f` matches
  itself. Two were still spinning hours after the delegate finished, and they made
  the session believe it was still running. Match on something that can't self-match
  (`pgrep -f "[a]gent exec"`), check the task's actual artifact, or just use the
  harness's completion notification instead of polling. Check with
  `ps -eo pid,etime,command | grep -E "until|sleep"` and `TaskStop` any harness
  tasks still listed. (The tool names these were first recorded against: `LOCAL.md`
  beside this skill, when your copy keeps one, *Delegate-agent daemons and
  wait-loops*.)
- **Background agent jobs**, which can spawn minutes *after* their wrapper returns
  and edit files under you — re-check the job list rather than trusting a wrapper's
  "finished".
- Kill by PID or port, not by a guessed pattern: `pkill -f "vite --port X"` misses
  the process, because the real command line is `node …/vite.js --port X`. Use
  `lsof -ti:<port> | xargs kill -9` and verify the port is free.

### 5. Git end-of-work sweep

Run the git-sync skill's end-of-work sweep: everything committed and pushed (when
a remote exists), merged branches pruned, merged worktrees removed, shared
checkout left pristine on its main branch.

### 6. Skills Review — the final section of every handoff

Review the session's work through the lens of each skill that actually applied
(code-quality, frontend, tabler-ui, git-sync, tdd-skill, service-architecture,
design-guide, …). For each applicable skill give a verdict — ✅ good / ⚠️ note /
❌ issue — plus a one-line finding. If a skill surfaces a real follow-up, add it
to the handoff's resume points. Skip skills that don't apply; don't pad.

In a long multi-item session, don't save this all for the end — run it at each
completed phase/PR boundary while the work is fresh, and let the handoff-time
review cover only what's landed since the last one.

**Then review the environment, not the work.** The Skills Review grades what was
built; this asks what made building it slower or riskier than it needed to be. Read
the session (the transcript, not your memory of it — see step 7) and list findings
**most severe first**, each with a proposed change, under these headings — skip any
with nothing in it:

- **Navigation** — information that took long to find; a pointer that would have saved it.
- **Automated checks** — a mistake a lint, type check, test or hook could have caught,
  or a repo with no guardrail at all. Check the repo's own check command first: an
  existing check that sits unwired or silently broken is the finding.
- **Standards** — a review miss. A **mechanical** miss (a banned API, an import shape,
  a file location) gets a deterministic check — a lint rule, a hook, a CI step —
  never a new prose rule; prose is for genuine judgement calls only.
- **Steering files** — a rule in `AGENTS.md`/`CLAUDE.md` or the global rulebook that
  belongs in a check or a skill instead, or that changed nothing (a no-op).
- **Tool economy** — an expensive call or tool that a cheaper route would have replaced.
- **Information access** — something the session needed and could not see (logs,
  read-only access to a service).

Each finding becomes a resume point, a learnings entry, or a proposed PR — never a
rule edited in place.

### 7. Per-skill learnings sweep

Learnings are captured **write-through** — appended to the relevant skill's
`LEARNINGS.md` the same turn they land (see the write-through discipline above).
This step is the safety net, not the capture mechanism: sweep for any straggler
the session learned but didn't write (dedupe against what's already there; tag
project-specific items). If this sweep regularly finds much to add, the
write-through discipline is slipping — fix that, don't grow this step.

**Sweep the transcript on disk, not your context**, with targeted searches for
corrections, stated preferences and reversed decisions. Run exactly this (the session id
is in any scratchpad or task path already in context; extra arguments are regexes):

```bash
<skill-dir>/scripts/transcript-sweep.sh <sessionId> [extra-regex ...]
```

(`<skill-dir>` is this skill's base directory, which Claude Code prints when the skill loads).

It prints the transcript path it found, every genuine user turn that matches, and a
`<m> of <k> user turns matched` line; a missing transcript is exit 3, never a silent empty
result. Why the file is found this way and what counts as a user turn:
[transcript-sweep.md](transcript-sweep.md).

### 8. Post the resume handoff (when work remains) — route by surface

Route the resume however your harness supports resuming (a saved prompt, a resume
chip, a scheduled task). **Unless the user has asked for auto-resume, do NOT arm
tasks that start follow-on sessions by themselves:** the user starts the next
session, and the handoff's job is to make that start one click. (This install's
routing — which routes are retired, the device setting, the chip and the paste-in
surface — is in `LOCAL.md` beside this skill, when your copy keeps one, *Resume
routing*.)

**When the continuation target is already ALIVE.** If your harness lets sessions
message each other and the work should continue in a session that already exists
(e.g. the session that owns that program), hand the baton by message instead of
starting a new one: point the message at the brief file and the handoff file, exactly
like a resume prompt. Caveats: unattended sessions (scheduled or remotely spawned
runs) may be unable to receive — this route is for attended sessions only — and the
message is an ephemeral chat turn, so the brief file below is still mandatory; the
message only carries the pointer.

First, always write the brief. Then route by the surface the user is on — do NOT ask
when the session already knows it (e.g. from a device setting loaded at session start):

1. **Write the resume brief** to a file outside the chat — a fixed briefs directory,
   `<branch-or-task>-<date>.md` (this install's directory: `LOCAL.md` beside this
   skill, when your copy keeps one, *Resume routing*) — fully self-contained: enter
   the right repo/worktree/branch FIRST, then read the handoff file; include env
   gotchas and the exact first work action. Assume the reader saw none of this chat.
2. **Route the resume by surface:**
   - **A surface that can post a clickable resume** (e.g. a desktop resume chip) →
     post it: imperative title (e.g. "Build phase 5 admin UI"), prompt = fully
     self-contained (point at the brief file AND the handoff file, name the
     worktree/branch, state the first action).
   - **A surface that can't** (e.g. a phone, or a launcher only the user can drive)
     → present the same fully self-contained resume prompt **in a copyable code
     block** as the final message, for the user to paste in themselves. If the launch
     surface is user-only, don't try to invoke it — the deliverable is the prompt
     text, ready to copy. Don't post a chip to a surface that can't show one.

**What the brief must contain, and how chips behave once posted:**
[resume-brief.md](resume-brief.md). Read it before writing the brief: it opens with
a branch verify, works from a fresh worktree, states the blocker above the task and
ends with a `Recommended model:` line; post one chip per stream, in dependency order.

### 9. Archive the session

The final action of a handoff, after everything above is saved, is to archive the
session (Claude Code: `archive_session`). Never archive first — an archived
session can't finish its own handoff.

## Common failure modes

- **Summarizing in chat and calling it a handoff.** If it isn't in memory, a
  handoff file, or the repo, it doesn't exist next session.
- **"Next step: continue implementing X".** Not executable. Name the file, the
  command, the specific edit.
- **Handing off dirty.** Uncommitted changes + shared working tree = another
  session's branch switch silently destroys the work.
- **Skipping the Skills Review / learnings pass** because the session "went
  fine". The pass exists to harvest what went fine into reusable rails.
- **Leaving services running.** The next session (or the user) inherits port
  conflicts and mystery processes.

## Before you call this done

- [ ] In-flight work committed (or WIP-committed with its gap stated)
- [ ] Handoff record has: status, decisions+why, files/commits/PRs, verification
      results, blockers, EXACT next action
- [ ] Loose ends written to the follow-ups tracker
- [ ] Services you started are down; git sweep done; shared checkout pristine
- [ ] Atlas vault note refreshed for every project materially changed (step 3b)
- [ ] Skills Review appended; learnings captured per applicable skill
- [ ] Result held against the owner's judgment lens, when this install keeps one: one read,
      then a check of the work against its top items, each miss fixed or named in the record.
      The lens predicts how the owner judges work; it never approves, decides or speaks for
      them (this install's lens: `LOCAL.md` beside this skill, when your copy keeps one,
      *Owner lens*)
- [ ] Resume routed by surface when work remains — a resume chip, or the copyable
      prompt where the surface can't show one, self-contained either way
- [ ] Session archived (last action)

## Related skills

- [status-update](../status-update/SKILL.md): a dashboard may sit inside the handoff record; it never replaces it.

## Capturing learnings (session-handoff protocol)

Accumulate handoff-quality lessons in `LEARNINGS.md` beside this skill, when your copy
keeps one: resume points
that turned out too vague, state that got lost anyway and why, per-project handoff
file locations. Dedupe and read it before writing the next handoff.

<!-- The environment review's headings and its mechanical-miss-becomes-a-check rule are adapted from mattpocock/skills `retro` (MIT, (c) 2026 Matt Pocock). -->
