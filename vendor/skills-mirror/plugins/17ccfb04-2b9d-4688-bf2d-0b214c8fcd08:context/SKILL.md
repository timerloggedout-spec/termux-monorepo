---
description: Generate a CLAUDE.md skeleton from a project's detected stack + tooling. Captures the rules-files-first context-engineering ethos as an explicit artifact every Claude session will load. Inspired by addyosmani/agent-skills' context-engineering skill.
argument-hint: "--project <dir> [--out <path>] [--json] [--force | --append]"
allowed-tools: Bash
destructive: true
read-only: false
---

Generate or refresh a project's CLAUDE.md:

!`python "${CLAUDE_PLUGIN_ROOT}/skills/one-shot-generator/scripts/context_writer.py" $ARGUMENTS`

## What it does

Scans the project's manifests (`requirements.txt` / `pyproject.toml` /
`package.json` / `pom.xml` / `go.mod`) and emits a structured CLAUDE.md
with:

- **Stack** — detected language, framework, ORM, test runner, linter,
  formatter, type checker, migration tool
- **Conventions Claude MUST follow** — placeholder for your team rules
- **Conventions Claude must NEVER do** — placeholder for anti-patterns
- **Where things live** — placeholder for repo structure map
- **How to run things** — framework-specific dev / test / migration commands
- **What's risky / requires review** — placeholder for danger zones
- **Quick links** — placeholders for ADRs, OpenAPI, runbook, dashboard

Sections marked `(fill in)` need YOUR input — the script can't know
your team's conventions. The output is a starting point, not a final
document.

## When to run

- **First time onboarding a project** — `/context --project .` produces
  the file; you edit it; you commit it.
- **After a major dep upgrade** — `/context --project . --append` adds
  a fresh detection block alongside the existing file so you can diff.
- **Before sharing with a new teammate** — confirms the rules file
  reflects current reality, not stale assumptions.

## Examples

```bash
# Generate against current dir, write to ./CLAUDE.md
/context --project .

# Custom output path (e.g. for testing)
/context --project . --out /tmp/CLAUDE.draft.md

# Just show what would be detected, don't write
/context --project . --json

# Overwrite an existing CLAUDE.md (use with care)
/context --project . --force

# Add a fresh detection block to an existing CLAUDE.md
/context --project . --append
```

## Output excerpt

```markdown
# my-fastapi-shop — Project Context for Claude

## Stack

- Language: python
- Framework: fastapi `==0.115.6`
- ORM / DB layer: sqlalchemy
- Test runner: pytest
- Linter: ruff
- Formatter: (formatter not detected — fill in)
- Type checker: mypy
- Migrations: alembic
- Docker: yes
- CI: yes
```

## Honest limitation

The script can detect **what** is in the project, not **how** the team
uses it. The `(fill in)` markers are where YOU codify the conventions
that don't show up in manifests:

- Which router pattern do you use? (Functional view vs class-based)
- Where does business logic live? (Service layer vs fat models vs fat views)
- What's your error envelope shape?
- Which lint rules are non-negotiable?

Without those, future Claude sessions invent answers — and the answers
drift over time. CLAUDE.md is the single artifact that anchors them.

## Related

- `/refine` — pre-`/one-shot` workflow for sharpening a feature idea
- `/interview` — extract clarifying questions when the feature is vague
- `/perf-audit` — scan for known performance anti-patterns
- `/ship-check` — production-readiness gate before `--apply`
