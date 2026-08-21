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

The initial client contract is intentionally small:

- **observe** — read current task, agent, workflow, evidence, and event state.
- **inspect** — retrieve authoritative source/evidence for a selected object.
- **dispatch** — submit an authorized handoff/job envelope.
- **approve/escalate** — record an explicit human/authority decision when the operating mode requires it.
- **stop** — request an authorized cancellation/containment action; destructive or authority-only operations remain governed by existing policy.

The client displays and submits protocol objects. It does not invent alternative lifecycle semantics.

## Handoff envelope

A handoff should carry at minimum:

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

The eventual schema should add versioning, expiry, idempotency, provenance, and replay handling consistent with `hub_mcp`.

## Operating modes

The same protocol supports:

1. **HITL** — human decision at configured authority edges.
2. **Supervised autonomous** — routine execution under predeclared capability and policy scopes, with escalation for exceptional states.
3. **Autonomous** — policy-eligible planning, delegation, execution, verification, repair, and promotion without routine human queueing.

Mode is protocol state, not a separate UI implementation.

## Capability vs authorization

A model or agent may have a capability without having authority to invoke it against a target. The client should render both separately. Authorization should be scoped to repository, ref/SHA, operation class, target, and applicable policy.

## Evidence and UI authority

Dashboards, cards, cached indexes, and model summaries are observations. The client should link back to the authoritative protocol object, GitHub state, source file, check result, or review record. A UI presentation may propose an action but does not become authoritative merely because it is displayed.

## Termux role

Termux is the first execution target and the natural host for the TUI/mobile client. The UI may later gain richer mobile presentation, but device transport, public exposure, credentials, and remote execution remain separately governed concerns.

## Future evolution

Research, reverse engineering, adversarial testing, self-healing, and evolutionary experiments should use the same handoff/evidence/promotion primitives. Experimental changes may produce policy candidates; promotion into active policy remains an explicit, versioned, reviewable state transition.
