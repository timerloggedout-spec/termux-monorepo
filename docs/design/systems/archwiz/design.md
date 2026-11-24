# ArchWiz — Design

> **Evidence status:** proposed / partially implemented  
> **Design owner:** ArchWiz UI and protocol maintainers  
> **Canonical implementation:** `archwiz/` and ICM source cards  
> **Last source review:** 2026-11-23

## 1. Purpose and users

ArchWiz is identified in the repository ICM as an operator cockpit and bounded operational tool surface. The UI protocol proposal frames it as a Termux/mobile client over shared agentic protocols.

## 2. Experience surfaces

| Surface | Audience | Evidence status | Owning source |
|---|---|---|---|
| Operator cockpit / TUI | Operators | Existing system; details in source | [ArchWiz ICM card](../../../icm/objects/operations/archwiz.md) |
| Termux/mobile UI protocol | Operators | Posted proposal | [Protocol items](../../../proposals/active/archwiz-ui-protocol/ITEMS.md) |
| Visual review | Human reviewers | Initiated process | [Optional visual review](../../../icm/objects/operations/optional-visual-review.md) |

## 3. Information architecture

The ICM card owns current tool and component navigation. The UI protocol proposal identifies observe, inspect, dispatch, approve/escalate, and authorized stop as primary operation categories.

## 4. Journeys and interactions

Treat the proposal's five operation categories as proposed client capabilities. The shared protocols retain job, event, handoff, capability, authorization, and evidence semantics. The client presents those contracts rather than defining a parallel execution model.

## 5. Visual language

Visual review artifacts and operator cockpit components remain owned by their implementation sources. Cross-system guidance lives in [visual language](../../_shared/visual-language.md).

## 6. Accessibility

Record keyboard operation, focus, terminal constraints, and any mobile accessibility behavior from the actual client implementation. The proposal alone does not establish conformance.

## 7. Evidence and system states

Keep observation separate from authority. Dispatch, approval, escalation, and stop actions must reflect the protocol capability and authorization contract. Surface evidence lineage and completion state from authoritative sources.

## 8. Decisions and open gaps

- Reconcile the posted UI protocol proposal with current implementation.
- Identify which operation categories are implemented and which remain proposed.
- Map query/context-builder and visualization entry points to user journeys.
- Record mobile-specific surface scope and accessibility evidence.

## 9. Canonical sources

- [ArchWiz ICM card](../../../icm/objects/operations/archwiz.md)
- [UI protocol items](../../../proposals/active/archwiz-ui-protocol/ITEMS.md)
- [Optional visual review](../../../icm/objects/operations/optional-visual-review.md)
- [Agent Team Control Plane](../../../architecture/AGENT-TEAM-CONTROL-PLANE.md)
