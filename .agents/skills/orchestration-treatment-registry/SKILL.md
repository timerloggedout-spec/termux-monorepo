---
name: orchestration-treatment-registry
description: Define, compare, validate, and evolve repository-native orchestration treatments across TUI, CLI, GitHub, Devin, MCP, and agent surfaces without creating parallel state machines. Use when adopting an external orchestration pattern, designing a new manager, normalizing lifecycle telemetry, or reviewing whether a treatment is ready for promotion.
---

# Orchestration Treatment Registry

Treat external frameworks and native managers as orchestration treatments: comparable, evidence-backed implementation patterns. Do not copy an external architecture wholesale and do not rank treatments.

## Native flow

pattern -> architecture hypothesis -> native schema mapping -> experiment -> evidence -> accepted orchestration primitive

## Canonical identity

Use the same identity vocabulary across TUI, CLI, GitHub, Devin, MCP, and agent adapters:

orchestration_id -> cycle_id -> attempt_id -> action_id -> event_id -> evidence_id -> outcome

A receipt is a projection of one observation. The evidence corpus and context-relationship corpus remain the historical sources.

## Treatment contract

Use docs/ops/ORCHESTRATION-TREATMENT.schema.json.

Capture, where known:
- lineage/source and immutable source SHA;
- manager and strategy;
- capabilities, hooks, tools, and routing;
- wait and retry policies;
- evidence and validation contracts;
- lifecycle status.

Unknown fields stay absent. Never manufacture capabilities, metrics, providers, or validation evidence.

## Lifecycle

candidate -> experimental -> accepted -> deprecated/rejected

Promotion requires current-SHA evidence, relevant deterministic validation, review/finding disposition, and repository-defined gates. accepted means the repository adopted the treatment contract; it is not a performance ranking.

## Receipt semantics

Use docs/ops/ORCHESTRATION-RECEIPT.schema.json.

Keep state, task outcome, and promotion separate:
- state answers where execution is;
- outcome answers whether requested work was achieved;
- promotion answers whether the implementation may be adopted.

Never infer task success from a completed dispatch, a green-looking activity stream, or provider availability.

## Adapter rule

TUI/CLI/GitHub/Devin/MCP adapters emit normalized observations into the native evidence contract. They must not become independent sources of truth.

For Devin, hooks are telemetry adapters: sanitize the event, bind it to repository/ref/SHA where available, then project it into evidence/action-effect records. A hook failure is not a task failure unless the authoritative validation contract says it is.

## Wait rule

Use the repository adaptive-wait contract. Queued or in-progress execution is not success. After material changes, re-fetch the watched SHA and authoritative workflow/check evidence before classification.

## External-pattern rule

External material may supply a pattern or hypothesis. It becomes repository-native only after:
1. explicit schema mapping;
2. bounded implementation;
3. deterministic validation;
4. evidence capture;
5. recorded promotion decision.

This keeps Wingman, Devin, Loopy, and future orchestration systems useful as pattern corpora without making them hidden authorities.

## Related contracts

- docs/ops/EVIDENCE-ENVELOPE.schema.json
- docs/ops/ACTION-EFFECT-EVENT.schema.json
- .agents/skills/adaptive-wait/SKILL.md
- .agents/skills/adaptive-feedback-cycle/SKILL.md
- .agents/skills/context-relationship-graph/SKILL.md
- .github/skills/workflow-orchestration/SKILL.md


## Session capability inventory as a treatment source

Use `ops/capabilities/chatgpt/current.json` to resolve the current dated ChatGPT session catalog. The manifest pins the skill catalog, tool-definition chunks, namespace counts and source hashes.

Treat catalog entries as discovery candidates. For an experiment or adapter proposal, capture:

- snapshot date and manifest SHA-256;
- provider namespace and exact tool identifier;
- exact skill URI and source group, when applicable;
- adapter version and declared operation scope;
- permission tier, context strategy and execution environment;
- orchestration/cycle/attempt identity and evidence references.

Use provider namespace, skill composition, tool selection, manager policy, context strategy and approval tier as candidate DoE treatment factors. Record execution through the canonical event, evidence-envelope and action/effect contracts. Keep catalog availability, account authorization, execution state, task outcome and promotion as separate fields.

A session tool definition supplies an interface description. Repository execution authority remains in the named provider adapter, `hub_mcp/policy.py`, harness admission and the existing approval gates.
