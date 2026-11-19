---
name: done
category: Workflow
description: "Session close-out with no resume prompt. Use on /done, or when wrapping up a session where nothing remains to resume or the continuation prompt already exists (a standup queue's next item). Runs the handoff close-out minus the resume-prompt step. Need a fresh resume prompt? Use handoff instead, never both. In a parent session it closes the child sessions first.\n"
---

# Session Close-Out (/done)

Goal: everything a handoff protects — durable state, skill training, a clean
environment — without producing a resume prompt. This exists because "a prompt
for the next session already exists" is NOT the same as "the session was closed
out properly".

## Relationship to handoff

This skill IS the handoff skill minus one step. Read
[the handoff SKILL.md](../handoff/SKILL.md) and execute its sequence with one
modification:

- **Run steps 1–7 and 9 exactly as written there**: land the in-flight unit,
  sweep loose ends, write the handoff record, refresh the atlas vault note,
  shut down what you started, git end-of-work sweep, Skills Review, per-skill
  learnings sweep, archive the session (last action).
- **SKIP step 8 (post the resume handoff) entirely.** Do not write a resume
  brief, do not post a resume chip, do not produce a copyable resume prompt in a
  code block, regardless of which surface the user is on (this install's brief
  directory and resume surfaces: `LOCAL.md` beside this skill, when your copy keeps
  one, *Resume step skipped*). If a
  continuation prompt already exists, leave it alone — do not regenerate,
  improve, or duplicate it.

All of handoff's discipline still applies verbatim — write-through during the
session, reconcile-with-reality before writing the record, concurrent-session
rails, trustworthy-claim standards, and the failure modes list. /done changes
what you *emit* at the end, not the rigor of anything before it.

## Children first (when this session started other sessions)

A parent session closes out last. Before running any handoff step for itself,
a session that started child sessions runs /done in each of them and waits
until every one is archived. Each child closes out with its own context, its
own record and its own learnings; the parent's record then reports their
outcomes instead of guessing at them. The mechanics for this install are in
`LOCAL.md` beside this skill, *Child sessions*, when your copy keeps one.

1. **Find the children.** A child is a session this one started, still attached
   to it (not moved to top level by the user), and not yet archived. A
   grandchild is its own parent's job: each child's /done runs this same step,
   so the whole tree closes from the leaves up.
2. **No children → skip this section** and run the close-out as below.
3. **Tell each child to run /done**, in one message per child. A child that is
   mid-turn picks the message up when that turn ends.
4. **Wait without polling.** Do not loop or sleep; end the turn and let each
   child's turn-end bring you back. On every return, re-read the children's state
   from the session list, never from a child's message: a child is done only
   when it shows as archived.
5. **A child that ends its turn without archiving is blocked.** It is waiting on
   the user, refused the close-out, or failed. Never archive it on its behalf,
   because that would skip its record and learnings. Name it to the user with a
   link, say what it is waiting on, and stop: the parent's own close-out waits too.
6. **Every child archived → run the close-out for yourself**, starting at
   handoff step 1. The handoff record lists each child and how it closed.

An unattended session (a scheduled run, or one started from a phone) may be
unable to message other sessions. Then list the children in the final message
and stop rather than closing the parent over them.

## Remaining work

Work left on the table does not resurrect step 8. Instead:

- Record it where the next session will actually look: the follow-ups tracker,
  the queue file (if this is queue work), and the handoff record's "exact next
  action" line. The record must still pass the handoff test — a fresh session
  could resume from it — even though no prompt points at it.
- If the pre-existing continuation prompt is now WRONG (the session changed the
  plan, the branch, or the blocker it names), say so explicitly in the record
  and tell the user in the final message that the old prompt is stale — but the fix
  is the user regenerating via /handoff, not /done quietly emitting a new one.

## The final message

End with a short close-out summary: what landed (with PR/commit refs), the
Skills Review verdicts, any learnings appended, and confirmation the
environment is down and the session is archived. No code-block prompt, no chip.
Before writing it, run the owner's-lens line of handoff's *Before you call this
done* list: it applies to /done unchanged.

## Related skills

- [status-update](../status-update/SKILL.md): a close-out covering several units may carry a dashboard; it never replaces the record.

## Capturing learnings

Close-out lessons share mechanics with handoff — append them to
`LEARNINGS.md` beside the handoff skill, when your copy keeps one (tagged `/done`
where the distinction matters) rather than growing a parallel journal here.
