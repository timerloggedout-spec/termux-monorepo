Run a pre-deploy readiness check before pushing to Railway. Catches issues that
`railway up` cannot — broken Dockerfiles, missing dependencies, and
SQLite-incompatible migrations — before they cause a failed deploy.

## Steps

**1. Determine project root**

Use the current working directory unless the user specifies a path.

**2. Run all three checks in parallel**

Execute each script and capture its JSON output:

```bash
python3 ~/.claude/scripts/railway-preflight/check_dockerfile.py <project_root>
python3 ~/.claude/scripts/railway-preflight/check_deps.py <project_root>
python3 ~/.claude/scripts/railway-preflight/check_migrations.py <project_root>
```

Each script prints a JSON object with:
- `check` — which check ran
- `status` — `pass`, `warn`, `fail`, or `skip`
- `issues` — array of issue objects with `severity`, `type`, `message`, and optionally `file`, `line`, `fix`
- `summary` — one-line count summary

**3. Present results**

Show a summary table first:

```
┌─────────────────────┬────────┐
│ Check               │ Status │
├─────────────────────┼────────┤
│ Dockerfile          │ ✅ pass │
│ Dependencies        │ ❌ fail │
│ Migrations          │ ⚠️ warn │
└─────────────────────┴────────┘
```

Status icons: ✅ pass, ❌ fail, ⚠️ warn, ⏭️ skip

Then for each check with issues, show the issues grouped by severity (errors first):

```
### Dependencies — 1 error

❌ missing_dependency (src/api/app.py)
   'psutil' is imported but not declared in pyproject.toml.
   Add 'psutil' to dependencies.
   Fix: pip install psutil → add "psutil>=5.9.0" to pyproject.toml
```

**4. Verdict**

- Any `fail` → **DO NOT DEPLOY.** Fix all errors first.
- Only `warn` → **Deploy with caution.** Warnings may not break the deploy but indicate fragile patterns.
- All `pass`/`skip` → **Ready to deploy.** Proceed with `railway up`.

**5. Offer to fix errors automatically**

For each error, ask the user if they want you to apply the fix:

- `missing_dependency` → add the package to pyproject.toml
- `source_order` → reorder COPY/RUN instructions in Dockerfile
- `boolean_integer_literal` → replace 0/1 with false/true in the migration INSERT
- `pragma` → remove or replace PRAGMA with PostgreSQL equivalent
- `exec_form_with_var` → convert CMD to shell form

Apply only what the user confirms. After fixing, re-run the affected check to verify.

## Notes

- Scripts require Python 3.11+ (for `sys.stdlib_module_names` and `tomllib`)
- `check_deps.py` scans `src/` if it exists, otherwise scans the project root
- `check_migrations.py` scans any directory named `migrations/` recursively
- `check_dockerfile.py` detects the build backend from `pyproject.toml` to apply
  the correct source-ordering rule (hatchling, flit, poetry, setuptools all need
  source present before `pip install .`)
