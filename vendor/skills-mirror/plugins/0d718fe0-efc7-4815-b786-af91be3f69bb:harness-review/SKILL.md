---
name: harness-review
description: "Assess an existing agentic harness — read-only. Use to review, audit, or assess a harness, to judge how well its skills and agents are actually used, to check drift between the files and the CLAUDE.md record, or to validate that skills trigger and agents wire up. It produces a prioritized review context that hands off to harness-setup, and writes nothing. To build or change a harness, use harness-setup. Not for reviewing ordinary code or a pull request (that is code review)."
model: inherit
disallowed-tools: Write, Edit, NotebookEdit
---

# Harness review — assess an existing harness (read-only)

This skill diagnoses an existing agentic harness and produces a *review context*: a
prioritized account of what works well and what to improve. It is the **reader** half of the
plugin — it writes nothing. The fixes it identifies are carried out by `harness-setup`.

The harness model it assesses against is in `${CLAUDE_PLUGIN_ROOT}/shared/harness-model.md`
(agent = who, skill = how, orchestrator = when/order).

## This skill vs harness-setup

`harness-review` reads and judges; `harness-setup` writes. A request to "review / assess /
audit a harness" or "how well is the harness used" is this skill. A request that creates or
changes anything is `harness-setup`. The output here is a review context that hands off to
`harness-setup` — this skill never applies a change itself.

## The read-only contract

Make no edits — not to `.claude/agents/`, not to `.claude/skills/`, not to `CLAUDE.md`, not
to project memory. Run nothing that mutates the project. When a fix is obvious, write it into
the review context as a recommendation for `harness-setup`; do not apply it. The value of a
reader is that its findings are trustworthy precisely because it changed nothing.

This contract is also backed mechanically: the skill sets `disallowed-tools: Write, Edit,
NotebookEdit`, so those tools are removed from the pool while it runs. `Bash` stays available
for read-only inventory — the prose above still governs it; run nothing that mutates the project.

## Step 1: Inventory the harness

1. List `.claude/agents/` and `.claude/skills/`; identify the orchestrator skill.
2. For each agent, read its frontmatter and role; for each skill, read its name and
   description. Note the declared execution mode.
3. Map which skills each agent uses and how the orchestrator wires them together.

## Step 2: Read the record

Read the harness section of `CLAUDE.md` — the goal, the entry-point directive (the hard gate
routing every prompt through the orchestrator), and the change-history table. The convention is
in `${CLAUDE_PLUGIN_ROOT}/shared/claude-md-pointer.md`. The history tells you how the harness has
evolved and where recent changes concentrated.

## Step 3: Detect drift

Compare three views of the harness:

- the files in `.claude/agents/` and `.claude/skills/`,
- the orchestrator's stated composition,
- the `CLAUDE.md` pointer and change history.

List every discrepancy: an agent or skill present in the files but absent from the record or
the orchestrator; something the record names that no longer exists; an orchestrator that
references a member it never forms. Do not reconcile drift — report it. Reconciliation is a
write, and belongs to `harness-setup`.

**Tracker-sync drift** — when the harness includes a generated `tracker-sync` skill (a
`.tracker-sync/` store at the repo root; model in
`${CLAUDE_PLUGIN_ROOT}/shared/tracker-sync-protocol.md`), read its state read-only and judge
each signal against the sync config (the `mapping.md` under the generated skill):

- **Cursor age vs the configured cadence** — a cursor far older than the cadence means the
  sync is not running.
- **Unresolved conflict count** in `conflicts.md` — a growing log nobody reads is drift in
  the projection.
- **Open-proposal backlog age** in `proposals.md` — an old `open` proposal means a human
  state decision is waiting for adoption while state push stays suspended for that item.
- **Orphan counts** (`orphaned-remote` / `orphaned-local` in `map.jsonl`) — terminal states
  pending a user decision that nobody has made.
- **A stale `reports/` directory** — a schedule is registered but not producing reports
  (or producing only "role unavailable" reports, which points at headless auth).

Each is a finding for `harness-setup` — including "the sync exists but shows no sign of
running at all".

## Step 4: Assess effective usage

Drift tells you what *exists*; usage tells you what is *used*. Judge effective usage from a
fixed, deterministic signal set — read each, infer nothing you cannot ground in one:

- **Project auto-memory** at `~/.claude/projects/<project-hash>/memory/` — what the project
  has recorded about how work actually happens.
- **The `CLAUDE.md` pointer and change history** — whether the entry-point directive is present
  and current (a soft "use the skill for X" trigger instead of the hard gate is itself a finding),
  and what has been changing.
- **The `.claude/` inventory** — what the harness offers.
- **The tools registry**, if present (a `tools.md` in the orchestrator's `references/`
  directory) — which roles are filled by which tools, and their alternatives.

From these, classify each skill and agent as **used**, **unused**, **bypassed** (the work
happens but around the harness), or **drifted** (present but out of sync). When the orchestrator
itself is bypassed — work in its domain happening without it — treat the entry-point directive as
the first suspect: flag it for `harness-setup` to strengthen (hard gate in `CLAUDE.md`, plus an
entry-point description), not just the skill's keywords. Apply the same lens
to registered tools: is each one still used, and is there now a better alternative for its
role? Flag tools that look unnecessary or superseded — as findings for `harness-setup`, not
changes you make. If there is no tools registry at all, treat that as a finding too —
recommend that `harness-setup` offer tool research — since a harness with no considered
tooling is more often an oversight than a decision. The method for reading each signal and
making the call is in `references/usage-assessment.md`. This step is strictly read-only.

## Step 5: Validate

- **Structural.** Agents are files in the right place (including built-in types); skill
  frontmatter has `name` and `description`; cross-references between agents are consistent;
  no `commands/` directory was generated.
- **Triggering.** For each skill description, write should-trigger and should-NOT-trigger
  queries — the should-NOT set built from near-misses, including ones that belong to a
  *different* skill. Confirm the descriptions separate cleanly and don't collide. The method
  is in `references/skill-testing-guide.md`.
- **Effectiveness.** Where feasible, compare the deliverable with the skill against the same
  task without it, to confirm the skill adds value. Also in `references/skill-testing-guide.md`.
- **Dry-run.** Walk the orchestrator: is the phase order logical, do data-passing paths have
  no dead links, does each phase's input match the previous phase's output, is each error
  fallback executable? Check the declared execution mode against
  `${CLAUDE_PLUGIN_ROOT}/shared/execution-modes.md` — in particular, that a team-mode
  harness has the subagent fallback it needs.
- **QA agent, if present.** Check it against the QA methodology — does it compare across
  boundaries rather than only confirm existence, and run incrementally rather than once at
  the end? See `references/qa-agent-guide.md`.

## Step 6: Emit the review context

Produce a prioritized review context — the deliverable of this skill — and hand it to
`harness-setup`:

````markdown
## Harness review: {domain} — {date}

### Works well (keep)
- {finding} — {brief evidence}

### To improve (act on)
| Priority | Finding | Target | Why |
|----------|---------|--------|-----|
| high | {what's wrong} | {agent / skill / orchestrator / CLAUDE.md} | {evidence and impact} |
| medium | ... | ... | ... |

### Drift
- {discrepancy between files, orchestrator, and record}

### Suggested next step
Hand this context to `harness-setup` to act on the "to improve" items in priority order.
````

Order the "to improve" items by impact, name a concrete target for each (so `harness-setup`
knows where the fix lands), and ground each in evidence from the steps above — not in
speculation. Keep "works well" honest: it tells `harness-setup` what not to touch.

## Optional: feedback on the tool

The review's targets are *this project's* harness — `harness-setup` acts on them. But a review
sometimes surfaces a limitation of the **tool itself** (agentic-harness): a check that could not
be expressed, a step that misled, a capability the plugin lacks. That is upstream feedback, not a
project change. After the review context is delivered, offer `harness-feedback` to file it as a
GitHub issue on the agentic-harness repo, with the user's consent. This stays within the
read-only contract — this skill still writes nothing; the handoff, like the one to `harness-setup`,
is what carries any action.

## References

- `references/usage-assessment.md` — the deterministic signal set and how to read each to
  classify a skill or agent as used, unused, bypassed, or drifted.
- `references/skill-testing-guide.md` — trigger validation (should / should-not), with-skill
  vs baseline effectiveness checks, and the iterative-improvement method.
- `references/qa-agent-guide.md` — what a good QA agent does (cross-boundary comparison,
  boundary-bug patterns, incremental QA), for assessing a harness that includes one.
- `${CLAUDE_PLUGIN_ROOT}/shared/harness-model.md`,
  `${CLAUDE_PLUGIN_ROOT}/shared/claude-md-pointer.md`,
  `${CLAUDE_PLUGIN_ROOT}/shared/execution-modes.md` — shared concepts.
