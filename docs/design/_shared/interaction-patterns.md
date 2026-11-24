# Shared Interaction Patterns

**Scope:** reusable user/operator interaction concepts. Protocols and capability contracts remain owned by their source documents.

## Current evidence

- [ArchWiz UI protocol items](../../proposals/active/archwiz-ui-protocol/ITEMS.md) identify observe, inspect, dispatch, approve/escalate, and authorized stop operations.
- [Linguist Panel](../../ops/LINGUIST-PANEL.md) documents a focused operator-facing panel.
- [Optional visual review](../../icm/objects/operations/optional-visual-review.md) defines a human review boundary.
- [Terminal dashboard items](../../proposals/active/ratatui-tokio-terminal-dashboard/ITEMS.md) specify asynchronous event/state handling and terminal lifecycle concerns.

## Pattern vocabulary

| Pattern | Evidence status | Source |
|---|---|---|
| Observe current state | Proposed protocol operation | ArchWiz UI protocol |
| Inspect supporting evidence | Proposed protocol operation | ArchWiz UI protocol |
| Dispatch authorized work | Proposed protocol operation | ArchWiz UI protocol |
| Approve / escalate | Proposed protocol operation | ArchWiz UI protocol |
| Stop authorized work | Proposed protocol operation | ArchWiz UI protocol |
| Human visual review | Existing ICM process card | Optional visual review |
| Async event-to-view update | Terminal implementation proposal | Ratatui + Tokio items |

These are source-derived concepts, not a mandate for every product to implement every operation.

## State and authority rules

- Make user-visible state distinct from execution authority.
- Keep approval and escalation boundaries explicit.
- Show evidence and source lineage where the underlying contract supplies them.
- Document cancellation, recovery, and unavailable states per system.
- Preserve platform-specific interaction behavior in the owning system entry.
