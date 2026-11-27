---
id: coralogix-foss-observability-reconstruction
title: "Coralogix capability reconstruction with FOSS observability and agent-evaluation comparators"
author: ChatGPT
posted_at: 2026-11-27
source: README.md
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
  - id: ChatGPT
    role: author-executor
    status: executing
related_issues: [7]
related_prs: []
related_branches:
  - timerloggedout/ter-7-p1-expand-reftemplates-with-foss
gates_required: [repo-gate, termux-smoke, siglary-mandate]
---

# MANIFEST — coralogix-foss-observability-reconstruction

## Summary

Compare Coralogix and FOSS observability/evaluation systems, extract capabilities from My-Jogyo and Docxology, and implement repository-owned adapters over the existing evidence substrate. The current tranche registers source references, reconciles the research-template index, records ForeSight candidates, and defines the architecture and experiment plan.

## Reviewers

| ID | Role | Status | At | Notes |
|---|---|---|---|---|
| timerloggedout-spec | operator-authorizer | accepted | 2026-11-27 | Explicit operator direction to implement recommendations and deliver the high-detail proposal. |
| ChatGPT | author-executor | executing | 2026-11-27 | Metadata, proposal, and registry implementation on the TER-7 branch. |

## Review log

### 2026-11-27 — timerloggedout-spec

- Disposition: accepted
- Notes: Operator authorized implementation, high-detail proposal delivery, and commit/push. TER-7 scope expanded to include the FOSS observability and research-comparator work.

### 2026-11-27 — ChatGPT

- Disposition: commented
- Notes: Candidate references and ForeSight records prepared. Existing schemas, telemetry ingestion, and otel-core catalog entry mapped as the implementation foundation. Staging gates pending.

## Checklist (process)

- [x] Registered in docs/proposals/registry.yaml
- [x] ITEMS.md itemized
- [x] Operator review recorded
- [x] Status accepted before execution merges
- [x] PR cites Implements: TER-7 and proposal item IDs
- [ ] repo-gate, termux-smoke, and Siglary checks green on merge
- [ ] Closed and moved to closed/ when terminal

## Links

- ITEMS: ./ITEMS.md
- Source: ./README.md
- Linear: https://linear.app/termux-monorepo-linear/issue/TER-7/p1-expand-reftemplates-with-foss-observability-and-research
- Branch: timerloggedout/ter-7-p1-expand-reftemplates-with-foss
