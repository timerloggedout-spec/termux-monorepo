---
id: que-sie-pipeline-integration
title: "QUE SIE research, RFP, Delphi, DoE and implementation claim integration"
author: ChatGPT
posted_at: 2026-11-13
source: "QUE task #5389; qdesk-self-repair; QUE #5283/#5286; QDesk RFP #5145"
status: in_review
priority: P0
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
  - id: ChatGPT
    role: author+executor
    status: executing
related_issues: [5389, 5283, 5286, 5113, 5116, 5156]
related_prs: [5145, 5371, 5372, 5330]
related_branches: [feat/que-sie-pipeline-integration, feat/workflow-planning-operating-model]
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — que-sie-pipeline-integration

## Summary

Connect existing QUE ranking, claim, lease, watchdog and SIE learning machinery to a durable improvement lifecycle: observe → triage → research → RFP → Delphi → DoE design → claim → implement → independently verify → promote → learn.

## Source-of-truth boundaries

- QUE owns admission, ranking, claims, leases and dispatch-state feeds.
- SIE owns the improvement loop and its existing role/failure-class learning weights.
- Oracle Method generates research-backed proposal packages.
- Delphi owns independent RFP review, ballots, awards and signed ledgers.
- DoE owns design records, treatment identity, experiment runs and evaluation.
- ATES owns execution outcome evaluation; repository dual gates own promotion evidence.
- CEEL owns capability discovery and opportunity mapping.
- Observatory surfaces project existing canonical feeds and ledgers.
- Siglary owns notation governance; PDDL is a formal-planning subdomain within Siglary.
- Existing Kahn DAG, dependency-phase engine, queue ranker, watchdog and auto-claim remain canonical components.

## Review log

### 2026-11-13 — initial proposal and contract implementation

- QUE task #5389 filed with source triggers, stage contract, acceptance criteria and delivery slices.
- Added a deterministic SIE stage model, JSON Schema and regression tests.
- Implementation status: contract slice committed on feature branch; live trigger and Delphi dispatch wiring remain subsequent items.
