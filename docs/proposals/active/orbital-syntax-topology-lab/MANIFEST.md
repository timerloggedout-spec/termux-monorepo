---
id: orbital-syntax-topology-lab
title: "Orbital Syntax — radial information topology and rapid-scan interface research"
author: ChatGPT
posted_at: 2026-11-01
source: source.md
status: posted
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
related_issues: []
related_prs: []
related_branches:
  - feat/orbital-syntax-topology-lab
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — orbital-syntax-topology-lab

## Summary

Develop an independent, dependency-free proof of concept for concentric-ring and polar hierarchy layouts inspired by the supplied "Orbital Syntax" concept. The work treats radial organization as an optional information architecture for hierarchical data, not as an established speed-reading technique. It is deliberately parallel to the existing SHE dashboard, context-relationship graph, and ArchWiz Markov trellis work.

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| timerloggedout-spec | operator-authorizer | requested | 2026-11-01 | Review scope, naming, and integration boundary |
| ChatGPT | author+executor | posted | 2026-11-01 | Initial research/specification and isolated SVG prototype |

## Review log

### 2026-11-01 — ChatGPT

- Disposition: posted
- Notes: Added a bounded research proposal and isolated browser-native SVG prototype. No SHE integration, telemetry schema, or production claim is made.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [ ] At least one non-author review recorded
- [ ] Status → accepted before execution merges
- [ ] PRs cite `Implements: <ITEM-ID>`
- [ ] Gates green on merge
- [ ] Closed + moved to `closed/` when terminal

## Links

- ITEMS: ./ITEMS.md
- Source: ./source.md
- Prototype: ../../../../apps/orbital-syntax-lab/
- Design contract: ../../../../docs/ops/ORBITAL-SYNTAX-LAYOUTS.md
