---
name: scripts
description: "Discover, understand, run, and scaffold automation scripts in scripts/ folders. Use when the user wants to find a script for a task, run a script, add a new script, audit existing scripts, or get suggestions for scripts to automate repeated work. Modes: context, run, add, maintain, suggest."
compatibility: Requires Python 3.9+. Slash-command dispatch (/scripts ...) and cross-skill invocation via the Skill tool are Claude Code conventions; other agents can still follow these instructions and run discover_scripts.py/describe_scripts.py directly.
allowed-tools: Read Edit Write Glob Grep Bash Skill
metadata:
  claude-code-argument-hint: <context|run|add|maintain|suggest> [path] ["intent or task description"]
  claude-code-context: fork
---

You manage a project's script library — executable files in `scripts/` and `**/scripts/` folders that automate tasks. Scripts are self-documenting via `--help` — that is the authoritative source of what a script does and how to call it, not a comment header.

This skill's own `discover_scripts.py`/`describe_scripts.py` are plain Python 3 (no bash/WSL
required — this works the same on Linux, macOS, and Windows) and live in this skill's own
`scripts/` directory, next to this `SKILL.md` file.
Run them with `python3 <path>`, resolving `<path>` against that directory (e.g. if this file is
at `/home/alice/.claude/skills/scripts/SKILL.md`, run
`python3 /home/alice/.claude/skills/scripts/scripts/discover_scripts.py`).

## The `--help` requirement

Every script **must** implement `--help` properly. This is not optional and not just a style
preference — the discovery mechanism below executes `--help` on every script it considers, so a
broken `--help` breaks discovery itself. "Properly implemented" means:

- Always available as a flag, regardless of other arguments.
- Exits `0`.
- Has **no side effects** — no writes, no network calls, no state mutation. `--help` must be safe
  to run blindly on every script in the repo.
- Runs fast (well under a second in the normal case) — discovery applies a timeout and treats a
  hang as a failure.
- Prints a real description and usage — enough for both a human and an agent to know what the
  script does and how to call it correctly, not just a bare flag list.

A script whose `--help` errors, hangs, or prints nothing is a bug in that script, flagged by
`maintain` (see below) and treated with the same severity as malformed frontmatter is in the
`directives` skill.

## Optional tags header

Deciding whether a script belongs at its current level of the directory tree, or whether it's a
near-duplicate of a sibling subproject's script worth generalizing and hoisting, is a cross-cutting
judgment call spanning the directory hierarchy — see `context-refactor` rather than trying to fix
it from inside `maintain` here.

A script may optionally carry a single header line for cheap keyword pre-filtering, without having
to execute anything:

```bash
#!/usr/bin/env bash
# tags: [tag1, tag2]
```

This is a hint only — the authoritative description/usage always comes from `--help`, not from a
comment. Don't duplicate the description or usage in a comment; that's a second source of truth
that can drift from what `--help` actually prints.

## Starting every invocation

Run the discovery script first:

```bash
python3 scripts/discover_scripts.py
```

## Modes

### `context "<task description>"`

Find and return the scripts relevant to a task. This mirrors how the `directives` skill resolves
conventions — `discover` lists what exists, `describe` extracts the authoritative metadata cheaply
(there: frontmatter without reading the body; here: `--help` output without reading the source) —
except the metadata source is `--help`, since scripts are executable and frontmatter would be
static, un-enforced text a script could drift away from.

A `scripts/` folder may also carry a `README.md` — e.g. `scripts/android-emulator/README.md`.
That's not a script, so it has no `--help`, but it's often the *only* place gotchas,
prerequisites, or non-obvious conventions live (permission requirements, environment caveats,
recommended configs) — things no individual script's `--help` output would mention on its own.
Treat it as authoritative context for every script in that same folder, not just noise to skip —
but its full content is only read once that folder's scripts are relevant (step 4 below), the
same way a directive doc's body is only read once it matches in the `directives` skill; the
describe step below only ever sees a short summary of it, not the whole file.

1. Run `discover_scripts.py` — list of paths
2. Run `describe_scripts.py` — runs `--help` on every script (with a timeout) and prints its
   output, plus any optional `# tags:` line; for a `README.md` in a scripts folder, prints only a
   short summary (first paragraph, capped) instead of the full file

```bash
python3 scripts/describe_scripts.py
```

3. Match the `--help` output, any `tags` line, any `README.md` summary, and the path against the
   task description — be inclusive, err on the side of returning more
4. Return each matched script with its `--help` output already captured in step 2 — no need to
   run it again. If its folder has a `README.md`, read the **full file** now and surface the
   relevant parts (don't just link to it, and don't rely on the step-2 summary) — that's
   frequently where the actual answer to a "how do I..." question is.
5. If no scripts match, say so clearly — do not fabricate scripts

### `run <script> [args]`

Execute a script.

1. If arguments are unclear or not provided, run `<script> --help` first and show the output
2. If the script has side effects (writes files, calls external APIs, deletes data), state this and ask the user to confirm before proceeding
3. Execute via Bash with the provided or inferred arguments
4. If the script fails, show stderr and suggest fixes based on the `--help` output

### `add <path> "<intent>"`

Scaffold a new script.

1. Run `discover_scripts.py` to see existing scripts in the target folder
2. Infer the language from existing scripts in the same `scripts/` folder; if the folder is empty or mixed, ask the user; default to **Python** when no signal is present
3. Create the file at `<path>` with:
   - Shebang line appropriate for the language
   - Real argument parsing wired up (argparse for Python, getopts or a `usage()` function for bash)
     that satisfies the `--help` requirement above — not a stub. `<intent>` becomes the description
     `--help` prints.
   - Optional `# tags:` header line, inferred from `<intent>`
   - Placeholder `main()` body with a `TODO` comment
4. Set executable bit: `chmod +x <path>`
5. Run `<path> --help` and confirm it exits `0` and prints real output — fix immediately if not,
   don't hand back a script that fails its own `--help` requirement
6. Report the created path and remind the user to fill in the body

### `maintain`

Audit the script library for quality. Run `describe_scripts.py` first, then for each script:

- **`--help` works**: this is the load-bearing check. Flag any script `describe_scripts.py` marked
  as failing, hanging (timed out), or producing no output — this is a bug in the script itself
  (see the `--help` requirement above), not a cosmetic issue
- **Executable bit**: flag if the file is not executable
- **Non-empty body**: flag if the file is a stub with only the scaffold and a TODO

Report a table of findings. Apply trivial fixes inline (add executable bit). A broken `--help`
needs a real fix to the script's argument parsing — flag it for human attention rather than
papering over it.

### `suggest`

Scan the project for automation opportunities and propose new scripts.

1. Run `discover_scripts.py` to see what already exists
2. Scan the project for signals:
   - Long bash one-liners or manual steps described in `docs/` or README files
   - `TODO: automate` or `FIXME` comments in code
   - Repeated commands in CI config, Makefiles, or shell history hints in docs
   - Common dev patterns without a wrapper (data migration, report generation, health checks, data export)
3. For each gap, produce a **proposal** — do not create files yet:
   - Proposed path (e.g. `investments/scripts/rebalance.py`)
   - One-line description
   - Sample tags
   - Two or three bullet points describing what it would do
4. Present all proposals as a numbered list. Ask the user which ones to create.
5. For each approved proposal, run `add <path> "<intent>"` inline — do not ask for confirmation again.

---

## AGENTS.md instruction

The root `AGENTS.md` should contain this block (add it under a `## Scripts` heading if missing).
Use `AGENTS.md`, not `CLAUDE.md`, as the canonical file — if the project's agent is Claude Code
specifically, ensure its `CLAUDE.md` contains a single-line import instead of a duplicated copy:
`@AGENTS.md` (Claude Code resolves that as an include). Other agents that support the emerging
`AGENTS.md` cross-tool convention read it directly, no import needed.

```
## Scripts

Before writing a new script or tool, or doing something manually that could be scripted, run
`/scripts context "<task description>"` to check whether one already exists. Prefer running an
existing script over reimplementing the same logic inline.
```
