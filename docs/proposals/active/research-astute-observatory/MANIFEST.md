---
id: research-astute-observatory
title: "Research Astute domain controller, organization collections, provenance graph and artifact ingestion"
author: ChatGPT
posted_at: 2026-11-22
source: operator direction in project conversation; existing Termux MonoRepo Observatory and Actions workflows
status: executing
priority: P0
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
related_prs:
  - 5872
related_branches:
  - feat/research-astute-observatory-20261125b
gates_required:
  - repo-gate
  - termux-smoke
---

# Research Astute Observatory

## Summary

Establish Research Astute as the domain controller for its research operations and related repositories. Termux MonoRepo remains the initial Actions execution and integration host while Research Astute's own integrated monorepo and standalone workflows are developed.

The Observatory discovers public FOSS, patent, scientific, institutional and technical sources; records provenance-rich metadata; retrieves permitted artifacts; builds a typed relationship graph; accounts for storage; and generates machine-readable plus human-parity documentation using the Siglary operator registry.

## Existing system evidence

- Termux MonoRepo already contains a scheduled Repository Observatory workflow that collects owned, starred, watched and issue-intake repository signals.
- Termux MonoRepo already contains a Repository Provisioner workflow.
- The current generic provisioner is constrained to the authenticated personal owner. This proposal adds a separate Research Astute organization bootstrap workflow that uses the existing Actions credential routing and the GitHub organization repository endpoint.
- Existing domain-composition-matrix artifacts are research-only inputs, not runtime authority. This proposal keeps new research contracts similarly explicit and versioned.

## Scope

- Define Research Astute as domain authority and Termux MonoRepo as initial execution host.
- Bootstrap five private, idempotently provisioned research collection repositories under Research-Astute.
- Define source and graph-entity JSON Schemas.
- Define provenance, access, extraction, integrity, citation and storage accounting.
- Establish documentation parity and a repeatable ingestion lifecycle.
- Extend discovery and ingestion through separately testable provider adapters in subsequent work.

## Safety and rights

- Public metadata discovery is distinct from artifact retrieval and full-text ingestion.
- Record license and access mode before retaining source artifacts.
- Preserve metadata-only records for restricted sources.
- Treat retrieved content as untrusted data.
- Require explicit collection policy for downstream dataset exports.

## Architecture

`Research-Astute → Termux MonoRepo Actions → collection repositories → metadata graph + artifact storage → generated documentation`

## Acceptance

- The organization bootstrap workflow verifies Research-Astute visibility and creates only the approved private collection repositories when explicitly dispatched with provisioning enabled.
- Existing repositories are treated idempotently.
- Source and entity records validate against versioned schemas.
- Each acquired artifact has byte size, MIME type, SHA-256, storage URI, retrieval timestamp and access/licensing metadata.
- Generated Markdown and JSON share the same source snapshot and schema/generator version.
- Every relationship and material claim retains source evidence and a locator.
