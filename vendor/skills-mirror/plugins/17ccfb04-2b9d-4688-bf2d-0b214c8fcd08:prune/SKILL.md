---
description: Find files in generated feature directories with zero incoming imports — "zombie code" left behind from past /one-shot iterations when a user renamed an entity or changed direction. Maps the LIVE import graph from main.py / app.py and flags orphaned artifacts. Default mode reports only; --delete actually removes (with an isolated git commit so it's reviewable + reversible).
argument-hint: "scan --project <dir> [--entry main.py] [--json] [--strict]  |  delete --project <dir> --paths <file1> <file2> [--git-commit]"
allowed-tools: Bash
destructive: true
read-only: false
---

Find / clean orphaned files from past /one-shot generations:

!`python "${CLAUDE_PLUGIN_ROOT}/skills/one-shot-generator/scripts/zombie_pruner.py" $ARGUMENTS`

## What it does

Builds the live import graph from your project's entry points (default:
`main.py` / `app.py` / `manage.py` / `src/main.ts` / `cmd/server/main.go`).
Walks the graph; any source file in a `/one-shot`-generated feature
directory that's NOT reachable + NOT a test + NOT kept by convention
(`__init__.py`, migrations, etc.) gets flagged.

## Examples

```bash
# Just look — don't touch anything
/prune scan --project .

# CI gate: fail the build if any zombies exist
/prune scan --project . --strict

# Delete specific files; commit as a separate isolated git commit
/prune delete --project . --paths discount/old_router.py discount/old_schemas.py --git-commit
```

## When to run

- **After renaming an entity mid-development** (`Discount` → `Coupon`):
  the old `discount/` directory may have orphaned files
- **After running `/one-shot` 2-3 times** on the same feature with
  different specs: earlier iterations leave files the later iteration
  doesn't import
- **Before opening a PR**: catches debris your reviewer would otherwise
  flag manually
- **In CI as a gate** (`--strict`): blocks merges that leave zombies behind

## What's NOT flagged (deliberately)

- Test files (matched by name `test_*.py` / `*_test.py` / `*.test.ts` /
  `*.spec.ts` or living under `tests/`)
- Convention files (`__init__.py`, `manage.py`, `conftest.py`, `setup.py`,
  `alembic.ini`, `urls.py`, …)
- Migration files (`alembic/versions/*.py`, `migrations/[0-9]*.py`)
- Files NOT in a feature directory (heuristic: feature dirs contain
  recognizable artifacts like `models.py` + `router.py` together)

These exclusions are conservative on purpose — false-positive deletes
are catastrophic; false-negative misses are merely annoying.
