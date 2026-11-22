# Architecture Governance and Versioning Flow

**Status:** canonical  
**Owner/lane:** Repository Architecture / ICM  
**Canonical for:** architecture versioning, manifest generation, and diagram refresh lifecycle  
**Related contracts:** [Architecture Versioning](../VERSIONING.md), [Architecture Entry](../../../architecture.md), [Automation Documentation Continuous Refresh](../../../.github/workflows/automation-docs-continuous-refresh.yml)

## Purpose

This module connects semantic architecture changes to versioned source history and deterministic generated projections. It extends the existing Mermaid and documentation automation rather than creating a second scheduler or source-of-truth system.

## Flow

1. A contributor changes an authoritative architecture document or editable Mermaid source.
2. The contributor classifies the semantic impact and updates docs/architecture/VERSION plus CHANGELOG.md in the same pull request.
3. Pull-request validation compares the branch with its base, runs focused unit tests, renders the architecture flow diagrams to SVG, renders operational diagrams to PNG, and generates the manifest.
4. The manifest binds the architecture version to ordered source paths, per-file SHA-256 values, a source-set digest, and diagram render digests.
5. The pull request receives generated evidence for review. The validation job remains read-only.
6. The trusted master refresh regenerates the same projections after merge and commits only changed generated assets.
7. The operator loop waits for completion, watches the run, re-fetches the master head, and compares the resulting manifest and diagram fingerprints with the merged sources.

## Authority boundaries

- Canonical architecture documents and Mermaid sources own meaning.
- VERSION and CHANGELOG.md own release identity and change history.
- The Python generator owns the JSON manifest.
- Mermaid CLI owns rendered SVG and PNG projections.
- Git history and Actions run/artifact metadata own execution provenance.
- Generated projections never replace their sources.

## Verification

The focused contract tests cover deterministic output, source coverage, missing renders, stale-manifest detection, semantic-version validation, required version bumps, and changelog entries.

The workflow is event-driven through the existing Automation Documentation Continuous Refresh lane. It adds no independent timer or external service.
