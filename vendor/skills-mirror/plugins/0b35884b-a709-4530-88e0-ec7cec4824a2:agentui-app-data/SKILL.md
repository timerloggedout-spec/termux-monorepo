---
name: agentui-app-data
description: Model and inspect an AgentUI app's hosted database — entity schemas that become real tables, reading records from the terminal, and row-level access rules. Use when the user wants their app to store data, asks for tables/fields/schema changes, wants to see what is in the database, asks who can read or edit which rows, or mentions permissions, roles, multi-tenant data, or data security for an AgentUI app.
---

# The app's database

## Entities are files

Every table is one file: `entities/<Name>.json`. `sync` writes them, `push`
migrates the real Postgres table. The file name is the entity name — `Invoice.json`
is `Invoice`. Read the schemas on disk; `agentui data entities` shows the live tables.

Adding a table = writing a new `entities/Invoice.json` and pushing it. Changing
a field = editing the file and pushing. Ask `agentui skills info "Database Operations"`
for the schema vocabulary and how app code queries these entities, and read `AGENTS.md`
in the project — it carries the current entity-authoring rules.

An `entities/<Name>.schema.json` holding `{ name, schema, workflowId }` is a table dump an
older CLI's `sync` wrote — not an entity. `push` and `deploy` ignore it (listed under
`ignoredSchemaDumps` in `push --dry-run --json`), `validate` flags it as info, the next
`sync` deletes it. Don't edit it or push it; edit `entities/<Name>.json`.

Inside app code, entities are imported per entity (e.g. `import { Invoice } from
"@/entities/Invoice"`) and expose the platform's query API (`Invoice.filter(...)`,
`User.me()`, …). Confirm the exact API from `AGENTS.md` / `agentui skills info` rather
than from memory — it is the part that moves.

## Reading records

Read-only by design. Writes go through the app, an automation, or the dashboard, where
the app's own rules run.

```bash
agentui data entities                       # entities and their fields
agentui data list Invoice --where 'status=overdue'
agentui data get Invoice <id>
agentui data count Invoice --where 'status=overdue'
agentui data list Invoice --where 'customer~acme' --sort -createdAt --limit 50
```

`--where` is repeatable and takes four operators: `field=value` (equals),
`field~value` (contains), `field^value` (starts with), `field$value` (ends with).
An unreadable clause is refused rather than dropped, because a confident empty result
is worse than an error. Paginate with `--offset` (the CLI prints the next one) or
`--page`, sort with `--sort -createdAt`, and search free-text with `--search`.

Every one of these reads the environment `agentui env current` reports and prints which
one it read. **Never show the user rows without saying which environment they came
from** — staging and production have completely separate data.

## Row-level security

```bash
agentui data security                       # current per-table rules
agentui guide security                      # the full access vocabulary, generated live
```

Rules are **proposed, never changed** from the CLI. `suggest` prints a link that opens
Data Security with the proposal filled in and an Accept button for the user:

```bash
agentui data security suggest Invoice \
  --read authenticated --update creator --delete admin \
  --reason "Financial records"
```

`agentui open security <Table>` with the same flags prints the same link, and
`agentui open` alone lists the tables that have no rules yet.

A proposal that would match no records — a field or user property that does not exist —
is refused before the link is minted, because accepting one locks every user out of
their own data with no error.

Default to the tightest rule that still lets the app work, and tell the user in one line
what the proposal would mean for each role before handing them the link.
