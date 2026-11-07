---
id: tak-common-operating-picture
title: "T.A.K. — Taktikal Awareness Kit common operating picture and actor-network emergence"
author: ChatGPT
posted_at: 2026-11-06
source: source.md
status: accepted
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
related_issues: [4496]
related_prs: [5025]
related_branches: [tak-common-operating-picture-contract-v1]
gates_required: [proposal-lifecycle, repo-gate, termux-smoke]
---

# MANIFEST — T.A.K. Common Operating Picture

## Summary

Establish a repository-native, evidence-backed common operating picture for the registered `tak` lens. T.A.K. consumes pinned, conflict-preserving procurement/registration datasets from the existing upstream ingestion work, projects public organizational entities, relationships, observations, and events, and detects actor-network emergence signals without duplicating crawlers, stores, tracking feeds, telemetry, or dispatch orchestration.

## Scope for this proposal revision

This revision is limited to **TAK-01: the Phase A contract**. It records the machine-readable picture envelope, evidence/provenance requirements, coverage and conflict semantics, unvalenced emergence entry, and composition with the registered SWOT duality doctrine.

It does not authorize a live source connector, crawler, data store, detector model, dashboard binding, procurement action, or autonomous adverse decision. Those require separate itemized evidence and owning-lane alignment.

## Reviewers

| ID | Role | Status | At | Notes |
|---|---|---|---|---|
| timerloggedout-spec | Operator authorizer | accepted | 2026-11-06 | Owner's explicit directive: “Do EVERYTHING” / “Complete” / “Continue” for T.A.K.; acceptance is bounded to TAK-01 Phase A contract only. |
| ChatGPT | Author and executor | executing | 2026-11-06 | Prepared contract PR #5025; no live source integration claimed. |

## Review log

### 2026-11-06 — timerloggedout-spec

- Disposition: accepted (Operator self-accept recorded from the explicit owner directive in this project session).
- Scope: TAK-01 Phase A contract only. This does not authorize live source collection, a detector, external data processing, dashboard binding, or autonomous procurement/adverse action.

### 2026-11-06 — ChatGPT

- Disposition: posted for review.
- Evidence: registered `tak` lens in `docs/ops/LENS-FRAME.md`; trigger in `docs/ops/LENS-TEMPLATE-TRIGGER.md`; upstream repeat-crawl/ingest/change-detection proposal in issue #4496; candidate operational feeds listed in the T.A.K. contract.
- Boundary: Phase A contract only. Proposal remains `in_review`; no acceptance or promotion is self-recorded.

## Checklist

- [x] Registered in `docs/proposals/registry.yaml`.
- [x] TAK-01 itemized in `ITEMS.md`.
- [ ] Non-author review recorded.
- [ ] Proposal accepted before implementation merges.
- [ ] PRs cite `Implements: TAK-01`.
- [ ] Proposal lifecycle, repo-gate, and termux-smoke pass on the current PR head.
- [ ] Later implementation items separately scoped and accepted before execution.

## Links

- [PR #5025](https://github.com/timerloggedout-spec/termux-monorepo/pull/5025)
- [Upstream dataset pipeline issue #4496](https://github.com/timerloggedout-spec/termux-monorepo/issues/4496)
- [ITEMS](./ITEMS.md)
- [Source record](./source.md)
