# Agent Orchestration — Design

> **Evidence status:** architecture defined; operator experience candidate  
> **Design owner:** Agent Team Control Plane maintainers  
> **Canonical implementation:** control-plane sources linked below  
> **Last source review:** 2026-11-23

## 1. Purpose and users

The Agent Team Control Plane owns agent lifecycle, dispatch, coordination, and evidence semantics. This design entry focuses on how operators observe and direct those capabilities.

## 2. Experience surfaces

| Surface | Audience | Evidence status | Owning source |
|---|---|---|---|
| Agent Team Control Plane | Operators / agent maintainers | Architecture defined | [Control Plane](../../../architecture/AGENT-TEAM-CONTROL-PLANE.md) |
| ArchWiz operator client | Operators | Separate design entry | [ArchWiz design](../archwiz/design.md) |
| Dashboard projections | Readers / operators | Read-only projections | [SHE design](../she-dashboard/design.md), [Tribute design](../tribute-dashboard/design.md) |

## 3. Information architecture

The control-plane source owns lifecycle and coordination concepts. A user-facing view should preserve those source concepts and their distinct states rather than flattening them into one generic task status.

## 4. Journeys and interactions

Operator journeys should be traced from observation through evidence inspection, dispatch, review, and escalation where supported by the control-plane and client contracts. This entry records those as a mapping target; exact UI behavior requires client evidence.

## 5. Visual language

Shared visual conventions are indexed in [visual-language](../../_shared/visual-language.md). Dashboard projections and terminal clients retain their own layout constraints.

## 6. Accessibility

Record accessibility evidence per client. The control-plane architecture does not itself establish interface conformance.

## 7. Evidence and system states

Preserve event lineage, task state, evidence, review, and completion distinctions from the control-plane contract. A green job or successful dispatch alone does not establish task outcome.

## 8. Decisions and open gaps

- Map each operator action to an explicit control-plane operation and authority.
- Document task/agent lifecycle views and transitions.
- Identify which views are authoritative versus read-only projections.
- Record review, cancellation, failure, and escalation recovery paths.

## 9. Canonical sources

- [Agent Team Control Plane](../../../architecture/AGENT-TEAM-CONTROL-PLANE.md)
- [ArchWiz UI protocol](../../../proposals/active/archwiz-ui-protocol/ITEMS.md)
- [Evidence Projection Surface](../../../ops/EVIDENCE-PROJECTION-SURFACE.md)
- [Adaptive feedback cycle](../../../../.agents/skills/adaptive-feedback-cycle/SKILL.md)
