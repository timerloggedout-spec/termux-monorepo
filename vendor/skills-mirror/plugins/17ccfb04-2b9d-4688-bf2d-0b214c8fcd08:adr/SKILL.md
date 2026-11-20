---
description: Create or list Architecture Decision Records (MADR format). ADRs capture the WHY behind a design choice — sequentially numbered under docs/adr/. Use for non-trivial decisions (DB choice, framework upgrade, multi-tenancy model) so future-you understands the constraints. Inspired by Addy Osmani's documentation-and-adrs skill.
argument-hint: "emit --project <dir> --title <text> [--status proposed|accepted|deprecated|superseded] [--context <text>] [--decision <text>] [--consequences <text>] [--alternatives <text>]  |  list --project <dir>"
allowed-tools: Bash, Read
destructive: true
read-only: false
---

Manage Architecture Decision Records:

!`python "${CLAUDE_PLUGIN_ROOT}/skills/one-shot-generator/scripts/adr_writer.py" $ARGUMENTS`

## When to write an ADR

Write one when:

- Choosing between two reasonable options (SQLAlchemy vs SQLModel, Celery vs RQ, REST vs GraphQL)
- Locking in a constraint future-self will want context for (soft-delete strategy, multi-tenancy model, error envelope shape)
- Accepting a trade-off where the obvious choice was rejected

Don't write one for trivial or reversible decisions — they bloat the record.

## Examples

```bash
# Quick — just title + decision
/adr emit --project . \
    --title "Use BullMQ for background jobs over Celery" \
    --decision "Standardise on BullMQ across all Node services"

# Full — context + alternatives + consequences
/adr emit --project . \
    --title "Adopt SQLAlchemy 2.0 mapped_column over legacy Column" \
    --status accepted \
    --context "Need ORM models compatible with FastAPI 0.110+ and Pydantic v2" \
    --decision "Migrate all models to mapped_column() + Mapped[T] syntax" \
    --consequences "Locks us into SQLAlchemy 2.0+. Pre-1.4 codebases must migrate first." \
    --alternatives "- Stay on legacy Column (rejected: deprecated in 2.0)
- Use SQLModel (rejected: still wraps SQLAlchemy, adds a layer)"

# Browse what's there
/adr list --project .
```

## Status lifecycle

```
proposed → accepted → deprecated → superseded
```

Never DELETE an ADR. Supersede it by writing a new one that references the old:
`/adr emit --status superseded` only on the OLD record; reference it from the NEW.
