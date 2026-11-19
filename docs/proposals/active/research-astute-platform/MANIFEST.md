---
id: research-astute-platform
title: "Research Astute — multi-experiment research platform and shared interactive graph surface"
author: ChatGPT
posted_at: 2026-11-19
source: source.md
status: in_review
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
related_prs: [5649]
related_branches:
  - research/research-astute-preliminary
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — research-astute-platform

## Summary

Establish a shared research platform for many independent, continuously evolving thought experiments. Define common experiment, source, evidence, typed-graph, alternate-path, snapshot, and run contracts; adapt the computational-limits seed as the first experiment; specify one interactive visualization UX for selecting, overlaying, and comparing alternate paths; and validate project references through the existing research CI surface.

## Reviewers

| ID | Role | Status | At | Notes |
|---|---|---|---|---|
| timerloggedout-spec | operator-authorizer | requested | 2026-11-19 | platform scope and promotion |

## Review log

### 2026-11-19 — implementation seed

- Disposition: in_review
- Notes: initial platform contracts and first experiment package committed on the linked branch; validation evidence and standalone repository provisioning remain in progress.

## Checklist

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [ ] At least one non-author review recorded
- [ ] Status accepted before integration promotion
- [x] PR cites implementation item IDs
- [ ] repo-gate and termux-smoke green on final head
- [ ] Closed and moved to `closed/` when terminal

## Links

- ITEMS: ./ITEMS.md
- Source: ./source.md
- Platform: `research/astute-platform/`
- First experiment: `research/astute-computational-limits/`
