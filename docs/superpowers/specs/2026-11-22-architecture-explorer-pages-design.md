# Architecture Explorer Pages — Design

**Date:** 2026-11-22  
**Status:** implementation design  
**Target:** `https://timerloggedout-spec.github.io/termux-monorepo/architecture/`

## Intent

Publish a browsable, read-only architecture portal that joins canonical architecture Markdown, editable Mermaid sources, imported SVG assets, and generated diagram outputs. The portal serves engineers, agents, and reviewers who need to navigate the repository's architecture and inspect both the visual artifact and its editable source.

## Goals

- Automatically refresh the portal when architecture source, diagram, SVG, or relevant generated assets change.
- Preserve source ownership and direct GitHub links.
- Provide nested navigation, search, Markdown reading, diagram inspection, and provenance.
- Reuse the existing project Pages publisher and Mermaid CLI version.
- Keep GitHub Actions and repository files authoritative.

## Non-goals

- A diagram authoring/editor surface.
- A second dashboard database or runtime control plane.
- A live API, authentication system, or browser-side repository mutation.
- A replacement for the existing Mermaid/PNG automation.
- A separate hosting project or new paid dependency.

## Approaches

1. **Add a route to the existing project Pages hub (chosen).** Place the UI under `apps/project-pages-hub/architecture/`, extend the existing publisher, and build a source-derived static bundle. This preserves the current `gh-pages` contract and creates a clean nested route.
2. Create a separate Pages site/repository. This adds a second publisher and site identity for content that already belongs to the project hub.
3. Embed the explorer inside the Tribute dashboard. This couples architecture navigation to the operations product and conflicts with the existing site-role separation.

## Architecture

- Canonical inputs: root `architecture.md`, `docs/architecture/**`, `docs/ops/diagrams/**`, selected SHE architecture documents, and generated diagram assets.
- Build: a standard-library Python inventory builder copies source files, emits a JSON catalog with SHA-256 and source identity, and maps every Mermaid source to a generated SVG output path.
- Render: the existing Pages workflow runs pinned Mermaid CLI to generate SVGs into the static artifact.
- UI: static HTML/CSS/JavaScript with nested expandable navigation, global search, Markdown rendering, diagram viewer controls, and source/provenance panels.
- Publish: existing `tribute-dashboard-deploy.yml` publishes the built route into the current `gh-pages` artifact.

## Constraints and security

- The browser is read-only and contains no credentials.
- Markdown HTML is sanitized before insertion.
- Repository-relative paths are validated before copying.
- Imported SVG is served as an image asset; the UI does not inline untrusted SVG markup.
- Every catalog item carries a canonical GitHub URL, source path, kind, byte count, and SHA-256.
- Build identity uses the actual GitHub source SHA/ref and actual build timestamp.
- Mermaid output is generated at publication time; source files remain canonical.

## UX defaults

- Dark, high-contrast layout consistent with the project hub's existing visual language.
- Desktop: persistent expandable tree, central reader/viewer, provenance rail.
- Mobile: collapsible navigation drawer and full-width reader/viewer.
- Search spans title, path, summary, and category.
- Diagram controls: zoom, pan, fit, fullscreen, rendered SVG, Mermaid source, and original imported SVG where applicable.
- Markdown documents render in the reader with links resolving to canonical GitHub source paths.

## Acceptance

See `docs/proposals/active/architecture-explorer-pages/ITEMS.md`, especially ARCH-EXP-002 through ARCH-EXP-006.
