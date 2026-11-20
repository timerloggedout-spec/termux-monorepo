---
name: controllerai-workflows
description: Build, inspect, edit, recover, and publish Controller AI workflows and their flows. Use when a user asks to create or change an automation, a flow, or a workflow release, and for the lifecycle rules every other workflow skill relies on.
---
<!-- generated from .claude/skills by cli/scripts/render-skills.mjs; edit the source -->

# Workflows

## Use this when

- Creating a workflow, adding or repairing flows, orienting inside an existing graph, validating, checkpointing, restoring, publishing, or deleting.
- Another skill needs the shared lifecycle rules: which rail an edit lands on, how contracts and IDs behave, what validation and publishing require.

Load the narrow skill when the work reaches it: nodes, connections, props and wiring → `controllerai-node-config`; computed values and conditions → `controllerai-expressions`; Router, If/Else, loops, joins, subflows → `controllerai-flow-control`; runs and debugging → `controllerai-runs`; schedules, webhooks, app events → `controllerai-triggers`; schemas and records → `controllerai-data`; Ask AI and agent nodes → `controllerai-ai-nodes`; user-facing agents → `controllerai-agents`.

## How it works

A **workflow** groups flows, custom schemas, data collections and triggers, and its flows share one data store per environment. A **flow** is one canvas and one callable contract: typed inputs, connected nodes, typed outputs. A Return node maps values into the declared outputs; declaring an output does not fill it. Workflow, flow, node, input and output IDs are distinct identities; never swap one for another.

Every graph edit lands on the **development** version. Publishing creates the **live** release; a live agent that uses the workflow as a tool follows its latest live release without an agent publish, while the owner's Test conversations run the development version. Publishing never copies development records into the live store, and every environment keeps its own data.

Every save is a **state**. History lists states in groups and gives candidate state IDs; a restore rolls the definition back to one state and leaves records and external effects untouched. How far back history is listed and how far back a state can be restored are two separate plan limits, so a listed state is not always restorable.

Deleting a workflow tears down its deployed triggers and soft-deletes it. It is refused while any draft or live agent depends on the workflow, and nothing undeletes. The dependency map shows a workflow's agent and workflow callers and the connections it uses. Deleting a flow removes its graph, its contract and the triggers targeting it, and breaks every caller bound to it.

The account event feed records only supported events: connections created, workflows created, updated, deleted, published and run, agents created and published, members added. Settings changes, member removals and label edits are not in it, and a past change that is not recorded cannot be reconstructed from names or current state.

## Rules

1. **Before changing an existing workflow, read its outline and the affected flow**, then repair those IDs rather than creating a replacement workflow or flow. A repair that recreates loses history, triggers and callers.
2. **Rename contracts in place.** Deleting and recreating an input or output breaks every expression, subflow mapping and agent tool bound to it. After a rename or deletion, re-read the flow and repair the affected dependents before validating or running; a stored input-ID binding survives a rename, so the readback may show nothing to repair.
3. **"Store, save, log, record" without a named destination means a custom data type plus a create-record node.** A flow output alone persists nothing. When the user names a destination (a sheet, a CRM, an app, a file), write there through that integration; add a platform record only if they also want a copy kept here.
4. **Validate after structural edits and before publishing.** Fix every listed prop, wire, expression, type, subflow, branch and trigger error, or report each one with what it breaks. Publish refuses errors; `--acknowledge-validation-errors` is for issues the user has seen and accepted, never a shortcut. If the user forbids a repair, report and stop.
5. **Validation counts are status.** Do not write them into unrelated workflow properties unless the user asks for exactly that.
6. **Deleting a workflow needs the user's explicit intent.** A confirmation flag is not authorization. Check dependencies first; detach draft tools with `cai agent remove-tool <agentId> --tool <toolId>`, and treat a live agent's republish as its own decision.
7. **Layout once per changed flow.** After adds, deletes or rewires, run the flow layout as the last structural step; placement at add time only avoids overlap.
8. **Never weaken the request to make a test pass.** Report an unsupported capability or ask the product question. Keep deliberately armed triggers and advisory-only nodes the user chose.
9. **A conflict means re-read, then reapply the intent to the current graph.** Never replay a stale document or old IDs; the retried write uses the IDs the current state holds.
10. **Say "not recorded" and change nothing** when asked to reconstruct history the feed does not hold.

## Recipes

### Establish context

```bash
cai auth status --json
cai workflow list --json
cai use <workflowId>
cai workflow status --json
```

A create or `cai use` may not win the effective pin: read `selected`, `effectiveWorkflowId` and `pinSource`, and resolve as `pinSource` says (drop the command flag, use `cai use <id>`, or clear an inherited `CAI_WORKFLOW`). `cai config reset` clears stored pins only; `cai doctor` confirms the effective pin and development head.

### Create

```bash
cai workflow create --name "<clear outcome-oriented name>" --json
```

Create with the final name. Read `flowCount` and `nextStep`: with 0 flows, create the first flow with `cai flow create --name "<name>" --json`; with one empty default flow, rename it and build in it; when either field is missing, list the flows before deciding. Add flows only for genuinely separate canvases, and stop at an empty workflow when that is what was asked. A missing projected field is not a failed create: read the full result or the exact inventory before retrying.

### Orient

```bash
cai workflow outline --json
cai workflow state --flow <flowId> --json
cai flow get <flowId> --json
```

The outline shows flows, contracts, graph dependencies, triggers and data inventory in one call. State is a bounded projection; pass the flow ID for node and edge identities. The flow read exposes props and expressions.

### Build

1. Translate the request into inputs, steps, outputs, trigger, integrations, failure behavior and publish intent.
2. Declare flow inputs and outputs before nodes whose props derive from them. Pass a human display label; use the current binding from `flow get` (`jsBinding`) or the outline (`binding`), never the diagnostic `legacyBinding`.
3. Add nodes in execution order and name each after the data it produces; downstream bindings are seeded from that name when wired.
4. Lay out each changed flow, validate, test on development, re-read status. Publish only when the user asked for a live change or authorized deployment.

### Publish

```bash
cai workflow status --json
cai trigger list --json
cai workflow publish --json
```

Read status and every trigger first: publishing activates enabled triggers on the live release. The publish refuses validation errors and may return an approval that the user must grant.

When the publish returns an approval, the CLI polls it; if polling is interrupted, `cai approval resume <approvalId>` continues the same intent instead of publishing again.

### Checkpoint and recover

```bash
cai workflow save --name "<checkpoint>" --json
cai workflow history --json
cai workflow history --group <groupId> --json
cai workflow restore --state <stateId> --json
```

Save before a risky rewrite. Expand a group to find the state ID; restore by state, not by group.

### Delete

```bash
cai deps --json
cai workflow delete <workflowId> --yes
```
`cai deps --account` maps the whole account. The `--force` flag is deprecated and inert.

## Verify

```bash
cai workflow outline --json
cai workflow validate --json
cai workflow status --json
cai flow get <flowId> --json
cai run flow <flowId> --inputs <values.json> --json
```

Evidence that a build works: validation reports zero errors, or each remaining error is reported with its effect; required connections and props are complete; expressions resolve to the expected values, with intentional empties explained; the expected branch and error paths ran where practical; the flow outputs contain the promised values; the development or live state matches the request; the final outline matches the request, with only your own abandoned scratch objects removed. A checkpoint or a rename needs its readback, not a run. Once the requested blockers are fixed and each changed path ran once, stop; warnings alone do not justify a redesign.

## Report

What was built, what ran and what it returned, whether it is published, and any connection or product decision still pending. Share returned product links only; never guess one.

Read [references/command-map.md](references/command-map.md) for the command families by domain when a task spans several areas.
