---
name: context-refactor
description: "Review and guide refactors across a project's directives, how-tos, and scripts systems, catching cross-cutting problems no single one of those skills can see on its own: a section embedded in the wrong kind of doc, a directive with no backing enforcement script, a doc or script living at the wrong level of the directory tree, or near-duplicate scripts that are candidates for hoisting into one parametric script. Presents findings as a numbered, impact-ordered menu and walks through them one guided change at a time. Use when the user wants a cross-system audit or wants to plan a refactor that spans docs/ how-tos/ and scripts/ folders."
compatibility: "Requires Python 3.9+ and git, and the directives/how-tos/scripts skills installed alongside it in the same skills/ root (it calls their discover_*.py/describe_*.py scripts directly by relative path). Slash-command dispatch (/context-refactor ...) and cross-skill invocation via the Skill tool are Claude Code conventions; other agents can still follow these instructions and run the referenced scripts directly."
allowed-tools: Read Edit Write Glob Grep Bash Skill Agent
metadata:
  claude-code-argument-hint: "[path] [directives,how-tos,scripts]"
  claude-code-context: inline
---

You audit a project's `directives`, `how-tos`, and `scripts` systems together and guide the user
through fixing what you find, one change at a time. This is not a fourth `maintain` mode bolted
onto one of the other three skills — it is a separate, cross-cutting pass that only makes sense
with visibility into all three systems plus the directory hierarchy at once.

## How this differs from the other three skills' `maintain` modes

Each of `directives`, `how-tos`, and `scripts` already audits its own domain: frontmatter
completeness, staleness, broken `--help`, un-deferred automation. Those checks are single-domain
and largely mechanical — they don't require deciding whether something belongs in a *different*
system, or at a *different level* of the tree. This skill reuses those checks (by calling the same
discovery scripts) but adds four categories none of the three own individually. It never
duplicates a check the others already make — where one applies (e.g. `how-tos`' "un-deferred
automation" check), call that skill's `maintain` mode instead of reimplementing it.

Every finding here is a judgment call, not a lint violation. Never batch-apply. Always walk
findings one at a time, with the user picking which change to make and how, before anything is
written.

## Starting every invocation

Run each sibling skill's discovery script (paths are relative to this file, per
[[os-independence]]):

```bash
python3 ../directives/scripts/discover_docs.py
python3 ../how-tos/scripts/discover_docs.py
python3 ../scripts/scripts/discover_scripts.py
```

## Scope

Optional arguments: a path to restrict the audit to (default: repo root) and a comma-separated
list of systems to include (default: all three — `directives,how-tos,scripts`). Filter the
discovery output to paths under the requested scope path before proceeding.

## Phase 1 — Full-content inventory

Unlike `directives`/`how-tos`' `context`/`maintain` modes (frontmatter only) or `scripts`'
(`--help` only), the checks below are section-level and require the actual body text. Read every
matched directive and how-to doc **in full**. For scripts, run `describe_scripts.py` for `--help`
output, and additionally read the source of any script that looks like a plausible duplicate of
another (Category 4 below) — `--help` text alone won't reveal that.

## Phase 2 — Cross-cutting analysis

Build a findings list. Each finding has:

- **category**: `type-misclassification | enforcement-gap | placement | duplication`
- **scope**: `section | whole-file`
- **file**, and for section-scoped findings, the **heading text** and approximate line range
- **severity**: `high | medium | low` — used for impact ordering, not as a gate
- **summary**: one line
- **detail**: what was found and why it matters
- **options**: one or more concrete proposed actions (see below) — never just one forced answer
  for Category 4

### Category 1 — Type misclassification

Applies **at the section level**, not just to a whole doc — a directive can be broadly correct as
a directive and still contain one embedded section that's actually a procedure, or vice versa.

- A directive (`docs/`) containing a numbered, ordered sequence of concrete steps (a procedure) →
  that section belongs in a how-to, with a short reference left behind in the directive
  ("see `how-tos/x.md` for steps").
- A how-to (`how-tos/`) containing a standing rule with no ordered steps (a convention) → that
  section belongs in a directive, with a reference left behind if the how-to still needs to invoke
  it.
- A directive or how-to step that is fully mechanical and not yet pointed at a script — this
  overlaps `how-tos`' own "un-deferred automation" check; when found in a how-to, prefer flagging
  it there (or just running `how-tos maintain`) rather than duplicating the finding here. Only
  raise it here when it's found in a **directive** (which has no `scripts`-deferral convention of
  its own) or spans multiple docs.

Whole-file misclassification (a whole doc filed in the wrong folder) is the same category but
`scope: whole-file` — simpler to detect and to fix.

### Category 2 — Enforcement gaps

A directive states a rule that is mechanically checkable (a naming convention, a required file, a
frontmatter shape) but no script in the project actually checks it. Flag it with a proposed script
sketch as the option — this is a proposal, not an assumption that enforcement is always wanted;
some rules are deliberately left to human review.

### Category 3 — Placement / hierarchy level

A doc or script lives higher or lower in the tree than where it's actually useful:

- Something scoped to one subproject sitting at the repo root (too high — only relevant readers
  have to see it in every unrelated discovery run).
- Something with cross-cutting relevance duplicated or buried inside a single subproject's
  `docs/`/`how-tos/`/`scripts/` (too low — other subprojects that need it won't find it).

The fix is a `git mv` plus fixing any relative-path references to the moved file (other docs'
`[[links]]`, a how-to's script-path reference, this skill's own sibling-script paths if it were
ever the one moved).

### Category 4 — Duplication candidate for generalization

Two or more scripts (or doc procedures) in sibling subprojects do near-identical things with minor
variation. This is explicitly a balance between simplicity/readability and avoiding drift — do not
pick a winner automatically. Always present the three options from the "placement" framing and let
the user choose:

1. **Leave duplicated** — the variation is enough that one parametric version would be harder to
   read than two clear ones.
2. **Add the missing one** — subproject B gets its own copy/adaptation of subproject A's
   script/doc; no consolidation.
3. **Generalize and hoist** — make the logic parametric, move it to the lowest common ancestor
   `scripts/`/`docs/`/`how-tos/` folder, and point both subprojects at it (via `scripts` skill
   discovery, or a directive/how-to reference).

## Phase 3 — Present findings menu

Sort by severity/impact (high first) within each category, then present:

```
Found N findings:

TYPE MISCLASSIFICATION
  1. [high] <summary> (docs/foo.md, section "## Deploying")
  2. [low] <summary> (how-tos/bar.md, whole file)

ENFORCEMENT GAPS
  3. [medium] <summary>

PLACEMENT
  4. [medium] <summary>

DUPLICATION
  5. [high] <summary> (investments/scripts/fetch.py vs ledger/scripts/fetch.py)

Which do you want to work on? Say a number, ask anything directly, or 'done'.
```

Omit empty categories. If there are no findings, say so and stop.

## Phase 4 — Guided single-change loop

For the finding the user picks:

1. **Explain** — what was found, why it matters, quoting the relevant section or `--help`/source
   excerpt.
2. **Propose** — the concrete action(s). For a section extraction, show the exact text block that
   would move and the exact reference line that would stay behind. For Category 4, present all
   three options and ask which one; don't assume "generalize" is always right.
3. **Confirm**, then **apply** — mostly inline, in this turn:
   - **Section extraction**: `Skill(skill: "how-tos", args: 'add <path> "<intent>"')` or
     `Skill(skill: "directives", args: 'add <path> "<intent>"')` seeded with the extracted content,
     then `Edit` the source doc to replace the section with a reference line.
   - **Whole-file reclassification**: `git mv` (never a plain filesystem move — this repo tracks
     history), then the matching `Skill(... update ...)` call to fix frontmatter/format for the
     new home.
   - **Enforcement gap**: `Skill(skill: "scripts", args: 'add <path> "<intent>"')`, then
     `Skill(skill: "directives", args: 'update <path> "<intent>"')` to add the reference to it.
   - **Placement**: `git mv`, then `Grep` for and fix references to the old path.
   - **Duplication → generalize**: parametrize the chosen script in place, `git mv` it to the
     common ancestor's `scripts/` folder, then either `git rm` the sibling copy and update its
     callers, or leave a thin wrapper if callers can't be updated in the same pass — say which you
     did.
   - Reserve `Agent(run_in_background: true)` for the rare case where the mechanical execution
     spans many files (more than a handful of reference fixes) — offer it as an option for that
     finding specifically, don't default to it.
   - Follow the project's git conventions doc for branch/commit naming if one exists (check via
     `describe_docs.py` for a doc with `git` in `covers`); otherwise use the same defaults as the
     `directives` skill's "Large refactors" section.
4. **Re-render remaining findings** with that one removed, same format as Phase 3. If empty, move
   to Phase 5.

## Phase 5 — Summary

One or two sentences: how many findings were found, how many were applied, how many were left for
later, and whether any generalization decisions are worth revisiting once more subprojects exist.
