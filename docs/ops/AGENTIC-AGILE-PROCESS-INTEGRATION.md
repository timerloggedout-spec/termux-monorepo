# Agentic-Agile Process Integration

## Purpose

This document adapts the public Agentic-Agile patterns from Microsoft's agentic-agile-template to the existing termux-monorepo Agentic Development Environment (ADE).

The intent is integration, not replacement. The repository already has runtime observation, provenance, bounded authority, orchestration policy, and the WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → RECORD loop. Agentic-Agile adds a clearer work-contract and wave-governance layer around those capabilities.

## Adopted principles

| Agentic-Agile pattern | ADE implementation |
|---|---|
| Specifications/contracts over open-ended prompts | Every dispatched unit records objective, scope, constraints, acceptance evidence, and negative constraints before execution. |
| Independently executable work units | Work units declare file/path ownership and dependency edges before parallel admission. |
| Parallel waves | Independent units may execute concurrently; dependent units wait for an explicit gate. |
| Review gates | A wave cannot unlock its dependents from a completion claim alone; the gate requires observable evidence. |
| Humans design, agents execute, both review | Agents operate inside bounded authority; review and promotion remain evidence-driven control points. |
| Built-in governance | Authority, source ownership, writer leases, secret boundaries, and promotion rules are part of the execution contract. |
| Continuous measurement | Existing ATES/WTCV/3L0/evidence lanes measure the partnership and the integrated outcome. |
| Autonomy earned through evidence | Scope of autonomous execution expands only after repeated validated observations, not after a single green run. |
| Retrospectives improve the system | Every completed wave should emit reusable process findings: spec gap, decomposition gap, routing gap, verification gap, or environment/provider failure. |

## Canonical work-unit contract

A dispatchable unit SHOULD be representable as:

```yaml
id: <stable-work-id>
objective: <observable outcome>
scope:
  paths: []
  repositories: []
  refs: []
ownership:
  writer: <agent-or-role>
  readers: []
dependencies: []
wave: <integer>
constraints:
  negative: []
acceptance:
  checks: []
  evidence: []
authority:
  tier: <bounded-tier>
  promotion_required: <boolean>
runtime:
  manager: <policy-version>
  provider: <provider>
  model: <model-or-catalog-selector>
```

The contract is compatible with the existing evidence identity: manager + task + role + provider + model + workflow_run + head_sha.

## Wave lifecycle

```text
INTAKE
  ↓
SPECIFY
  ↓
DECOMPOSE
  ↓
OWNERSHIP / DEPENDENCY CHECK
  ↓
WAVE ADMISSION
  ↓
PARALLEL EXECUTION
  ↓
REVIEW GATE
  ↓
EVIDENCE VALIDATION
  ↓
INTEGRATION
  ↓
RETROSPECTIVE
  ↓
NEXT WAVE
```

The runtime observation loop remains nested inside execution: ACT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD.

Thus a wave is not complete merely because its jobs terminate successfully. It completes when the resulting state satisfies its acceptance contract and the evidence is recorded.

## Dependency and ownership rules

1. Two units in the same wave MUST NOT have overlapping write ownership unless an explicit writer lease permits it.
2. A dependency MUST name the evidence or interface that unlocks the dependent unit.
3. A completion comment, label, or route declaration is not sufficient evidence by itself.
4. A stale SHA invalidates work whose acceptance depends on current repository state.
5. Ambiguous ownership blocks parallel admission rather than silently choosing a writer.
6. Integration files and shared contracts SHOULD be isolated into explicit foundation/integration waves.
7. Failed execution is recorded as an observation and classified before retry; retry is a new controlled attempt, not a rewrite of history.

## Review-gate contract

Each gate should answer four questions:

- What changed? Compare the expected scope with the observed diff/state.
- Does it satisfy the contract? Run the declared acceptance checks.
- Can the next wave safely start? Verify dependency, interface, and ownership conditions.
- What did we learn? Record process findings separately from task outcome.

Gate outcomes:

- OPEN — evidence incomplete.
- PASS — acceptance evidence sufficient.
- BLOCKED — dependency, authority, ownership, or environment prevents safe continuation.
- FAIL — execution occurred but acceptance evidence is negative.
- UNKNOWN — insufficient evidence to classify.

These states must remain distinct from workflow execution states such as queued, in-progress, cancelled, or successful.

## Retrospective schema

A retrospective SHOULD record:

| Field | Meaning |
|---|---|
| work_unit | Stable unit identity |
| wave | Execution wave |
| outcome | Contract result |
| spec_gap | Missing/ambiguous requirement |
| decomposition_gap | Hidden dependency or ownership collision |
| execution_gap | Agent/provider/tool failure |
| verification_gap | Missing or weak evidence |
| integration_gap | Merge/conflict/reconciliation problem |
| governance_gap | Authority or policy problem |
| environment_gap | CI/runtime/network/tooling problem |
| action | Concrete process change |
| evidence_ref | Durable supporting evidence |

Repeated retrospective findings SHOULD become skill, template, test, or workflow changes rather than remaining conversational advice.

## What this changes in practice

1. Convert the human request into one or more bounded work units.
2. Capture acceptance criteria and negative constraints before dispatch.
3. Build a dependency graph and assign file/path ownership.
4. Group independent units into waves.
5. Admit a wave only after ownership/dependency checks pass.
6. Execute with the existing runtime watcher loop.
7. Hold a review/evidence gate before unlocking dependent waves.
8. Integrate once, then measure the integrated outcome.
9. Record a retrospective and promote reusable process improvements into repository automation/skills.
10. Treat autonomy as an evidence-backed capability that can expand or contract.

## Source and adaptation boundary

The upstream reference is Microsoft's agentic-agile-template, particularly its Agentic-Agile Manifesto, universal agent entry point, evaluation framework, and epic/wave decomposition guidance.

This repository does not copy the upstream template wholesale. It retains ADE-specific controls for provenance, attribution confidence, dynamic provider catalogs, bounded authority, runtime observation, and Moneyball/3L0 measurement.

The upstream methodology is therefore a process input; the repository's observed runtime evidence remains the authority for claims about this ADE.