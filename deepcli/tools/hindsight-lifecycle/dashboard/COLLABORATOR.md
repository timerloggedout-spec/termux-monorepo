# Dashboard Collaborator Lane

## Contract

Dashboard renders independent sections. Each section is a bash script in
`dashboard/sections/*.sh`. Sections run in filename order, receive the exported
runtime environment, and print a human-readable operational view to stdout.

The dashboard is **read-only by contract**: sections observe state; they do not
start, stop, rotate, assign, purge, or mutate the pipeline.

## Built-in lanes

| Lane | Purpose |
|---|---|
| 00-overview | API, PostgreSQL, bank/memory totals, active model |
| 10-run-state | current MVT run + recent batch outcomes |
| 20-banks | bank inventory, age, convention classification |
| 30-extraction | documents vs memory units by bank |
| 40-quota | active model and cached per-model headroom |
| 50-ledgers | provenance ledger + quota snapshot presence |
| 90-integrity | stale-bank, purge staging, stack-state checks |
| 99-template | collaborator starting point |

## Adding a section

1. Create `dashboard/sections/NN-name.sh`.
2. First line: `#!/usr/bin/env bash`.
3. Optional header:
```
# @section NAME
# @owner <github-handle>
# @depends db|api|env
```
4. Body: pure bash. Use `$PSQL` for queries and `$HOME` for user files.
5. Keep sections independently runnable; never rely on another section's output.
6. Use exit 0 for an intentionally unavailable optional source; use non-zero for
   a genuine section failure so `hs-dash` records it.

## Environment

Exported before sections run:

- `PSQL` — PostgreSQL client path
- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`
- `CS` — Codespace name
- `KEY` — Hindsight bearer token
- `DASHBOARD_RUN_ID`
- `DASHBOARD_STARTED_AT`

Never print `PGPASSWORD`, `KEY`, or any credential-derived value.

## Safety rules

- Never kill/restart the pipeline from a section.
- Never write to `/tmp/hs-stack/` from a section.
- Never mutate PostgreSQL from a section.
- Never execute `purge-stale.sql` from a section.
- Prefix lines with `[ SECTION ]` only when needed for disambiguation.
- Missing optional telemetry should be visibly reported, not converted into fake zeros.

## Deployment

`hs-dash` re-ships the dashboard before every run and explicitly stages
`purge-stale.sql` at `/tmp/purge-stale.sql` because the sovereign runner
consumes that path.

The runner executes every section, records PASS/FAIL per section, prints a
dashboard receipt, and exits non-zero when any section genuinely fails.

## Verification

Run:

```bash
bash dashboard/verify.sh
```

The verifier checks shell syntax, required metadata, and mutation/safety
invariants without contacting the database.

## Commit flow

- Branch: `feat/dashboard-lanes`
- Owner: collaborator
- Merge path: PR to `feat/gh-actions/deepseek-integrates-itself`
- Never force-push that branch
