# Architecture Versioning and Automated Refresh — Design

**Date:** 2026-11-22  
**Status:** accepted for implementation by the current operator instruction  
**Scope:** root architecture entry, related architecture flow maps, semantic versioning, generated documentation evidence

## Context

The repository already has a root architecture entry, paired Markdown/Mermaid flow modules, an operational Mermaid-to-PNG refresh lane, and an Automation Documentation Continuous Refresh workflow. The architecture flow sources under docs/architecture/flows/ are outside the existing operational diagram inventory. The current generated asset catalog also lacks one release identity for the architecture source set.

## Decisions

1. Use stable SemVer in docs/architecture/VERSION, with a matching CHANGELOG.md entry for every semantic source change.
2. Treat architecture.md, architecture Markdown/Mermaid files, operational diagram sources, and the SHE architecture source as manifest inputs.
3. Generate one deterministic JSON manifest containing architecture version, per-file SHA-256 values, source-set digest, and source/render digests.
4. Render architecture flow Mermaid sources to SVG and retain the existing operational Mermaid-to-PNG pipeline.
5. Extend the existing automation workflow and path classifier; keep one event-driven writer and one established master refresh lane.
6. Keep PR validation read-only. Upload generated review evidence; commit generated projections only through the trusted master refresh.
7. Keep timestamps and run identifiers outside the deterministic manifest. GitHub commit/run/artifact metadata supplies execution provenance.

## Version policy

- MAJOR: breaking authority, ownership, boundary, or contract change.
- MINOR: additive plane, subsystem, interface, or material flow.
- PATCH: correction that preserves semantics.

## Acceptance

- [ ] A version gate requires a greater SemVer and matching changelog entry for semantic source changes.
- [ ] Focused tests cover determinism, source coverage, render existence, drift, and version-bump enforcement.
- [ ] The root architecture entry links to the version contract and governance flow.
- [ ] Existing architecture flow index includes the new governance module.
- [ ] Existing documentation automation recognizes architecture sources and generated projections.
- [ ] Existing workflow renders, validates, and refreshes architecture artifacts without adding a scheduler.
- [ ] PR validation evidence and master refresh execution are observed on the exact head SHA.

## Boundaries

Domain contracts retain semantic ownership. Generated files remain projections. BRR remains read-only; branch reconciliation and promotion follow repository governance.
