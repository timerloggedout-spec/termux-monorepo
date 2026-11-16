# Agentic-Agile Process Integration

## Purpose

This document adapts the public Agentic-Agile patterns from Microsoft's `agentic-agile-template` to the existing `termux-monorepo` Agentic Development Environment (ADE).

The key architectural decision is **adapter, not replacement**. The repository already has a deterministic dependency-phase control plane. Agentic-Agile supplies process vocabulary—specification, work-unit decomposition, parallel waves, review gates, and retrospectives—while the repository's existing phase engine remains the machine authority.

## Canonical implementation boundary

The authoritative lifecycle artifacts are already:

- `docs/agentic/dependency-phases.json` — canonical phase/dependency policy.
- `docs/agentic/phase-approvals.json` — explicit approval evidence.
- `scripts/agentic/dependency_phase_engine.py` — pure validation/evaluation/rendering engine.
- `scripts/agentic/dependency_phases.py` — lifecycle CLI.
- `scripts/agentic/github_phase_adapter.py` — live GitHub evidence adapter.
- `.github/workflows/dependency-phase-*.yml` — validation, evaluation, synchronization, and controlled dispatch.
- `tests/test_dependency_phase_engine.py` — lifecycle invariants and fail-closed fixtures.

Generated Markdown/Mermaid views, Project cards, dashboards, issue prose, and agent comments remain derived evidence/views rather than authority.

This means Agentic-Agile **must not introduce a second canonical YAML plan, second dependency evaluator, or competing claim protocol**.

## Adopted principles

| Agentic-Agile pattern | Existing ADE implementation |
|---|---|
| Specifications/contracts over open-ended prompts | Phase records define stable identity, description, dependencies, execution policy, required checks, approval requirements, and completion evidence before dispatch. |
| Independently executable work units | Stable `phase_id` units with deterministic dependency evaluation and existing PR/file-claim coordination. |
| Parallel waves | Independent ready phases may be admitted concurrently when their dependencies and ownership evidence permit it; dependent phases remain `waiting`. |
| Review gates | `awaiting_review`, required checks, merged-PR evidence, and explicit approvals gate downstream evaluation. |
| Humans design, agents execute, both review | Canonical plans and approval evidence are reviewable repository state; agent execution is bounded by the phase policy. |
| Built-in governance | Prohibited actions, approval requirements, branch boundaries, claim idempotency, and least-privilege workflows are encoded in the existing control plane. |
| Continuous measurement | Existing provenance, evidence, ATES/WTCV/3L0, and workflow telemetry remain the measurement layer. |
| Autonomy earned through evidence | A phase becomes dispatchable only from deterministic current evidence; a completion claim cannot substitute for merged-PR/check evidence. |
| Retrospectives improve the system | Repeated process findings should become changes to phase contracts, validators, workflows, tests, or skills rather than remaining conversational advice. |

## Agentic-Agile lifecycle mapped onto the ADE

```text
INTAKE
  ↓
SPECIFY
  ↓
DECOMPOSE INTO PHASES
  ↓
DEPENDENCY / OWNERSHIP CHECK
  ↓
WAVE ADMISSION (ready)
  ↓
AGENT / HUMAN EXECUTION
  ↓
REVIEW GATE (awaiting_review / blocked)
  ↓
EVIDENCE VALIDATION
  ↓
INTEGRATION (merged PR + required checks)
  ↓
RETROSPECTIVE / LEARNING RECORD
  ↓
NEXT WAVE
```

The existing runtime observation loop remains nested inside execution:

```text
ACT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD
```

A phase is therefore not complete because an agent says it is complete. The current evaluator requires the configured completion evidence, including merged-PR/check evidence and the repository's Project state, before dependents unlock.

## Work-unit contract

The ADE phase contract is the normalized work-unit boundary. At minimum, a phase carries:

- stable `phase_id`
- human-readable title and description
- explicit `depends_on` list
- governing Project identity
- explicit `approval_required` state
- bounded execution mode and approved agent
- required completion checks
- merged-PR completion requirement

Agent prompts may contain task-specific scope, negative constraints, file ownership, and acceptance details, but those are **derived from and subordinate to the canonical phase/proposal records**. They must not become a second source of lifecycle truth.

## Wave and concurrency rules

1. A phase with incomplete prerequisites remains `waiting`; it is not dispatched.
2. An approval-required phase without explicit approval evidence remains `blocked`.
3. An active claim or linked PR produces `running`/review states; it does not authorize duplicate execution.
4. Independent ready phases may occupy the same execution wave when their scopes do not conflict and capacity permits.
5. Shared-file ambiguity blocks parallel admission until ownership is explicit.
6. A stale SHA or changed plan hash requires fresh evaluation before execution continues.
7. Retries are new controlled observations; they do not overwrite the previous attempt.
8. No automatic merge, proposal closure, submodule update, or approval inference is introduced by this methodology.

## Review-gate contract

Every gate should answer:

- **What changed?** Compare expected scope with observed PR/diff state.
- **Does it satisfy the contract?** Evaluate required checks and completion evidence.
- **Can the next wave safely start?** Re-evaluate dependencies, ownership, approvals, and current plan hash.
- **What did we learn?** Record process findings separately from task outcome.

The lifecycle engine already distinguishes:

- `invalid` — plan/schema/graph is unsafe; fail closed.
- `waiting` — prerequisites incomplete.
- `blocked` — approval/evidence/conflict prevents safe execution.
- `ready` — current evidence permits one idempotent claim.
- `running` — active claim or linked implementation exists.
- `awaiting_review` — implementation exists but review/check evidence is incomplete.
- `complete` — required completion evidence agrees.

These lifecycle states must remain distinct from workflow transport states such as queued, in-progress, cancelled, or successful.

## Retrospective / learning loop

A completed wave should produce reusable process findings, classified at least as:

| Gap | Meaning |
|---|---|
| `spec_gap` | Requirement or acceptance contract was missing/ambiguous. |
| `decomposition_gap` | Dependency, phase boundary, or ownership collision was hidden. |
| `execution_gap` | Agent/provider/tool execution failed or stalled. |
| `verification_gap` | Evidence was missing, weak, or incorrectly interpreted. |
| `integration_gap` | Merge/reconciliation caused conflict or unexpected state. |
| `governance_gap` | Authority, approval, branch, or policy boundary was wrong. |
| `environment_gap` | CI, runtime, network, quota, or tooling condition affected execution. |

A repeated finding should become a durable repository change—validator rule, fixture, workflow guard, phase template, skill, or documentation update. This is the **continuous improvement loop**, not a separate task-management database.

## Practical operating protocol

For future multi-agent work:

1. Convert the human request into bounded phase/work units.
2. Attach explicit acceptance evidence and negative constraints.
3. Establish dependency edges and file/path ownership.
4. Evaluate the canonical phase plan before dispatch.
5. Admit independent ready units as a wave.
6. Execute with the existing runtime watcher loop.
7. Hold the review/evidence gate before unlocking dependents.
8. Integrate once and measure the integrated outcome.
9. Record the retrospective/learning signal.
10. Promote repeated improvements into the phase engine, workflows, tests, or skills.

## Source and adaptation boundary

The upstream reference is Microsoft's `agentic-agile-template`, particularly its Agentic-Agile Manifesto, universal agent entry point, evaluation framework, and epic/wave decomposition guidance.

The upstream methodology is a process input. The ADE retains its own canonical state, evidence model, attribution/provenance rules, provider catalog, bounded authority, and promotion gates.

No claim about upstream methodology is treated as evidence about ADE runtime performance. Runtime conclusions continue to require repository/workflow evidence.

## Implementation consequence

The next engineering increments should **extend the existing dependency-phase engine**, rather than create a parallel Agentic-Agile engine:

1. Add optional work-unit metadata where the current phase schema lacks it.
2. Add deterministic wave computation from the existing DAG.
3. Add explicit file/path ownership validation where dispatch adapters need it.
4. Add retrospective fields to the existing learning/evidence records.
5. Expose the resulting wave/gate state through the existing generated status views.
6. Validate each increment with the current dependency-phase unit suite and repository gates.

This preserves one source of truth while importing the useful Agentic-Agile process mechanics.
