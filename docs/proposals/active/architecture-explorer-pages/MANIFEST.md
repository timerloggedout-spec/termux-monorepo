# Architecture Explorer Pages — Proposal Manifest

**ID:** architecture-explorer-pages  
**Status:** executing  
**Priority:** P1  
**Owner:** ChatGPT — documentation and static-site implementation  
**Operator authorization:** accepted for the bounded GitHub Pages architecture portal  
**Implementation branch:** `feat/architecture-explorer-pages-20261122`

## Objective

Publish a read-only architecture explorer at `/termux-monorepo/architecture/` that automatically indexes canonical architecture Markdown, Mermaid sources, imported SVG assets, and generated SVG diagrams.

## Scope

- Add a nested architecture explorer page to the existing project Pages hub.
- Inventory `architecture.md`, `docs/architecture/**`, `docs/ops/diagrams/**`, selected SHE architecture contracts, and generated diagram assets.
- Preserve source paths, source links, hashes, source SHA, and build timestamp.
- Render Mermaid sources to SVG during the existing Pages publication workflow.
- Import standalone SVG and PNG assets into the static site.
- Provide expandable navigation, search, Markdown reading, diagram zoom/pan/fullscreen, source inspection, and provenance.
- Extend Pages path filters, deployment verification, site map, and operator skill.

## Authority and boundaries

- Git-tracked Markdown, Mermaid, and SVG files remain canonical sources.
- Generated SVG/PNG files are presentation artifacts.
- GitHub Actions remains the publisher; the browser remains read-only.
- The explorer does not become a dashboard database, workflow editor, or execution surface.
- Publication remains under the existing `gh-pages` project-hub route.

## Acceptance

- [ ] Static page publishes at `https://timerloggedout-spec.github.io/termux-monorepo/architecture/`.
- [ ] Inventory includes the root architecture entry, six modular flow pairs, SHE architecture sources, and discovered SVG assets.
- [ ] Mermaid sources render to SVG during publication and preserve a direct source link.
- [ ] Imported SVGs retain their repository path and SHA-256.
- [ ] Navigation expands by category and nested path.
- [ ] Search filters documents and diagrams by title/path/category.
- [ ] Markdown reader links back to canonical GitHub sources.
- [ ] Diagram viewer supports zoom, pan, fit, fullscreen, and source inspection.
- [ ] Page exposes source SHA, build timestamp, and item hashes.
- [ ] Agent-readability and static-site tests pass.
- [ ] Repository dual gates and Pages publication are verified on the same source SHA.

## Evidence

- Existing Pages publisher: `.github/workflows/tribute-dashboard-deploy.yml`.
- Existing Mermaid source/render pipeline: `automation-docs-continuous-refresh.yml` + `scripts/ci/automation_docs.py`.
- Existing architecture entry: `architecture.md`.
- Existing modular maps: `docs/architecture/flows/`.
- Existing architecture/SHE navigation contracts: `docs/ops/SHE-DASHBOARD-INDEX.md` and `docs/ops/SHE-DASHBOARD-UI-UX-CONTROL-PLANE.md`.

## Review log

| Date | Actor | Event | Evidence / disposition |
|---|---|---|---|
| 2026-11-22 | ChatGPT | Operator request accepted; isolated branch created from master | `feat/architecture-explorer-pages-20261122` |

