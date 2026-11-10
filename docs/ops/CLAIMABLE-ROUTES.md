# Claimable routes — the D-h pullable trigger registry

The registry of record is [`ops/dispatch/claimable-routes.json`](../dispatch/claimable-routes.json)
(schema `claimable-routes/v1`). This doc is its human view.

## Why this exists (D-h)

The dispatch claim/lease machinery let a producer seat *claim* a task, but
a claim engaged nothing: there was no registered, pullable trigger a seat
could fire to turn a claim into execution, so execution waited on chat
routing. D-h closes that gap:

- Every route that can move a claimed task toward execution is **registered**
  in `ops/dispatch/claimable-routes.json` with its real trigger, inputs,
  producer class, and receipt surface — each row read from the workflow of
  record, never from folklore.
- **A route is claimable only if it is registered here.** Register a new
  route in the same PR that adds its workflow.
- A claim is not pulled until the route fires and stamps its receipt.

## How a producer seat pulls work

1. **Claim** the task issue (the dispatch claim stamp names the claiming
   seat, its session, and the claim time).
2. **Fire a registered route** for that issue, using the trigger and inputs
   in its registry row — e.g. post the route's trigger comment on the issue,
   or dispatch its workflow with the named inputs.
3. **The route stamps the receipt.** Firing is not done when the button is
   pressed; it is done when the route's receipt lands on the issue. The
   receipt/claim stamp names:
   - **firing hand** — who or what fired the route (the actor / seat);
   - **route** — the registry row's route name;
   - **run id** — the Actions run that is executing (with its URL);
   - **heartbeat deadline** — the instant by which an outcome (a PR, an
     honest already-exists comment, or a failure stamp) must land.
4. **Watch the heartbeat, not the chat.** If the heartbeat deadline passes
   with no outcome, the claim is stalled and watchdog-ageable: re-fire,
   reassign, or escalate on the record. A silent or false-green run is a
   defect, never a success.

## The routes

| Route | Workflow | Trigger | Producer class | Receipt lands |
|---|---|---|---|---|
| `build-dispatch` | `.github/workflows/build-dispatch.yml` | `@gemini-cli /build` issue comment (OWNER/MEMBER/COLLABORATOR) or `workflow_dispatch` {issue_number, branch?} | Gemini build arm (`run-gemini-cli`, `gemini-3.5-flash-lite`) under the Termux Fleet Swarm App token | Pre-builder receipt comment on the build issue {route · run_id · branch · fired_by · heartbeat_deadline = start + 75 min}; outcome = PR against master or already-exists comment; failures post a run-failed comment |
| `project-task-dispatch` | `.github/workflows/project-task-dispatch.yml` | `issues` opened/reopened, keyed on the `project-task` label or a `[task]` title prefix | Intake router — validates the filing, posts the routing receipt, queues; selection/execution in the claim/dispatch machinery | Routing receipt comment + `dispatch-queued` label (valid) or intake diagnosis + `intake-incomplete` label |
| `game-development-dispatch` | `.github/workflows/game-development-dispatch.yml` | `workflow_run` on `swarm-admission` completed/success, selecting admitted `game-development-task.yml` filings from the `issue-admission` handoff artifact | Admission-follower queueing route; provider selection/execution remain in the claim/dispatch machinery | Queueing comment + `game-development` and `dispatch-queued` labels (valid) or intake diagnosis + `intake-incomplete` |
| `provider-command-dispatch` | `.github/workflows/provider-command-dispatch.yml` | `workflow_dispatch` or `repository_dispatch` type `provider-command` | Provider-command operator — one explicit, allowlisted provider operation (coderabbit/qodo/devin) on an open PR | Dispatch receipt on the PR (marker `<!-- operator-provider-command:v1 -->`) + a stamp fanned out to the scoring planes via `dispatch-stamp-fanout.yml` |

`build-dispatch` is the build arm among these: it is the only registered
route that turns a claimed issue into code (a branch and a PR). It is not
the `gemini-dispatch` invoke router — that route is text-only. The arm is
the `run-gemini-cli` full-checkout builder ported from
`timerloggedout-spec/repo-story` (issue #5108, parent #5096), where its
proving run 41426129878 produced repo-story PR #6.

## Adding a route

1. Land the workflow.
2. In the **same PR**, add its row to `ops/dispatch/claimable-routes.json`
   — facts read from the workflow file itself — and add its line to the
   table above.
3. The route's receipt must name {firing hand · route · run id · heartbeat
   deadline} (or the closest honest equivalent for event-driven routes:
   the receipt comment and labels the route itself posts). A route whose
   runs can end silently is not registrable until its failure surface
   exists.
