# Architecture Governance and Versioning Flow

**Status:** canonical  
**Owner/lane:** Repository Architecture / ICM  
**Canonical for:** architecture versioning, manifest generation, and diagram refresh lifecycle  
**Related contracts:** [Architecture Versioning](../VERSIONING.md), [Architecture Entry](../../../architecture.md), [Automation Documentation Continuous Refresh](../../../.github/workflows/automation-docs-continuous-refresh.yml)

## Purpose

This module connects semantic architecture changes to versioned source history and deterministic generated projections. It reuses the existing Mermaid and documentation automation, preserving one scheduler and one source-of-truth hierarchy.

## Flow

1. **Observe** — Read the current branch/base SHA, canonical architecture sources, version, manifest, and existing diagram fingerprints.
2. **Choose** — Select the bounded source/diagram scope and classify the semantic change as MAJOR, MINOR, or PATCH.
3. **Act** — Update canonical documents and paired Mermaid sources; bump VERSION and add the matching CHANGELOG entry in the same pull request.
4. **Verify** — Run focused tests and the base-diff version gate; render architecture flows to SVG and operational diagrams to PNG; generate and check the deterministic manifest.
5. **Record** — Preserve the commit SHA, architecture version, source-set digest, workflow run, artifact identity, outcome, and remaining work in Git and Actions evidence.
6. **Repeat or stop** — Re-read fresh state only when new feedback can change the next action. Stop with success, unchanged, blocked, approval-required, exhausted, or stagnated as appropriate.

The pull-request job remains read-only and uploads generated review evidence. After merge, the trusted master refresh commits changed generated projections. The next cycle observes the resulting master head and confirms the manifest and renders match the merged sources.

## Authority boundaries

- Canonical architecture documents and Mermaid sources own meaning.
- VERSION and CHANGELOG.md own release identity and change history.
- The Python generator owns the JSON manifest.
- Mermaid CLI owns rendered SVG and PNG projections.
- Git history and Actions run/artifact metadata own execution provenance.
- Canonical sources retain authority; generated projections serve as reviewable outputs.

## Verification

The focused contract tests cover deterministic output, source coverage, missing renders, stale-manifest detection, semantic-version validation, required version bumps, and changelog entries.

The existing Automation Documentation Continuous Refresh workflow remains the single event-driven scheduler and execution surface.
