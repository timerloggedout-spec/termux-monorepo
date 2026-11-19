---
name: controllerai-expressions
description: Author, validate, persist, and debug Controller AI expressions for node props and conditions. Use when a value comes from a flow input, an upstream node, a loop item, workflow data, a constant, a calculation, a template or a boolean rule, and when an expression compiles but resolves to null or the wrong input.
---
<!-- generated from .claude/skills by cli/scripts/render-skills.mjs; edit the source -->

# Expressions

## Use this when

- A node prop or condition needs a dynamic value: a flow input, a wired upstream output, the current loop item, workflow records, a date calculation, a text template, a boolean guard.
- An expression compiles but the run shows null, an empty value, or the wrong source.

Node discovery, connections and static props belong to `controllerai-node-config`; Router, If/Else and loop structure to `controllerai-flow-control`; execution evidence to `controllerai-runs`.

## How it works

Expressions are written in a restricted JavaScript-like language and compiled into the engine's expression tree. It is not JavaScript: no loops, assignments, `new`, regular expressions, optional chaining, object literals (the `{ ignoreEmptyConstraints: true }` filter options object is the one accepted object) or library methods beyond what the compiler catalog advertises. A program is optional `const` declarations followed by one final expression.

**Everything is typed.** An expression can only be written against a known type. An integration node's output type is usually learned from a representative development run, or from a supported output selector or a declared provider sample, and `node status` says which route applies; `custom.*` types describe data-store records and AI structured outputs; `dataRecord.custom.x` is a stored record of that shape with its identity (`id`, `createdAt`, `updatedAt`), while bare `custom.x` is the shape alone; `list.` prefixes a list of any type. When an expression cannot be authored, the cause is usually a missing upstream type.

**Scope** comes from the destination's expression context: `flow.<name>` is a flow input, `inputs.<name>` a wired node input (usually already unwrapped), `item` the current loop item where the context exposes it, `workflowData("custom.type")` the records of an active collection on the current rail, and `now` and `isLiveVersion` constants. Bindings are display-derived and de-duplicated by the context; display labels and old spellings are not bindings.

**Empty values.** An omitted input arrives in its typed empty form: `""` for text, null for objects, and it is compared like any other value: `=== ""` matches only rows whose field is empty, `!==` passes every other row including rows with a missing value, `includes("")` matches every text row, and a negative membership check against a missing list passes everything. An omitted optional input therefore does not close a filter by itself: equality usually returns nothing, a negation or containment returns everything, and an omitted lookup key can turn a create-if-missing step into a duplicate. With `ignoreEmptyConstraints` on, a constraint whose value is null, empty text or an empty list is skipped; `0`, `false`, whitespace and dates stay real constraints. `.every()` takes the same predicates as `.filter()` and compiles to a single-pass "all match"; a constraint on a field the item does not have compiles, makes `.every()` false and is dropped by `.filter()`, which then matches every item. Predicates compare a field of the item, so a list of numbers or text cannot be filtered by its values: count or classify primitives with a per-item loop that returns a flag, then sum the flags. Comparators decide what missing, null or unparseable values do, and negative comparisons can pass rows with missing values, so a guard states presence explicitly.

**Dates** travel as ISO-8601 text. A `date`-typed input or field takes date operations directly; text needs `.toDate()` first, and epoch text needs an explicit unit, `.toDate("epoch_seconds")` or `.toDate("epoch_millis")`. Format with Moment tokens such as `format("YYYY-MM-DD")`.

**Templates and ternaries.** A backtick template with `${...}` returns text; keep non-text values as direct typed expressions. A ternary keeps its type when both branches are numbers or both are booleans; any other pair renders as text, so give both branches the same type when a number or boolean is needed, and never quote or coerce a branch to hide a type mismatch.

**Channels.** A literal value and an expression are stored on different channels; the setters pick the channel from the prop's metadata. On a value-channel text array, a scalar expression replaces the whole array with one dynamic element and a list expression is rejected; a static list is written as a literal array, and a list expression only where the prop exposes whole-array expression mode.

## Rules

1. **Wire first, then read the context, then write.** An upstream output listed under `unwiredUpstreamOutputs` is discovery, not scope. Re-read the context after rewiring, renaming an input, changing a schema, changing a dynamic selector, or resolving an output type.
2. **Copy bindings exactly.** Never derive one from a label, never add `.data` on your own, and when a diagnostic advertises a typeable accessor, use it. For duplicate names, use the de-duplicated binding, input ID and source node the context gives.
3. **Use only advertised operations.** Read the catalog for the type; never author a raw expression tree or probe a private API. When an idiom is rejected, use the advertised alternative, or express the logic through routing, typed inputs or a native action.
4. **A literal is a literal.** `flow.name`, `{{name}}` and `${name}` inside a literal stay text. Dynamic values go through the expression setter.
5. **Preserve `0` and `false`.** Fallbacks are same-type literals (`flow.count ?? 0`, `flow.enabled ?? false`) and never swallow a real zero or false.
6. **Optional filters are a decision, not a default.** An omitted value is a real comparison, not a skipped constraint; turn on `ignoreEmptyConstraints` only when omitting that constraint is what the user wants, and test both the supplied and the omitted case.
7. **Compiler success proves syntax and types, not the source.** When names are ambiguous, check the source node and input IDs, then look at runtime values.
8. **An expression that reads `inputs.<name>` is verified only by running the containing flow.** A node run never executes upstream nodes.
9. **Empty results need a reason.** An intentional empty (a closed filter, an absent optional) is valid; an unexpected null or partial value in `resolvedConfigs` is a failure to trace, not something to fix by rewriting valid syntax.

## Recipes

### Discover the scope and the operations

```bash
cai expr context <nodeId> --prop <propName> --json
cai expr ops --workflow <workflowId> --type <text|number|date|list|boolean|file|custom> --json
```

The catalog is read from the workflow's expression context, so the workflow needs at least one node, and an existing pin (`cai use` or `CAI_WORKFLOW`) can replace `--workflow`.

If the source is not wired yet:

```bash
cai node connect --flow <flowId> --from <sourceNodeId> --to <targetNodeId> --json
```

Router and If/Else outputs connect through `cai branch connect`.

### Validate, write, read back

```bash
cai expr validate <nodeId> --prop <propName> --js '<expression>' --json
cai expr set <nodeId> --prop <propName> --js '<expression>' --json
cai expr decompile <nodeId> --prop <propName> --json
```

The setter fetches the prop's metadata, enables a catalog-only optional prop when needed, compiles, writes the right channel and verifies the readback. If the write fails after enabling, the prop stays enabled: disable it with `cai node disable-prop <nodeId> --prop <propName>` and re-read. Decompile returns the stored source and channel, not a type: validate the decompiled source against the current destination to confirm the type still holds.

For a multiline or shell-sensitive expression, keep the exact UTF-8 source in a file and pass `--js-file <path>` (or `--js-file -` for stdin) instead of `--js`; `expr validate`, `expr set`, `node set`, `node only-when`, `branch add` and `branch update` all accept it.

### Conditions

```bash
cai expr validate <nodeId> --mode onlyWhen --js '<boolean expression>' --json
cai node only-when <nodeId> --js '<boolean expression>' --json
cai node only-when <nodeId> --groups-json '[["flow.email.isNotEmpty()","flow.units < 5"],["flow.override === true"]]' --json
cai branch update <nodeId> --route <routeId> --condition-json '[["flow.email.isNotEmpty()","flow.units < 5"],["flow.override === true"]]' --json
```

A node guard takes one boolean expression, or groups where each inner list is AND and the outer list is OR; a root `&&` or `||` inside one expression is not supported, so compound guards use groups. Branch conditions use the same grouped shape, each string compiled separately. Make a missing number fail a comparison with a same-type boundary: `(flow.unitsLeft ?? 5) < 5`.

### Prove the value at runtime

```bash
cai run node <nodeId> --inputs <values.json> --json
cai run flow <flowId> --inputs <values.json> --json
cai exec node <nodeExecutionId> --full --json
```

The node run isolates the destination's own configuration. The flow run proves an upstream-derived value. Inspect `runScope` and `resolvedConfigs`; when a search unexpectedly returns nothing, look at the resolved comparison values first.

## Verify

The current context shows the intended source IDs and bindings; the decompiled source validates against the current destination; the run's `resolvedConfigs` hold the intended value, with intentional empties explained; the edge cases the task implies were exercised: omitted input, `0`, `false`, empty text or list, missing record.

## Report

Which values are dynamic and what they read from, any optional-filter or fallback decision you made, and what the run showed.

Read [references/dsl-and-recipes.md](references/dsl-and-recipes.md) for the canonical patterns: templates, prefix tests, HTTP JSON bodies, fallbacks, dates, workflow records, optional filters, loop items and outputs, and the troubleshooting order.
