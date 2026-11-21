---
name: status-update
category: Workflow
description: "Session status as a visual dashboard plus a 2-3 line TLDR, never prose alone. Use on /status-update, \"where are we\", \"what's left\", mid-way through a multi-item run, and at any wrap-up covering more than one unit of work.\n"
---

# Status Update (/status-update)

Goal: make state legible at a glance. This exists because prose recaps of
progress do not register — working memory is small, anything not on screen is
forgotten, and visible progress is what makes work land (where this rule comes
from in this install: `LOCAL.md` beside this skill, when your copy keeps one —
*Output shape*). A status update is a picture of the run, not a story about it.

## The standing rule

**Status is ALWAYS a dashboard plus a 2-3 line TLDR — never prose alone.**

1. **TLDR first, 2-3 lines max.** Verdict-shaped: what just landed, what is
   in flight, what (if anything) needs the user. If a decision is needed, it
   is line one.
2. **Then the dashboard.** One row per unit of work (queue item, PR, phase,
   ticket). Every row carries a state glyph the eye can scan without reading:
   ✅ done · 🔄 in flight · ⏸ blocked (name the blocker) · ⬜ not started ·
   ❌ failed (name the failure). Add columns only if they change what the user
   does next (PR link, verification state, owner).
3. **Nothing else.** Reasoning, caveats, and open questions go after the
   dashboard, in prose, only if they need a decision or change what happens
   next. No play-by-play of how the session got here.

## Channel, by agent and surface

- **An agent with the visualize MCP:** render the dashboard as a
  widget (progress/rollup view) — that is the preferred channel for
  mid-session status. Fall back to a Markdown table when the MCP is absent.
- **Status the user will come back to later** (end of a long
  unattended run, a report referenced across days): publish an Artifact and
  hand over the link; the in-chat dashboard still appears alongside it.
- **Any agent without visual tooling:** a Markdown table meets the
  rule. The rule is dashboard-shaped output, not any particular renderer.
- **External surfaces** (tracker comments, digests): keep the dashboard shape
  but follow [plain-language](../plain-language/SKILL.md) for wording, and make
  zero unverified claims — a reader outside the session cannot question one.
  (This install's agent wording and external-communications rule: `LOCAL.md`
  beside this skill, when your copy keeps one — *Channel*.)

## Row discipline

- **Rows are facts, not hopes.** A row says ✅ only when the completion is
  verified against a real source (tests run, PR checks green, deploy
  observed). An inferred state gets 🔄 with a note, never ✅.
- **Blocked rows name the blocker and the owner** ("⏸ waiting on staging
  approval — user"), so the dashboard doubles as the waiting-on-me view.
- **Position line on multi-step runs:** the TLDR
  restates position every time — "item 3 of 7, X merged, next is Y".
- **Side-quests get a row**, flagged as such (a fallback to a different
  implementer, an unplanned fix), so the dashboard never hides unrequested work.

## Gather the real state first — never render from memory

Pull the live facts before drawing anything: PR/merge state from `gh pr view
--json state,mergeCommit` (never claim "merged" unverified), ticket statuses
from the project's tracker, which background agents/lanes are running vs done,
and the durable queue record (the project's work-queue file or memory) for
decisions (this install's: `LOCAL.md` beside this skill, when your copy keeps one —
*Queue record*).
Round every number; only state what you verified.

**Include each session's state** whenever the dashboard covers sessions,
lanes or scheduled runs: read it live from the control room's status feed
(working, thinking, waiting on you, rate-limited, idle, hung, gone, with the
card each holds and the time in state). Give every session row its state and
time in state, and put each waiting-on-you or hung session in the
waiting-on-you box. A machine whose feed is stale shows its sessions as "last
seen", never as live; an empty feed means nothing is reporting yet, so say so
rather than inferring states from memory (this install's feed: `LOCAL.md`
beside this skill, when your copy keeps one — *Session state*).

## Scope the dashboard to the ask

- "full status" / end-of-batch rollup → the complete board (all workstreams,
  metric cards, every open decision).
- "how's X going" → just X's row/card, its metric(s), and any decision it is
  blocked on. Don't dump everything.
- Nothing changed since the last update → say so in one line and show a
  minimal card; don't re-render a heavy dashboard.

## Widget house style (visualize MCP renderer only)

When the dashboard renders as a visualize widget, follow its design system;
these are hard rules, not taste:

- Call `visualize:read_me` once per session before the first widget — silently.
- **A "waiting on you" box** (`--bg-warning`/`--text-warning`)
  enumerating every open decision — numbered, never collapsed to a count.
- Before/after wins render as `old` (struck, `--text-danger`) →
  `≈new` (`--text-success`) with a `ti-arrow-right` between.

## When NOT to use

- Single-unit answers ("did the test pass?") — answer directly; a one-row
  dashboard is ceremony.
- A handoff or close-out — those run [handoff](../handoff/SKILL.md) or
  [done](../done/SKILL.md), which carry their own record formats; the
  dashboard may appear inside them but does not replace them.
