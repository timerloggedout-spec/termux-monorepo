---
id: approxination-integration
title: "Approxination skill search/create/contribute + A/B/C/D evaluation cohort"
author: grok
posted_at: 2026-09-23
source: operator-maintained proposal
status: executing
priority: P1
reviewers:
  - id: grok
    role: author+executor
    status: executing
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
related_prs: [614]
related_branches:
  - feat/approxination-integration
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — Approxination Integration

## Summary

Integrate Approxination skill search, creation, contribution, and A/B/C/D tool-layer evaluation as an AEF reference treatment. This is a reference/adaptation lane, not a wholesale source merge.

## Boundary

- no paid API spend in CI;
- no automatic external deployment;
- external skills/resources remain learning templates until locally adapted and validated.

## Evidence

See README.md and ITEMS.md. Keep the proposal registry entry and manifest synchronized.
