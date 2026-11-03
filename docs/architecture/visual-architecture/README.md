# Visual Architecture & Versioning Standard

**Status:** Proposed repository standard  
**Scope:** Integration Intelligence Cockpit and related architecture diagrams  
**Owner:** termux-monorepo maintainers  
**Last updated:** 2026-11-02

## 1. Purpose

Maintain one coherent visual architecture project with multiple focused pages, explicit revision history, and reproducible milestone archives. Diagrams are maintained views of the system; they are not substitutes for executable specifications, source code, tests, or operational evidence.

## 2. Information architecture

Use one master board/workspace with the following canonical pages:

| Order | Page | Responsibility |
|---|---|---|
| 00 | Executive Overview | System map, boundaries, critical flows, maturity summary |
| 01 | Integration Registry | Providers, capabilities, ownership, lifecycle and evidence |
| 02 | Adapter Architecture | Adapter contracts, normalization, orchestration and failure handling |
| 03 | API Impact Intelligence | API change detection, extraction, classification and consumer impact |
| 04 | Evidence & Provenance | Schemas, source references, lineage, validation and retention |
| 05 | Intelligence Systems | Relationships among internal intelligence systems and data layers |
| 06 | Research & Experimental Lanes | Isolated experiments, connector availability and promotion criteria |
| 07 | Security & Governance | Trust boundaries, privacy, permissions, approvals and release controls |
| 08 | Evolution Roadmap | Milestones, dependencies, acceptance criteria and delivery state |

A page represents a stable subject area. Do not create a new page for every edit or version.

## 3. Revision model

Use three levels:

1. **Page revision:** ordinary refinement of the same subject. Record meaningful changes in the page's revision notes.
2. **Milestone snapshot:** immutable capture at a meaningful design or delivery checkpoint.
3. **Architecture release:** a reviewed collection of page snapshots that together describe a coherent system state.

Suggested version syntax:

- `v0.x`: exploratory and pre-release revisions.
- `v1.0`: first reviewed baseline.
- `v1.x`: backward-compatible refinements to the architecture.
- `v2.0`: material change to boundaries, contracts, or information architecture.

Version numbers are assigned only when a snapshot is actually created. Proposed versions must not be presented as existing artifacts.

## 4. Export and archive contract

For every approved milestone, preserve the following where supported:

| Artifact | Purpose | Required metadata |
|---|---|---|
| SVG | Scalable diagram for docs and design tools | Page, version, export date, source board |
| PNG | Quick preview and presentation | Page, version, export date |
| JSON snapshot | Recoverable editable source state | Page/board identity, version, source revision |
| Manifest | Integrity and provenance | SHA-256, source commit, export tool/version, included pages |
| Change note | Human-readable revision history | Summary, rationale, review status, known limitations |

A selected-shape export is a reusable component, not a full-page backup. A JSON snapshot should be treated as the editable recovery artifact. SVG/PNG alone do not preserve the full editing model.

### Archive layout

```text
docs/architecture/visuals/
  integration-intelligence/
    README.md
    manifest.schema.json
    releases/
      v0.1/
        manifest.json
        CHANGELOG.md
        executive-overview.svg
        executive-overview.png
        board.snapshot.json
      v1.0/
        ...
```

Do not check in generated exports until the export has been verified, metadata is complete, and repository size/licensing constraints have been checked. Large binary archives may be better stored as GitHub Release assets or an approved artifact store, with their checksums and references committed to Git.

## 5. Provenance and traceability

Each visual element that asserts implementation status should be traceable to evidence. At minimum, capture:

- repository and branch;
- source commit SHA;
- related PR or issue;
- implementation state: `proposed`, `in_progress`, `implemented`, `validated`, or `deprecated`;
- evidence link(s), such as tests, docs, schema, workflow or runtime result;
- last verified date.

Use distinct visual notation for:
- implemented and verified;
- implemented but not yet verified;
- proposed design;
- external dependency;
- unknown or disputed relationship.

Never draw a proposed integration as an operational connection. Never infer production status from a connector being available.

## 6. Change and review workflow

1. Edit the canonical page for the affected subject.
2. Update the revision note and affected relationships in the overview.
3. Check terminology and status against repository evidence.
4. Review security boundaries, data flow and ownership implications.
5. Export the milestone artifacts and compute checksums.
6. Validate the manifest and links.
7. Commit source documentation and small artifacts, or publish large artifacts as a release.
8. Link the commit/PR and release back from the page's revision notes.

A material architectural change requires review by the relevant maintainers. A diagram-only change must not imply that the underlying implementation has shipped.

## 7. Export implementation boundary

The tldraw editor API exposes page and shape inspection, SVG generation, image generation, content export and editor snapshots. These capabilities establish a feasible export path. They do not by themselves establish that this repository has a working automated exporter.

Automation should be introduced only after a reproducible export can be run against a known board, with deterministic naming, error handling, integrity checks and a verified archive destination. Until then, record exports as manual and verified individually.

## 8. Acceptance criteria

- [ ] The master board contains the nine canonical pages.
- [ ] Each page has a concise purpose statement and revision note.
- [ ] Executive overview links/points to all subject pages.
- [ ] Implemented, proposed, unknown and deprecated states are visually distinct.
- [ ] Every approved milestone has a manifest and change note.
- [ ] SVG and PNG exports render correctly.
- [ ] JSON snapshot can be restored or inspected successfully.
- [ ] Checksums match archived files.
- [ ] Source commit and related PR/issue are recorded.
- [ ] No export or version is described as complete without verification.

## 9. Current execution status

This document establishes the repository-side standard only. It does not claim that the tldraw board has been reorganized, that any export has been generated, or that an automated export pipeline exists. Those actions remain pending until the live board can be inspected and the outputs verified.
