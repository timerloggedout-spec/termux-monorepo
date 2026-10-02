# Dashboard Collaborator Lane

## Contract

Dashboard renders sections. Each section is a bash script in
`dashboard/sections/*.sh`. Sections run in filename order, source `/tmp/hs-db-runner.sh`
for PG, and print to stdout.

## Adding a section

1. Create `dashboard/sections/NN-name.sh`
2. First line: `#!/usr/bin/env bash`
3. Optional header block:
```

@section NAME

@owner <github-handle>

@depends db|api|env

```
4. Body: pure bash. Use `$PSQL` for queries (already exported), `$HOME` for user files.
5. Ship: `hs-dash` re-ships the whole `dashboard/` dir before every run.

## Section env contract

Exported before sections run:
- `PSQL`        — path to psql binary on codespace
- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` — set
- `CS`          — codespace name
- `KEY`         — Hindsight bearer token

## Rules

- Never kill / restart the pipeline from a section
- Never write to `/tmp/hs-stack/` from a section (rotator owns it)
- Prefix log lines with `[ SECTION_NAME ]` only if the section needs disambiguation
- Sections must not depend on sections above them for ordering

## Commit flow

- Branch: `feat/dashboard-lanes`
- Owner: collaborator
- Merge path: PR to `feat/gh-actions/deepseek-integrates-itself`
- Never force-push that branch
