---
name: controllerai-flow-control
description: Design and configure Controller AI execution paths with only-when guards, If/Else branches, Router routes, for-each loops, subflows, Join Paths and error handling. Use when work must skip, branch, fan out, iterate over a list, call another flow, converge, return a value, or continue after a failure without changing the user's intended semantics.
---
<!-- generated from .claude/skills by cli/scripts/render-skills.mjs; edit the source -->

# Flow control

## Use this when

- A flow must skip an action, choose one path, run every matching path, repeat work per item, call another flow, converge exclusive paths, return a value, or continue after a failure.
- A run shows an unexpected skip, a branch that never fires, an empty return, or a loop that stops early.

Conditions are written with the expression discipline in `controllerai-expressions`; components are found and configured with `controllerai-node-config`; runs are read with `controllerai-runs`.

## How it works

| Intent | Primitive | Runtime semantics |
| --- | --- | --- |
| Skip one action when a condition is false | node `only-when` | No alternate path; the node records `only_when_false`, downstream stays eligible |
| Choose exactly one path | If/Else | The first matching branch runs; Else is the mandatory last fallback |
| Run every matching path | Router | Conditions are independent; every matching route runs, possibly several |
| Do work for every list item | `flow for-each` loop | A typed body flow runs once per item, sequentially, under an item cap |
| Reuse a typed unit of work once | Run flow (subflow) | Explicit input and output mapping to another flow's contract |
| Continue after a failed action | continue-on-error / Error output | The error is captured, downstream sees null for that node, the run ends `completed_with_error` |
| One action after whichever exclusive path ran | Join Paths (`registry_flow-merge`) | `chooseActivePath` passes the single active input's value on; `passThrough` returns one field per connected input (blocked ones null) and suits fan-out that can overlap |
| Give a flow its return value | Return response (`registry_flow-return-response`) | Maps producer values into the declared outputs; without it an otherwise successful flow returns empty outputs |

Skip reasons are the evidence: a false guard records `only_when_false`; a node on an untaken branch or an unmatched route records `upstream_skipped`. Choose the primitive by the semantics the caller and the tests need, never because a component was easier to find.

A fresh If/Else ships with one blank `If` branch and an Else; the blank condition is a validation blocker until it is set. Router routes cannot be reordered because every match runs. Loops run sequentially with a cap that defaults to 500 items (1 to 10000); a list over the cap fails before any iteration, never truncates. `continueOnIterationError` on a loop node continues past a failed child iteration and cannot help when the list or mapping expression fails before any child starts; node-level continue-on-error on the loop node lets the parent flow continue past that failed loop with a null output, but repairs nothing and resumes no iteration. With `chooseActivePath`, zero active inputs stop the flow at the join unless `continueIfNoActivePath` is enabled, which passes null on. Setting a subflow's target synthesizes mapping props from the target's current inputs; when those inputs change, set the target again and remap. Deleting a flow removes its graph, contract, triggers and caller links; turning continue-on-error off deletes the node's Error output and its edges.

## Rules

1. **Guard the action that must skip with `only-when`; do not replace a node skip with If/Else.** A false guard does not stop downstream execution (the skipped node just yields no value), so guard downstream separately or branch when it must skip too.
2. **Never invent a missing condition** from names, sample values or one observed run. Leave the branch blank, report the blocker and ask; a missing business rule is not yours to guess.
3. **Update the blank default If branch before adding another branch.** Adding beside it leaves a blocker and a duplicate.
4. **Order is behavior only for If/Else.** Put the most specific condition first, never write a complement condition for Else, and never simulate Router order by deleting routes or chaining descendants; leave a fan-out unchanged unless the user authorizes a redesign.
5. **Build per-item work with `flow for-each`**, never by hand-assembling the injection and mapping pattern. Put the real work in the generated body flow and declare its outputs before consuming aggregate results. Continue past failed iterations only when partial completion is acceptable and the downstream logic handles failed iteration records.
6. **Compound guards are supported**: a node guard takes one boolean expression or grouped conditions (inner list AND, outer list OR); a root `&&` or `||` inside one expression is not. Never weaken a rule to fit the grammar, and never probe a private API.
7. **Fail missing comparisons closed** with a same-type boundary (`(flow.unitsLeft ?? 5) < 5`), and keep money paths blocking: charges, purchases, transfers and refunds never continue on error, and never enable continue-on-error just to make a run green.
8. **Converge exclusive paths through Join Paths**; never wire several branches straight into an ordinary node and never duplicate the shared action.
9. **A flow that returns data needs a Return response node** bound to declared outputs. Every Return writes every declared output, unbound ones as null, and a later Return (in execution order) overwrites an earlier one, so a partial Return can erase a value; design one Return per path unless merging is intended.
10. **Read the branch list after every edit.** Warnings about missing conditions or unwired paths are blockers even when a run looks green.

## Recipes

### Guard one action

```bash
cai expr context <nodeId> --json
cai expr validate <nodeId> --mode onlyWhen --js '<boolean expression>' --json
cai node only-when <nodeId> --js '<boolean expression>' --json
cai node only-when <nodeId> --groups-json '[["flow.email.isNotEmpty()","flow.units < 5"],["flow.override === true"]]' --json
```

Use `--clear` only when removing the guard is the user's intent.

### If/Else and Router

```bash
cai branch list <controlNodeId> --json
cai branch update <controlNodeId> --route <defaultIfBranchId> --name "<meaning>" --js '<boolean expression>' --json
cai branch add <controlNodeId> --name "<meaning>" --js '<boolean expression>' --json
cai branch update <controlNodeId> --route <routeId> --condition-json '[["flow.email.isNotEmpty()","flow.units < 5"],["flow.override === true"]]' --json
cai branch connect <controlNodeId> --route <routeId> --to <targetNodeId> --flow <flowId> --json
cai branch reorder <ifElseNodeId> --order <conditionId1,conditionId2> --json
```

Find the control component with `controllerai-node-config`, then read the branch IDs. Grouped conditions are OR of AND rows, each string compiled separately. Add an If branch only for another non-Else case; add a Router route for each intended independent match. Reorder lists every condition branch exactly once and omits Else, which stays last. Wire every returned route ID explicitly.

### Loop over a list

```bash
cai node get <listProducingNodeId> --json
cai flow for-each --flow <parentFlowId> --from <listProducingNodeId> --source-output <exactOutputId> --name "<item flow name>" --item-type <text|number|date|boolean|custom.type> --max-items <n> --json
cai node set <loopNodeId> --prop maxItems --value <n> --json
cai node set <loopNodeId> --prop continueOnIterationError --value true --json
```

`--source-output` is the exact `outputs[].id` of the selected node, never a display name, and there is no first-output default (branch and error outputs included). When the whole output is the list, omit the list selectors; for a nested list use `--list-field` with the dot path below `.data`; reserve `--list-js` for an exact advanced expression whose shape you took from the context; the selection forms are mutually exclusive. `--item-field <id:type[:display]>` (repeatable) is only for creating a new `custom.*` item type; stored records use `dataRecord.custom.*`. Set the cap on purpose when the requirement differs from 500, decide `--continue-on-error` explicitly, then read the returned warnings and follow `nextSteps` in order; a list/item type mismatch means created but unverified. In mappings, `item` exists only where the context exposes it; inside the body flow the item is `flow.<itemInput>`; aggregate results are iteration records with child outputs under `outputs`.

For multiline or shell-sensitive list source, pass `--js-file <path|->` instead of `--list-js`.

### Call another flow

```bash
cai node set-flow <runFlowNodeId> --flow <calledFlowId> --json
cai node props <runFlowNodeId> --json
```

Define the called flow's inputs and outputs first, add the Run flow component, set the target, then bind the generated mapping props with expressions.

### Converge, return, handle errors

```bash
cai node add --flow <flowId> --node registry_flow --key registry_flow-merge --name "Join paths" --json
cai node set <joinNodeId> --prop mode --value chooseActivePath --json
cai flow output add <bodyFlowId> --display "<output label>" --name <output_key> --type <type> --json
cai node add --flow <bodyFlowId> --node registry_flow --key registry_flow-return-response --name "Return <value>" --after <producerNodeId> --json
cai node continue-on-error <nodeId> --enable --json
cai node connect --flow <flowId> --from <nodeId> --to <handlerNodeId> --output error --json
```

Join Paths: connect every type-compatible branch tail to it (all connected input types are checked, inactive paths included, which is why `pathDataType` is asked for once `chooseActivePath` reveals it), set `pathDataType` from the returned options, and place the shared action after it (`--after <joinNodeId>`, or connect the existing action). Return: declare the output first so its generated prop exists, add the exact component after the producer, then bind the prop through the expression setter. Error output wiring is optional; add it only when a failure needs explicit handling.

## Verify

```bash
cai branch list <controlNodeId> --json
cai workflow validate --json
cai run flow <flowId> --inputs <values.json> --json
cai exec tree <workflowExecutionId> --json
```

Every branch has its intended condition and a wired target; If/Else order matches priority with Else last; Router fan-out is intentional where more than one condition can be true; the loop's item type and list expression compile against real data; the paths the task implies ran: true, false or Else, empty list, one item, several, over the cap, and the intended error path; the execution tree explains every `only_when_false` and `upstream_skipped` and shows no unexplained missing node; a loop's outer success is not proof for every item, so inspect iteration records and surface individual failures.

## Report

Which primitive carries each decision and why, the tested paths with their outcomes, any rule you could not set because the business rule was missing, and any error-continuation you enabled and where.

Read [references/patterns.md](references/patterns.md) for the canonical shapes: guard, exclusive decision, fan-out, grouped conditions, per-item subflow, convergence, return, error path.
