---
name: controllerai-integration-actions
description: Discover, connect, attach, update and verify ready integration actions that a Controller AI agent calls directly. Use when an agent needs one existing app operation without a workflow, when choosing between a direct action and a workflow tool, or when changing an action's connection or per-run approval policy.
---
<!-- generated from .claude/skills by cli/scripts/render-skills.mjs; edit the source -->

# Integration actions

## Use this when

- An agent needs one existing app operation: send one message, create one record, add one row, look something up.
- You must decide between attaching a ready action and building a workflow tool.
- An attached action needs another connection, a different approval policy, or proof that it runs.

Building the agent itself belongs to `controllerai-agents`; a workflow node for the same app belongs to `controllerai-node-config`.

## How it works

**A ready action is one operation.** The catalog exposes provider integration actions that an agent can call directly, without a workflow; native registry actions appear in the same discovery but are not attachable as direct actions, and every direct attachment needs a connection, so native and provider operations carry different authorization requirements. Use a workflow tool instead when the capability needs several operations, transformation, branching, loops, durable state, a trigger, a custom typed contract, or reuse outside the agent. Never wrap a ready action whose contract already fits in a one-node workflow, and never replace deterministic orchestration with several independent direct actions.

**Identity is a pair.** An action is the exact integration slug plus its action key, as returned by discovery; a display label is not an identity, and a similar integration with a familiar name is not evidence of the capability. The action binds to a connection whose `integration` matches that slug exactly.

**Runtime.** The agent runtime configures the action's dynamic arguments when it invokes the action; nothing is preconfigured at attachment beyond identity, connection, description and approval policy. A direct action runs inline in the conversation and creates no workflow execution: the evidence is the persisted conversation, its action events with arguments and result, and the external effect.

**Approval policy.** An attached action runs without a human approval step unless `requireConfirmation` is `true`; the default is no approval. When confirmation is on, the runtime pauses with a pending request that the user approves or denies with the exact arguments visible.

**Live bindings.** Publishing snapshots the action identity, description and approval policy into the agent version. The connection and its authorization grant are live security bindings: rebinding redirects the published action immediately, and revocation, breakage or detachment stops it immediately without an agent publish; detachment also removes the draft tool, and a later publish removes it from the published list. Confirmation is strictest-wins: tightening the grant to require confirmation blocks the published action at once until a publish carries the new policy, while relaxing it waits for the publish. Organization members use the published agent, never the draft; direct actions run through the owner's connected account and the organization's shared usage pool whoever calls them.

## Rules

1. **Capture and reuse the exact identities**: integration slug, action key, connection ID, tool ID. Narrow the query or raise the result limit when more matches exist; never derive an identifier from a label.
2. **A missing connection is a handoff, not a substitution.** Keep the selected integration and action, give the user the authorization route, and stop the attachment there; never swap in `registry_http-http-request` or request provider credentials in chat. A raw endpoint the user mentions is context, not an instruction to hand-roll the call.
3. **Decide the approval policy before attaching.** For an action that sends, posts, spends or deletes, choose `true` or explicitly tell the user it will run unattended; prefer confirmation for permission changes, irreversible writes or an ambiguous destination, and omit it for reads and low-risk reversible operations the user asked to run autonomously. Mention the confirmation choice in the report to the user.
4. **Attach once.** Read the tool list before and after; the final list holds one intended direct attachment.
5. **A stored active connection is not proof of authorization.** Only a representative action test proves the provider still accepts it.
6. **Verify what the request asked for, where it lives.** Discovery proves metadata; a blocked attachment proves the honest handoff and the independent work; an attachment proves the saved grant; only an authorized runtime test proves the external effect, and for that the action event, its arguments and result, and the external state are the evidence, never a reply that says it ran. Inspect the external state before repeating a failed or uncertain mutation.
7. **Say whose account runs the action** before organization sharing: the owner's connection and the organization's usage pool, regardless of caller.

## Recipes

### Discover

```bash
cai integration search "<app or capability>" --json
cai integration actions "<operation>" --integration <integrationSlug> --json
cai integration action --integration <integrationSlug> --key <actionKey> --json
```

`search` ranks integrations (`--actions` or `--events` narrows the kind); `actions` ranks actions across one or all integrations; `action` returns the static metadata and props of one exact action. Read that metadata before choosing.

### Select or request a connection

```bash
cai connection list --integration <integrationSlug> --json
```

Use the active connection whose `integration` matches exactly. If none exists, `cai connection connect <integrationSlug> --no-open` returns the authorization URL: share it right away, and after the user finishes, list again and use the new ID.

### Attach

```bash
cai agent add-action <agentId> --integration <integrationSlug> --action <actionKey> --connection <connectionId> --description "Use when ..." --require-confirmation --json
cai agent tools <agentId> --json
```

`--require-confirmation` sets the policy to `true`; omitting it keeps the `false` default.
The description tells the agent when to choose the tool. Read the saved grant back: `toolType`, integration, action key, connection, description and confirmation policy.

### Update

```bash
cai agent update-tool <agentId> --tool <toolId> --connection <connectionId> --json
cai agent update-tool <agentId> --tool <toolId> --require-confirmation --json
cai agent update-tool <agentId> --tool <toolId> --no-confirmation --json
cai agent update-tool <agentId> --tool <toolId> --description "<when to use it>" --json
```

A connection change redirects the published action at once. A description change waits for the agent publish. A policy change is strictest-wins: turning confirmation on blocks the published action immediately until the next publish carries it, turning it off takes effect only at that publish.

### Verify in a draft conversation

```bash
cai agent test <agentId> --draft --message "<request that needs the action>" --json
cai agent conversation history <conversationId> --json
cai agent conversation approve <conversationId> --request <requestId> --json
cai agent conversation deny <conversationId> --request <requestId> --message "<reason>" --json
```

`agent test` is a one-shot that opens a new conversation; when a follow-up or an approval is expected, create one draft conversation and send into it as in `controllerai-agents`. When confirmation is on, inspect the pending action and its exact arguments, then approve or deny in that same conversation and read the history for the terminal result. Direct actions do not create workflow execution IDs: never invent one.

## Verify

For an attachment, the tool list shows exactly one intended direct attachment with the exact identities, connection, description and confirmation policy; for an authorized runtime test, the draft conversation history holds the action event, its arguments and its result, and the external effect was checked separately; for discovery alone, the exact metadata was read and nothing was changed. No wrapper workflow exists unless orchestration or reuse required it.

## Report

Which action is attached to which agent, its connection and confirmation choice, what the draft test proved, whose account and usage pool the action will use, and what remains: a connection to authorize, a publish, or a live verification.
