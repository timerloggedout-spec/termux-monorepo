---
name: controllerai-data
description: Define Controller AI custom data types and read, write, import, promote and debug workflow records in the development and live stores. Use when a workflow needs durable state, a custom.* type, a collection, record reads or writes, a CSV import, workflowData expressions, or data moved between development and live.
---
<!-- generated from .claude/skills by cli/scripts/render-skills.mjs; edit the source -->

# Data

## Use this when

- The user says store, save, log, record, track or remember with no external destination, or asks for a CRM-like backend, a tracker, a queue or a lookup table.
- A flow must create, find, update or delete records, or a schema needs a new field, a relabel or a type change without losing rows.
- A run works in a development test but a trigger or agent sees no data.

Filtering records in expressions belongs to `controllerai-expressions`; configuring the native data nodes belongs to `controllerai-node-config`.

## How it works

**Type versus record.** A `custom.<name>` schema defines fields, and creating it makes a collection available. `custom.customer` is a shape, like an interface; `dataRecord.custom.customer` is a stored record of that shape with its identity (`id`, `createdAt`, `updatedAt`). Only real stored records satisfy a `dataRecord.*` input: a record fetched by a query, by `workflowData(...)` or returned by a native Create or Get. A `custom.*` value has no identity, and the identity paths resolve empty on it. In the app this is the "data record" checkbox on a flow input or a run-on-list item type: unchecked means data shaped like a customer, checked means a real stored customer. Users find that checkbox confusing; explain it in these terms.

**Two stores.** Development and live hold separate rows. Publishing promotes the graph, props, expressions and schemas and creates the live collections; it never copies records and never touches existing live rows. Development runs, development trigger replays and an agent's Test conversations read the development store; published runs, ordinary live trigger dispatch and live agents read live. A flow that "works in the test but not for real" is often reading an empty live collection.

**Native nodes.** The `registry_data` component provides Create, Get, Update, Update multiple and Delete record actions, so a flow owns its own persistence and deletion; the data commands here are for setup, seeding and debugging. Discover the current action keys instead of assuming them. A flow output is a return value, not persistence.

**Update semantics.** The single Update node writes every enabled field that resolves to a value and keeps the other fields at their stored values, so enable only what should change; an enabled field that resolves to null or empty text overwrites the stored value, while one that resolves to nothing is left out. Update multiple takes `list.dataRecord.custom.<type>`, real records from a query or `workflowData(...)`, and runs as one transaction: a record that is missing, deleted since it was fetched, or from another collection fails the whole batch with zero changes to that collection; nodes that ran earlier in the flow keep their effects, so inspect the same-store records and those effects before any rerun the user asked for.

**Field keys.** Direct writes use field IDs; query and get results and CSV columns use display names, plus `id`, `created time` and `updated time`. A query returns one page (`limit` up to 100, `offset`) plus `totalCount`, so a page is never the whole collection unless the count says so. Date fields take ISO-8601 text (`"2026-06-05"` or `"2026-06-05T12:30:00Z"`) in direct writes and CSV; a date-typed expression is accepted as it is; the reserved timestamps read as text and need `.toDate()` in expressions.

**Schema changes never destroy rows.** Deleting a type deactivates its collection on the next saved state, and re-adding the same key reactivates it with every row. Removing a field hides its values; re-adding the same field ID exposes them again. Adding a field is additive and existing rows read it as null. Changing a field's type converts nothing: incompatible values read null and return when the type is restored, and the schema hash changes, which blocks copy-to-live until a publish syncs live. A schema update replaces the complete field list. Deleting a type also removes the fields on other types that referenced it; re-adding the type alone does not bring those fields back, while restoring an earlier workflow state restores every definition, never the records. The record store is not versioned and keeps whatever it holds now, so deleted records and overwritten values are gone for good.

**Search.** The query's text search matches the serialized record and its metadata, not a field predicate; exact filtering happens in expressions.

## Rules

1. **Persisting in workflow data needs a schema and a create-record node.** A flow output or an AI structured result is not stored anywhere by itself; a named external destination is written through its integration.
2. **Inspect existing schemas first and treat field IDs as contracts.** Relabel with `--display`; renaming the `custom.*` key or a field ID strands the stored values under the old key.
3. **Read the whole schema before updating it, then read the echo.** The field list is replaced, not merged; disclose every removed field and confirm the persisted shape matches intent.
4. **Never feed a query result into a direct create or update.** Its keys are display names; rebuild the fields object by write key and omit `id`, `createdAt` and `updatedAt`. The native Update, Update multiple and Delete nodes are the opposite case: they take the stored record itself.
5. **Work on the store the request names; development is the default.** Before any live write, say that published and triggered runs read that store.
6. **Record deletion and overwrites cannot be undone.** They need the user's explicit intent, and a schema mistake is never repaired with a broad delete; a schema mistake is repaired by restoring the key, the field ID or an earlier state.
7. **A CSV commit is partial and additive.** It writes the valid rows, skips the invalid ones and appends on every run: run the dry run first, and commit only when it reports zero invalid rows, unless the user accepts a partial import.
8. **Proof is a same-store read.** A query on the store the flow ran against proves persistence; a node's output alone does not.
9. **Do not infer database guarantees.** Uniqueness, permissions, cascading deletes and concurrent business rules exist only when the flow implements them or the platform verifiably provides them.
10. **Clean up only your own scratch schemas** from abandoned attempts, never a pre-existing user object.
11. **A page is not the collection.** Read `totalCount` and page with the offset before calling a list complete, deduplicating or exporting.

## Recipes

### Define and inspect a type

```bash
cai schema list --json
cai schema get custom.<name> --json
cai schema create custom.customer --display "Customer" --field email:text:"Email" --field score:number:"Score" --json
cai schema update custom.customer --display "Customers" --json
cai data fields --type custom.customer --json
```

`--field id:type[:display]` repeats; `--from-json <file|->` takes a full `{display, fields}` definition; a relabel is `--display` alone. Creating the schema creates the collection, and `cai data collection create` is the same call. Deleting a type needs `--yes` and also removes fields on other types that referenced it.

### Read and write records

```bash
cai data collections --env dev --json
cai data query --type custom.customer --env dev --limit 50 --json
cai data get <recordId> --type custom.customer --env dev --json
cai data create --type custom.customer --fields '{"email":"a@example.com","score":5}' --env dev --json
cai data update <recordId> --type custom.customer --fields '{"score":7}' --env dev --json
cai data delete <recordId> --type custom.customer --env dev --json
```

The update is a patch: omitted fields keep their values. A `get` of a missing record returns null rather than an error, because the two stores hold different rows. Live reads use `--env live` on the same commands; `--limit` and `--offset` page a query.

### Delete many

```bash
cai data delete-many --type custom.customer --records <id1,id2> --env dev --json
cai data delete-many --type custom.customer --all --yes --env dev --json
```

`--all` requires `--yes`, and the two selectors are mutually exclusive.
Soft deletes have no undo. On the live store the published workflow sees the change immediately.

### Import a CSV

```bash
cai data import --type custom.customer --file customers.csv --mode dryRun --env dev --json
cai data import --type custom.customer --file customers.csv --mode commit --env dev --json
```

Columns match display names, the opposite of a direct write. The dry run writes nothing on either store and reports valid and invalid rows; a live commit is visible to the published workflow at once. Read the result counts and query the imported rows on the same store.

### Promote development data to live

```bash
cai workflow publish --json
cai data copy-to-live --type custom.customer --json
cai data collections --env live --json
```

The live collection exists only after a publish, and a changed schema needs a new publish before copying. Copy upserts by record key: live-only rows stay, a live row with the same key is overwritten with the development value, and a deleted live row with that key comes back. Read both collections before an authorized copy, then report `createdCount`, `updatedCount` and the live total.

### Build a data backend

For a CRM, tracker or lookup table that flows and agents will call: define each entity's schema with stable field IDs, a status or archive field and record references for relationships; give each flow one operation with an explicit result for invalid input, a missing record and a duplicate key (an empty record is not success); let Create validate references before writing, Get select by ID, Update fetch then patch only the requested fields, Delete follow the chosen relationship policy, and Search return the matches with the count and page; then test create, get, search, update, get, delete and a missing get, plus a duplicate key, a bad reference, an omitted filter, an empty result, a zero or false value and a page boundary. Uniqueness and concurrency exist only where a flow enforces them.

### Diagnose development versus live

```bash
cai data collections --env dev --json
cai data collections --env live --json
cai data query --type custom.<name> --env live --json
```

A live store with no collections usually means no publish since a store-eligible schema existed; an empty live collection next to a populated development one usually means the data was never promoted or was cleared since. Confirm with the publish status, the live schema and the record history before prescribing a copy. Different row counts between the stores are normal until data is written or copied on each.

## Verify

```bash
cai schema get custom.<name> --json
cai data query --type custom.<name> --env <dev|live> --json
cai workflow validate --json
```

The schema readback shows the intended key, display, complete field list and types; a same-store query shows the expected records with the right field values; expressions that reference the schema still compile; and for a live request, the live collection holds the promised rows.

## Report

Which types and fields exist, which store holds which rows and how many, any field you removed or type you changed, and what remains for the user: an unpublished schema, an empty live collection, or a production write you did not perform.

Read [references/data-rails.md](references/data-rails.md) before a schema rewrite, a deletion, an import or a copy-to-live: what publishing copies, the safe schema-change sequence, and the destructive operations.
