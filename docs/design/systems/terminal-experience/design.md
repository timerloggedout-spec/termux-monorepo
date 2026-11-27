# Terminal Experience — Design

> **Evidence status:** in progress  
> **Design owner:** Ratatui + Tokio dashboard proposal and terminal maintainers  
> **Canonical implementation:** proposal and implementation paths linked below  
> **Last source review:** 2026-11-23

## 1. Purpose and users

A Termux-first responsive terminal dashboard. The registered proposal specifies a system/process monitor, asynchronous event producers, bounded channels, model/render separation, dirty-frame coalescing, graceful metric fallback, and clean terminal lifecycle.

## 2. Experience surfaces

| Surface | Audience | Evidence status | Owning source |
|---|---|---|---|
| Ratatui terminal dashboard | Termux operators | Executing proposal | [Proposal items](../../../proposals/active/ratatui-tokio-terminal-dashboard/ITEMS.md) |
| Runtime / build guidance | Developers and operators | Proposal item | [Proposal manifest](../../../proposals/active/ratatui-tokio-terminal-dashboard/MANIFEST.md) |

## 3. Information architecture

The proposal identifies process/system metrics, stream latency/throughput, and thread-pool/process views as intended panels. Exact navigation and panel hierarchy remain implementation decisions to verify against current source.

## 4. Journeys and interactions

The proposal requires an asynchronous event/state model, bounded channels, dirty-frame rendering, graceful metric fallback, and clean terminal lifecycle. Key interaction details such as key bindings, focus, selection, and drill-down remain open until sourced from implementation.

## 5. Visual language

Terminal layout must account for constrained dimensions and responsive rendering. Specific breakpoints, compact modes, colors, and glyph choices require source verification.

## 6. Accessibility

Document keyboard navigation, focus, contrast, and terminal-reader compatibility from implementation and tests. The current proposal provides the runtime model, not a completed accessibility audit.

## 7. Evidence and system states

The proposal explicitly requires graceful fallback when metric sources are unavailable. Record metric-source unavailable states separately from zero values and preserve clean terminal exit behavior.

## 8. Decisions and open gaps

- Verify current panel implementation against proposal items.
- Record key bindings and focus model.
- Define minimum terminal dimensions and narrow-layout behavior from code/tests.
- Verify fallback and shutdown behavior.

## 9. Canonical sources

- [Proposal items](../../../proposals/active/ratatui-tokio-terminal-dashboard/ITEMS.md)
- [Proposal manifest](../../../proposals/active/ratatui-tokio-terminal-dashboard/MANIFEST.md)
- [ArchWiz UI protocol](../../../proposals/active/archwiz-ui-protocol/ITEMS.md)
