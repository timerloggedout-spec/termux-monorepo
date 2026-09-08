# ArchW1z UI / Shared Protocol Boundary

## North star

ArchW1z is the **Termux/mobile UI and operator cockpit** for the autonomous engineering environment. It is not the canonical job-orchestration protocol.

```text
ArchW1z TUI / mobile UI
        |
        v
   client protocol
        |
        v
hub_mcp policy + capability boundary
        |
        v
job / event / evidence protocol
        |
        +-------------------+
        v                   v
GitHub coordination   Termux execution adapters
```

## Why this boundary matters

The UI lane must remain replaceable. The same protocol should be usable by GitHub Actions, autonomous agents, remote workers, future mobile clients, and other operator surfaces. A UI-specific job model would create a second orchestration system and make later integration expensive.

## Client operations

- **observe** — read current task, agent, workflow, evidence, and event state.
- **inspect** — retrieve authoritative source/evidence for a selected object.
- **dispatch** — submit an authorized handoff/job envelope.
- **approve/escalate** — record an explicit human/authority decision when the operating mode requires it.
- **stop** — request an authorized cancellation/containment action.

The client displays and submits protocol objects. It does not invent alternative lifecycle semantics.

## Handoff envelope

```yaml
handoff:
  id: HND-...
  parent_task: TASK-...
  source_agent: archwiz
  destination_agent: worker
  objective: "..."
  context:
    repository: timerloggedout-spec/termux-monorepo
    ref: master
    sha: "..."
  authority:
    scopes: []
  constraints: []
  evidence: []
  expected_outputs: []
  completion:
    acceptance: []
  escalation:
    conditions: []
```

## Operating modes

1. **HITL** — human decision at configured authority edges.
2. **Supervised autonomous** — routine execution under predeclared capability and policy scopes.
3. **Autonomous** — policy-eligible planning, delegation, execution, verification, repair, and promotion without routine human queueing.

Mode is protocol state, not a separate UI implementation.

## Evidence and UI authority

Dashboards and model summaries are observations. Canonical state remains in protocol/GitHub sources.

## Termux role

Termux is the first execution target and the natural host for the TUI/mobile client. Device transport, credentials, and remote execution remain separately governed.
