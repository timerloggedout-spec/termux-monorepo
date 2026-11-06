---
id: repository-intelligence-data-plane
title: "Repository Intelligence & Collaboration Data Plane (RIDP)"
author: ChatGPT
posted_at: 2026-11-05
source: source.md
status: posted
priority: P0
reviewers:
  - timerloggedout-spec
related_prs:
  - 2473
related_branches:
  - feat/ridp-repository-intelligence-data-plane
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — repository-intelligence-data-plane

## Summary

Establish a repository-native, incremental intelligence data plane that reduces redundant GitHub API acquisition and repeated agent context ingestion while preserving immutable evidence, authorization boundaries, freshness, provenance, quota governance and safe ref-scoped collaboration. RIDP integrates with the existing Agentic Collaboration conductor, Context Relationship Graph, SHE/ATES, rate-limit helpers and domain-owned projections; it does not replace them.

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| timerloggedout-spec | operator-authorizer | requested | | P0 architecture review and phase admission |

## Review log

No independent review recorded yet. Proposal remains posted; implementation phases require item-scoped acceptance under the repository proposal process.

## Checklist (process)

- [x] Registered in docs/proposals/registry.yaml
- [x] ITEMS.md itemized
- [ ] At least one non-author review recorded
- [ ] Status → accepted before execution merges
- [ ] PRs cite Implements: RIDP-XX
- [ ] Gates green on merge
- [ ] Closed + moved to closed/ when terminal

## Related implementation

- QAC-009 tick ledger implementation: PR #2473 (merged; source of per-request quota evidence).

## Links

- Architecture: ../../../architecture/REPOSITORY-INTELLIGENCE-DATA-PLANE.md
- ITEMS: ./ITEMS.md
- Source: ./source.md
