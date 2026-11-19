---
name: directives
description: "Manage project directive docs in docs/ folders. Use when the user wants to add or update conventions/standards documents, audit the directive system for quality, or find which directives are relevant to a task. Modes: add, update, maintain, context, suggest."
compatibility: Requires Python 3.9+ and git. Slash-command dispatch (/directives ...) and cross-skill invocation via the Skill tool are Claude Code conventions; other agents can still follow these instructions and run the bundled scripts/ directly.
allowed-tools: Read Edit Write Glob Grep Bash Skill
metadata:
  claude-code-argument-hint: <add|update|maintain|context|suggest> [path] ["intent or task description"]
  claude-code-context: fork
---

You manage a project's directive system — structured markdown files in `docs/` and `**/docs/` folders that encode conventions, standards, and domain knowledge. A single root `AGENTS.md` tells agents to use this skill to find relevant directives before doing any work.

All scripts this skill uses (`scripts/discover_docs.py`, `scripts/describe_docs.py`) are plain
Python 3 (no bash/WSL required — this works the same on Linux, macOS, and Windows) and live in
this skill's own `scripts/` directory, next to this `SKILL.md` file. Run them with
`python3 <path>`, resolving `<path>` against that directory (e.g. if this file is at
`/home/alice/.claude/skills/directives/SKILL.md`, run
`python3 /home/alice/.claude/skills/directives/scripts/discover_docs.py`).

## Skill-bundled default docs

This skill ships with its own `docs/` folder (next to this file) containing a default set of
directive docs — general engineering conventions (hierarchical verification, out-of-tree
artifacts, tools-over-judgment) that apply to any project, not just one that happens to vendor
its own copies.

`discover_docs.py`/`describe_docs.py` always include these bundled docs *in addition to* whatever
a project has in its own `docs/` folders — there is nothing to set up per project to benefit from
them. A project that wants to opt out entirely (it disagrees with the defaults wholesale, or
wants a clean slate) creates a `.no-bundled-directives` marker file (any content — presence is
what matters) at its root; `discover_docs.py`/`describe_docs.py` then skip the bundled-docs
section for that project, regardless of whether this skill is installed via symlink or copy (see
`docs/install-conventions.md` in the agent-context-kit repo for why both an install-time flag and
this per-project marker exist). Short of that, treat them as read-only defaults: **`add`/`update`
only ever create or modify files in the calling project's own `docs/` folder, never in this
skill's bundled `docs/`.** If a bundled default needs to change, edit it here (in the skill), not
by forking a copy into a project.

**Precedence**: when a project's own doc and a bundled default cover the same topic (e.g. both
describe the git integration/merge strategy), the project doc wins — it is the more specific,
deliberately-authored source. Don't silently follow the bundled default if a project doc contradicts
it; flag the contradiction (see `maintain` below) so one of them gets fixed or the project doc
explicitly notes it supersedes the default.

A directive with an embedded section of ordered steps (that section belongs in a how-to instead),
a directive with no backing enforcement script, or a directive at the wrong level of the directory
tree are cross-cutting judgment calls spanning `how-tos`/`scripts`/the directory hierarchy — see
`context-refactor` rather than trying to fix them from inside `maintain` here.

## Directive doc frontmatter

Every directive doc must have YAML frontmatter with exactly these fields:

```yaml
---
description: one-line summary of what this doc covers
scope: root                        # or a subsystem path, e.g. ledger, obsidian-brain
covers: [tag1, tag2, tag3]         # keywords for relevance matching
---
```

## Starting every invocation

Run the discovery script first to understand the project's docs landscape:

```bash
python3 scripts/discover_docs.py
```

## Modes

### `add <path> "<intent>"`

1. Run `discover_docs.py`
2. Read existing docs in the same folder for tone/format reference
3. Create the new directive doc at `<path>` with correct frontmatter and well-structured content
   - Content should be directive in tone: rules, not descriptions
   - Concise — Claude reads this on every relevant task
4. Ensure root `AGENTS.md` contains the directives instruction (see below); add it if missing
5. Assess impact and apply codebase changes (see Impact Assessment)

### `update <path> "<intent>"`

1. Run `discover_docs.py`
2. Read the current doc
3. Update content and amend frontmatter as needed (preserve existing fields, update if stale)
4. Assess impact and apply codebase changes

### `maintain`

A quality audit of the entire directive system. Run:

```bash
python3 scripts/describe_docs.py
```

Audit each doc by reading it fully:

- **Frontmatter completeness**: all three fields present and non-empty
- **Description quality**: specific and accurate? Does it reflect what the doc actually says? Rewrite if vague or stale.
- **Covers tags**: accurate and complete? Read the body — are there important topics not represented by any tag? Add missing ones. Remove tags that don't match the content.
- **Scope accuracy**: does the declared scope match where the file lives?
- **Body relevance**: are there sections that contradict current project state, or are clearly outdated? Do NOT silently delete content — flag for human review with a comment or report.
- **Bundled-default conflicts**: for each skill-bundled doc, check whether any project doc covers the same topic (matching `covers` tags is a good starting signal) and whether their guidance actually agrees. Flag any contradiction for human review — do not silently pick a winner.

For root `AGENTS.md`:
- Check the directives instruction is present; add it if missing

Report a summary: what was changed, what was flagged for human review.

### `context "<task description>"`

Find and return the directives relevant to a task.

1. Run `describe_docs.py` — frontmatter only, no body
2. Match `covers` tags and `description` text against the task description — be inclusive, not exclusive; err on the side of returning more
3. Read and return the **full content** of matched docs
4. If no docs match, say so clearly — do not fabricate conventions

This mode is intended to be called at the start of any task to replace manual discovery.

### `suggest`

Explore the repository and propose new directive docs that would be useful to add.

1. Run `discover_docs.py` to see what docs already exist
2. Explore the repository structure:
   - Read `AGENTS.md` and any existing docs to understand what is already covered
   - Scan top-level directories and their contents (`ls`, `Glob`, `Read` key files like `Makefile`, `pyproject.toml`, `package.json`, CI configs, etc.)
   - Look for undocumented conventions: naming patterns, testing approaches, tooling, deployment steps, data formats, language-specific idioms
3. For each gap found, produce a **proposal** — do not create files yet:
   - Proposed path (e.g. `investments/docs/scraper.md`)
   - One-line description of what it would cover
   - Sample `covers` tags
   - Two or three bullet points of what the directive body would say
4. Present all proposals as a numbered list. Ask the user which ones to create (they can say "all", list numbers, or pick interactively).
5. For each approved proposal, run `add <path> "<intent>"` inline — do not ask for confirmation again.

Focus on gaps where Claude would make wrong decisions without guidance — not on documenting things that are obvious from the code.

---

## AGENTS.md instruction

The root `AGENTS.md` should contain this block (add it under a `## Directives` heading if
missing). Use `AGENTS.md`, not `CLAUDE.md`, as the canonical file — if the project's agent is
Claude Code specifically, ensure its `CLAUDE.md` contains a single-line import instead of a
duplicated copy: `@AGENTS.md` (Claude Code resolves that as an include). Other agents that
support the emerging `AGENTS.md` cross-tool convention read it directly, no import needed.

```
## Directives

Before starting any task, run `/directives context "<task description>"` to load the relevant
conventions for that task. Do not proceed without doing this first.
```

---

## Impact assessment (add / update modes)

Before touching the codebase, estimate scope:

- **Small**: directive only affects naming conventions, comments, formatting, or a clearly bounded set of files (e.g. one module, one subsystem) → apply changes inline; stage for review
- **Large**: directive implies structural changes, touches many files, or introduces new patterns across the whole codebase → branch + chunk

### Git conventions

1. Run `describe_docs.py` and check for docs with `git` in their `covers` tags
2. If found → read that doc and follow its conventions exactly for branch naming and commits
3. If not found → use these defaults:
   - Branch naming: `add/<description>` for new conventions, `fix/<description>` for corrections
   - Integrate via rebase onto main branch + fast-forward merge; no merge commits
   - Commit messages: imperative mood, subject line under 72 characters, no AI/agent/Claude mentions

### Large refactors

For large changes, apply them incrementally (one coherent chunk per session turn, committing each
as it lands) rather than in one pass. This skill only manages directive docs — tracking the work
itself (task files, resuming interrupted refactors, etc.) is outside its scope; use whatever
task-tracking convention the project has, if any.
