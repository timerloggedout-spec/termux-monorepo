# Native Orchestration Contracts

## Purpose

The repository already has evidence, relationship, wait, review, and workflow contracts. This layer provides a stable vocabulary for comparing orchestration implementations across surfaces without creating a second control plane.

## Four layers

1. Surfaces: TUI, CLI, GitHub UI, Devin, MCP, and agent entry points.
2. Orchestration: routers, supervisors, managers, planners, mutators, and review/cycle controllers.
3. Evidence/state: SHA, run/job/step/artifact IDs, receipts, relationship observations, and outcomes.
4. SSOT/schemas: ICM, proposal governance, registries, JSON schemas, policy, and lane contracts.

Surfaces project state; they do not own it.

## Canonical lifecycle

RECON -> PLAN -> ACT -> COMMIT -> WAIT -> WATCH -> VALIDATE -> RE-FETCH -> COMPARE -> CLASSIFY -> RECORD -> REPEAT

The existing evidence-led loop and adaptive-wait semantics remain authoritative.

## State model

| Dimension | Values | Meaning |
|---|---|---|
| execution state | DISPATCHED, QUEUED, RUNNING, WAITING, STEERED, RETRYING, COMPLETED, FAILED, CANCELLED | lifecycle position |
| task outcome | TASK_PASS, TASK_FAIL, UNKNOWN | requested-work result |
| promotion | PROMOTABLE, NOT_PROMOTABLE, UNKNOWN | adoption decision |

A successful API call, completed agent session, or workflow completion must not be confused with task success.

## Identity model

orchestration_id -> cycle_id -> attempt_id -> action_id -> event_id -> evidence_id

Join external observations using stable GitHub run/job/artifact IDs and repository SHA/ref. Do not infer causality from comment volume, actor identity, or graph edge count.

## Treatment model

A treatment is a reusable orchestration pattern described by ORCHESTRATION-TREATMENT.schema.json.

External source patterns may include native managers, Wingman, Devin plugin/hooks, Loopy-style bounded loops, or future systems. Their source material supplies hypotheses; it does not authorize repository behavior.

## Adapter model

Each adapter emits the same normalized receipt vocabulary. Provider-specific adapters may add provider fields, but preserve canonical IDs, repository/ref/SHA, lifecycle state, outcome, promotion, evidence IDs, and timestamp.

### Devin

hook -> sanitized event -> native evidence envelope -> action/effect event -> relationship graph

Hooks observe. They do not become a hidden decision engine.

### GitHub

Treat GitHub as execution/event fabric:

dispatch -> workflow/run/job/step/artifact -> validation -> receipt/evidence

A queued or in-progress run remains unclassified until terminal evidence is available.

## Promotion gate

An experimental treatment can move to accepted only when the record contains:
- current-SHA alignment;
- deterministic relevant validation;
- authoritative workflow/check evidence where applicable;
- review/finding disposition;
- explicit remaining-unproven-work assessment;
- repository-defined dual gates.

## Security boundary

Adapters must not persist credentials, tokens, session stores, browser profiles, or discussion bodies into orchestration receipts. Store stable IDs and evidence references instead.

## Relationship to existing contracts

This composition layer references, rather than duplicates:
- EVIDENCE-ENVELOPE.schema.json for normalized observations;
- ACTION-EFFECT-EVENT.schema.json for temporal follow-through;
- context-relationship-graph for longitudinal history;
- adaptive-wait for terminal-state collection;
- workflow-orchestration for modular Actions;
- evidence-led-monorepo-ops for mutation and promotion discipline.
