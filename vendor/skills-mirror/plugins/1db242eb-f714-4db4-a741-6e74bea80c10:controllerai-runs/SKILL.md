---
name: controllerai-runs
description: "Run Controller AI nodes and flows and read execution evidence: inputs, resolved configs, outputs, ports, skips, warnings and output-type adoption. Use when proving a build works, investigating a failed or green-but-wrong run, resolving a dynamic output type, or checking what an expression produced at runtime."
---
<!-- generated from .claude/skills by cli/scripts/render-skills.mjs; edit the source -->

# Runs

## Use this when

- A node or flow was just built or changed and needs proof with real values.
- A run failed, or finished green with empty, partial or wrong data.
- A dynamic node's output type is unknown and downstream expressions cannot be written.

Expression authoring belongs to `controllerai-expressions`, branch and loop structure to `controllerai-flow-control`, trigger replay to `controllerai-triggers`.

## How it works

**A run is real.** Node runs always execute on development; flow runs execute on development by default or, explicitly, on the published live version. Both call the real providers: messages send, records change, usage is spent. Development isolation covers the workflow data store only.

**Running resolves types.** A dynamic integration node gets its output type from one completed representative run (`outputTypeAdoption`), and every downstream expression depends on that type. When the user declines to run a consequential action, the fallback is a declared output contract built from the provider's documented response; it is marked `declared (unverified)` and the first real completed run verifies it.

**Three scopes.** A node run isolates the node's own configuration and does not execute wired upstream nodes; `runScope.endToEndValidationRequired` is computed from the wiring before the run and says that upstream-derived values need a containing-flow check, while `resolvedConfigs` shows what they actually were. A flow run executes the wiring and proves `inputs.<name>` expressions and the return contract. A discovery run creates a scratch node from a component that is not in the graph inside a reusable scratch flow, executes it and deletes the node (the flow stays), only to learn what it returns; it types nothing in the real flow.

**Inputs are keyed by ID.** `run inputs` lists the exact input IDs a node or flow reads. A flow lists every declared input with a `used` flag: supply the used ones (an omitted used input falls back to its saved test value), and values for unused inputs are accepted and ignored. An isolated node run must receive every referenced `flowInputs[].id` or it fails before executing with `ISOLATED_FLOW_CONTEXT_REQUIRED`. Explicit `null`, `""`, `false` and `0` are supplied values; dates are plain ISO-8601 text.

**The evidence.** `status` and `errorMessage`; `skipReason` (`only_when_false`, `upstream_skipped`); `runScope`; `resolvedConfigs`, where a null entry on a dynamic prop that the contract did not intend is a silent expression failure on an otherwise green run, and each entry's `resolutionWarnings` (an explicit `[]` means the resolver reported nothing; the value still has to match the contract); the output shape and values; and the adoption result, `outputTypeAdoption` on a node run or `outputTypeAdoptions` on a flow run, where `adopted` or `already_typed` lets the node status converge, `no_observed_output` means the run returned no reusable shape, and each entry's `adoptedNodeIds` must be empty or name only its own node.

**Outcomes.** A run ends `completed`, `completed_with_error` (a handled error path, the expected result when testing continue-on-error), `failed` or `cancelled`; it can also stop `paused` waiting on something, or still be running when the wait ends. The CLI polls until a terminal status, a pause or its `--timeout` (milliseconds); a non-success result exits non-zero and carries the execution ID and last snapshot in `error.detail`. A running or paused status means inspect that execution later, never dispatch the run again.

## Rules

1. **Mitigate, do not refuse.** Before a send, delete, charge or people-affecting run, say what will really happen and agree a safe target: the user's own address or channel, a record created for the test, a person the user names. Reuse authorization the task already gave; ask only for what it did not cover.
2. **A declined run is declared, not skipped.** Declare the output from the provider's documented response, say it is unverified, and name the first real run as the verification step.
3. **Smallest scope first, then the containing flow.** A node run proves configuration; only a flow run proves upstream-derived values and the return value.
4. **Green is not proof, and red is not always failure.** Read resolved configs, outputs, ports and skips; a `completed` run with empty or null output is a failure until the values are read and explained, a null dynamic config the contract did not intend is a failure even when the status is green, and a run that matched the scenario's expected status, outputs and effects passed even when that status is `completed_with_error`. `0` and `false` are values.
5. **Find the first divergence, not the last error.** Walk the execution tree, classify each node as completed, failed, skipped on purpose, skipped unexpectedly or absent; later failures are usually consequences.
6. **Verify the effect where it lives.** Data writes: query the same store. Files: open the artifact. Provider actions: the provider's result, not the execution ID.
7. **Never let a stalled run become a duplicate.** Inspect the returned execution; rerun only after it reached a terminal state and the cause is understood.
8. **Adoption stays on the tested node.** Stop if `adoptedNodeIds` names a sibling, and re-read `node status` and downstream expression contexts after a type is adopted.

## Recipes

### Prepare inputs and run

```bash
cai run inputs <nodeId> --json
cai run inputs <flowId> --flow --json
cai run node <nodeId> --inputs <values.json> --json
cai run flow <flowId> --inputs <values.json> --json
```

`--inputs` takes inline JSON, a file path or `-` for stdin; the value is a flat map of input ID to value. `--timeout <ms>` bounds the wait.

### Declare an output the user will not run yet

```bash
cai node declare-output <nodeId> --sample-file <shape.json>
```

The sample is a representative response object (or a non-empty array of them) taken from the provider's API reference.

### Discover what a component returns

```bash
cai run discover --node <nodeSlug> --key <componentKey> --connection <connectionId|none> --props '<json>' --json
```

`--connection` is required (`none` for a component without auth); `--enable <prop>` enables optional props first; `--keep` retains the scratch node only when the user wants it.
Discovery calls the real action and spends usage. Never probe a destructive action just to learn its output: agree a safe target or declare the shape instead. Prefer testing a configured node: discovery returns `observedOutputType`, `nodeExecution`, `workflowExecutionId`, `scratchFlowId` and `nodeDeleted`, the full execution stays readable by ID, and the real node in the flow still has to be typed by its own run or a declaration.
With `--keep` the scratch node stays as well.

### Verify the published version

```bash
cai run flow <flowId> --inputs <values.json> --target live --confirm-live --json
```

When the user authorized live verification and named a safe target, run the published flow once under supervision instead of waiting for a real trigger event. It fires real actions and spends usage. Where the design calls for it, a safe-audience harness (an If/Else on `isLiveVersion` whose false branch targets the developer and whose true branch targets the real audience) protects development runs; the live run is still a real send, and adding that harness is a design change to agree, not a test step.

### Read the execution

```bash
cai exec tree <workflowExecutionId> --limit 50 --json
cai exec get <workflowExecutionId> --json
cai exec flow <flowExecutionId> --json
cai exec node <nodeExecutionId> --full --json
```

Page the tree with the returned `nextCursor` (`--cursor`) and narrow a large run with repeatable `--status` or an exact `--flow <flowId>`. The tree locates the first unexpected status; the full node execution holds the resolved configuration and the untruncated output. Read [references/debugging.md](references/debugging.md) for the fault-isolation order and the symptom table.

## Verify

The run exercised the changed path with credible values; the first unexpected node, if any, was identified from the tree; every dynamic config resolved to the intended value and `resolutionWarnings` were read; the output shape and values match what downstream expects; skips are intentional and error paths accounted for; a flow run reached the scenario's expected status, outputs and effects after isolated fixes; the stored or external effect was checked where it lives; and any declared contract is still marked unverified in the report.

## Report

What ran and on which version, the execution IDs, what each run proved, what is declared but unverified, and what remains untested and why.
