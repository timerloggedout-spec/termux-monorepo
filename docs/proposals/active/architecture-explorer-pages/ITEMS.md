# Architecture Explorer Pages — Work Items

**Proposal:** architecture-explorer-pages  
**Scope:** GitHub Pages static architecture portal, source inventory, SVG rendering, navigation, and provenance.

| ID | Work item | Acceptance evidence | State |
|---|---|---|---|
| ARCH-EXP-001 | Add proposal/design/plan and register the bounded publication scope. | Registry validator confirms manifest + ITEMS path and unique ID. | Implemented |
| ARCH-EXP-002 | Build a deterministic architecture source inventory and static asset bundle. | Unit tests cover Markdown, Mermaid, SVG, PNG, safe paths, and rendered-output verification. | In progress |
| ARCH-EXP-003 | Implement the nested architecture explorer UI and project-hub navigation. | Readability checks, keyboard/accessibility checks, source/provenance links, and static browser contract. | Pending |
| ARCH-EXP-004 | Extend the existing Pages publisher to build and publish the architecture route. | Workflow path filters, Mermaid-to-SVG generation, bundle verification, and source SHA receipt. | Pending |
| ARCH-EXP-005 | Reconcile site map, deployment lane, and operator documentation. | All navigation and deployment contracts identify the architecture route and source ownership. | Pending |
| ARCH-EXP-006 | Run focused tests, repository gates, inspect Pages deployment, and re-fetch the published SHA. | Current-head tests + repo gate + Termux smoke + deployment artifact/URL/source SHA evidence. | Pending |

## Review log

| Date | Actor | Event | Evidence / disposition |
|---|---|---|---|
| 2026-11-22 | ChatGPT | Scope registered on isolated branch | `feat/architecture-explorer-pages-20261122` |
