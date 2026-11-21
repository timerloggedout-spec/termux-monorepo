---
name: how-tos
description: "Manage project how-to docs in how-tos/ folders — step-by-step operational procedures (deploy, generate an access token, compile, rotate credentials, run a database migration, ...). Use when the user wants to add or update a procedure doc, audit the how-to system for quality, or find how to carry out an operational task. Modes: add, update, maintain, context, suggest."
compatibility: Requires Python 3.9+. Slash-command dispatch (/how-tos ...) and cross-skill invocation via the Skill tool are Claude Code conventions; other agents can still follow these instructions and run the bundled scripts/ directly.
allowed-tools: Read Edit Write Glob Grep Bash Skill
metadata:
  claude-code-argument-hint: <add|update|maintain|context|suggest> [path] ["intent or task description"]
  claude-code-context: fork
---

You manage a project's how-to system — structured markdown files in `how-tos/` and `**/how-tos/`
folders that encode operational procedures: how to deploy, how to generate an access token, how to
compile, how to rotate credentials, how to run a database migration, and similar recurring "how do
I actually do this" tasks. A root `AGENTS.md` tells agents to use this skill to find the relevant
procedure before attempting an operational task from scratch.

## How this differs from `directives` and `scripts`

- **`directives`** encodes conventions and standards — rules about how code should be written.
  **`how-tos`** encodes procedures — steps to carry out a specific operational task. A directive
  says "commits use imperative mood"; a how-to says "to cut a release, do steps 1–6."
- **`scripts`** is the executable layer. A how-to is allowed, and often expected, to have manual
  steps a script can't cover (click through a web console, wait for a build, copy a value out of a
  dashboard) interleaved with steps that *are* scripted. When a step is automated, the how-to must
  point at the `scripts` skill rather than inlining the command — see "Deferring to `scripts`" below.

This skill reuses the `directives` skill's discovery mechanism (glob a dedicated folder,
frontmatter-only describe pass) applied to `how-tos/` instead of `docs/`. Unlike `directives`, it
ships **no bundled defaults** — operational procedures are inherently project-specific, so there is
nothing generic to fall back to.

A section embedded in the wrong kind of doc (a directive with steps that belong here, or a how-to
step that states a standing rule) is a cross-cutting concern spanning both skills — see
`context-refactor` rather than trying to fix it from inside `maintain` here.

All scripts this skill uses (`scripts/discover_docs.py`, `scripts/describe_docs.py`) are plain
Python 3 (no bash/WSL required — this works the same on Linux, macOS, and Windows) and live in
this skill's own `scripts/` directory, next to this `SKILL.md` file. Run them with
`python3 <path>`, resolving `<path>` against that directory (e.g. if this file is at
`/home/alice/.claude/skills/how-tos/SKILL.md`, run
`python3 /home/alice/.claude/skills/how-tos/scripts/discover_docs.py`).

## How-to doc frontmatter

Every how-to doc must have YAML frontmatter with exactly these fields:

```yaml
---
description: one-line summary of what procedure this doc covers
scope: root                        # or a subsystem path, e.g. client, showcase-video
covers: [tag1, tag2, tag3]         # keywords for relevance matching
---
```

## Deferring to `scripts`

Before writing a manual command block into a how-to step, check whether a script already covers
it — use the scripts skill's discovery mechanism (its `context` mode, given the step's intent) to
find out. If one exists, the step must say to run it (name the script path, or point at the
scripts skill's `run` mode) instead of inlining the command — the script's `--help` is the
authoritative source for arguments, and duplicating them in the how-to creates a second source of
truth that will drift. If no script exists but the step is a good automation candidate, note that
in the how-to body (or flag it to the scripts skill's `suggest` mode) rather than silently leaving
it manual forever.

Steps that are genuinely manual (a web console click-path, waiting on an external party, a
one-time human judgment call) stay written out in full — don't force a script where none belongs.

## Starting every invocation

Run the discovery script first to understand the project's how-to landscape:

```bash
python3 scripts/discover_docs.py
```

## Modes

### `add <path> "<intent>"`

1. Run `discover_docs.py`
2. Read existing how-tos in the same folder for tone/format reference
3. For each step, check whether the scripts skill's discovery mechanism already covers it — defer
   to an existing script per the section above instead of inlining commands
4. Create the new how-to doc at `<path>` with correct frontmatter and numbered, imperative steps
   - Content is procedural: concrete, ordered, verifiable steps — not background or rationale
   - Concise — Claude reads this on every relevant operational task
5. Ensure root `AGENTS.md` contains the how-tos instruction (see below); add it if missing

### `update <path> "<intent>"`

1. Run `discover_docs.py`
2. Read the current doc
3. Update steps and amend frontmatter as needed (preserve existing fields, update if stale)
4. Re-check any newly-manual steps against the scripts skill's discovery mechanism per the
   deferring section above

### `maintain`

A quality audit of the entire how-to system. Run:

```bash
python3 scripts/describe_docs.py
```

Audit each doc by reading it fully:

- **Frontmatter completeness**: all three fields present and non-empty
- **Description quality**: specific and accurate? Does it reflect the actual procedure? Rewrite if vague or stale.
- **Covers tags**: accurate and complete? Read the body — are there important topics not represented by any tag? Add missing ones. Remove tags that don't match the content.
- **Scope accuracy**: does the declared scope match where the file lives?
- **Staleness**: do steps reference commands, URLs, or UI paths that no longer match the current project state? Do NOT silently rewrite from a guess — flag for human review if uncertain.
- **Un-deferred automation**: does any step inline a command that a script in `scripts/` already covers? Flag it and, if straightforward, fix it inline by pointing at the script instead.

Report a summary: what was changed, what was flagged for human review.

### `context "<task description>"`

Find and return the how-tos relevant to an operational task.

1. Run `describe_docs.py` — frontmatter only, no body
2. Match `covers` tags and `description` text against the task description — be inclusive, not exclusive; err on the side of returning more
3. Read and return the **full content** of matched docs
4. If no docs match, say so clearly — do not fabricate a procedure

This mode is intended to be called at the start of any operational task (deploy, generate a token,
compile, rotate credentials, run a database migration, ...) to replace ad hoc rediscovery.

### `suggest`

Explore the repository and propose new how-to docs that would be useful to add.

1. Run `discover_docs.py` to see what how-tos already exist
2. Explore the repository for undocumented procedures:
   - Read `AGENTS.md`, README files, and CI/deploy configs for multi-step operational tasks
   - Look for scripts in `scripts/` that are clearly one step of a larger manual procedure (e.g. a
     `generate-token.sh` next to no doc explaining when/why to run it)
   - Look for task or note history (tasks/, docs/, project notes) describing "how I did X" that
     never got turned into a repeatable procedure
3. For each gap found, produce a **proposal** — do not create files yet:
   - Proposed path (e.g. `how-tos/deploy-staging.md`)
   - One-line description of what procedure it would cover
   - Sample `covers` tags
   - Two or three bullet points of what the steps would be, noting which steps would defer to an existing script
4. Present all proposals as a numbered list. Ask the user which ones to create (they can say "all", list numbers, or pick interactively).
5. For each approved proposal, run `add <path> "<intent>"` inline — do not ask for confirmation again.

Focus on gaps where an operational task would otherwise be re-figured-out from scratch or from
memory — not on documenting things that are obvious from a single script's `--help`.

---

## AGENTS.md instruction

The root `AGENTS.md` should contain this block (add it under a `## How-Tos` heading if missing).
Use `AGENTS.md`, not `CLAUDE.md`, as the canonical file — if the project's agent is Claude Code
specifically, ensure its `CLAUDE.md` contains a single-line import instead of a duplicated copy:
`@AGENTS.md` (Claude Code resolves that as an include). Other agents that support the emerging
`AGENTS.md` cross-tool convention read it directly, no import needed.

```
## How-Tos

Before starting an operational task (deploy, generate an access token, compile, rotate
credentials, run a database migration, ...), run `/how-tos context "<task description>"` to load
the relevant procedure. Do not proceed without doing this first.
```
