# Tribute Dashboard — Design

> **Evidence status:** implemented  
> **Design owner:** Tribute Dashboard source and maintainers  
> **Canonical implementation:** `apps/tribute-dashboard/`  
> **Last source review:** 2026-11-23

## 1. Purpose and users

A read-only operational dashboard consuming committed surface feeds. The repository architecture identifies Tribute as a consumer of surface feeds, not an authoritative operational store.

## 2. Experience surfaces

| Surface | Audience | Evidence status | Owning source |
|---|---|---|---|
| Web dashboard | Repository operators / maintainers | Implemented | [README](../../../../apps/tribute-dashboard/README.md) |
| Shared dashboard styling | Dashboard views | Implemented | [dashboard.css](../../../../apps/tribute-dashboard/dashboard.css) |
| Data-fed panels | Dashboard readers | Implemented | [data directory](../../../../apps/tribute-dashboard/data/) |

## 3. Information architecture

The dashboard README is the entry point for page structure and usage. The design map records its navigation and page groups by reference; implementation remains the source of exact routes and grouping.

## 4. Journeys and interactions

The architecture establishes a read-only consumer role. Mutating operational state belongs to upstream systems and their authority boundaries.

## 5. Visual language

The shared stylesheet is the implementation source for current dashboard visual rules. Shared visual guidance is indexed in [visual-language](../../_shared/visual-language.md). Record token values from CSS rather than duplicating them here.

## 6. Accessibility

Use [shared accessibility guidance](../../_shared/accessibility.md) and [SHE UI/UX accessibility contract](../../../ops/SHE-DASHBOARD-UI-UX-CONTROL-PLANE.md). Surface-specific compliance evidence remains to be audited.

## 7. Evidence and system states

Dashboard chart behavior is governed by the [chart standard](../../../ops/DASHBOARD-CHART-STANDARD.md). Feed freshness and partial-data presentation must follow the feed contract; this entry does not infer unavailable-state behavior beyond those sources.

## 8. Decisions and open gaps

- Confirm exact navigation/page grouping from the current README and implementation.
- Audit keyboard/focus and screen-reader behavior.
- Inventory each feed's freshness and partial-data contract.
- Identify shared components beyond the stylesheet.

## 9. Canonical sources

- [Dashboard README](../../../../apps/tribute-dashboard/README.md)
- [Shared stylesheet](../../../../apps/tribute-dashboard/dashboard.css)
- [Repository architecture](../../../../architecture.md)
- [Chart standard](../../../ops/DASHBOARD-CHART-STANDARD.md)
- [Surface map](../../../ops/SURFACES-MAP.md)
