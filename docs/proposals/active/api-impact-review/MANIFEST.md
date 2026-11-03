---
id: api-impact-review
title: "API Impact Review — SHA-bound API evolution intelligence for pull requests"
author: ChatGPT
posted_at: 2026-11-02
source: "Repository evidence: llm_api_hub, hub_mcp, tests, and Integration Intelligence design"
status: accepted
priority: P0
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
related_prs: []
related_branches:
  - feat/api-impact-review-lane
gates_required: [proposal-lifecycle, repo-gate, termux-smoke]
---

# MANIFEST — api-impact-review

## Summary

Add a read-only, evidence-backed API evolution review lane. It detects configured API surface changes, consumes structured API Impact Mapper outputs, validates evidence and SHA identity, and publishes a deterministic PR artifact. The connected mapper remains an assistant-session capability; CI does not invent or assume a provider endpoint.

## Design

See [API Impact Review design](../../../superpowers/specs/2026-11-02-api-impact-review-design.md) and [implementation plan](../../../superpowers/plans/2026-11-02-api-impact-review.md).

## Review log

### 2026-11-02 — timerloggedout-spec

- Disposition: accepted
- Notes: Operator directive "Do EVERYTHING" authorizes implementation of the advisory, read-only lane. Promotion to a blocking required check remains a separate decision.

## Checklist

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [x] Implementation plan created
- [ ] Fresh non-author review recorded
- [ ] Repo-gate and Termux smoke green on the same PR head
- [ ] PR cites `Implements: APIII-001`
- [ ] Promote only after review and evidence thresholds are met

## Links

- ITEMS: ./ITEMS.md
- Design: ../../../superpowers/specs/2026-11-02-api-impact-review-design.md
- Plan: ../../../superpowers/plans/2026-11-02-api-impact-review.md
