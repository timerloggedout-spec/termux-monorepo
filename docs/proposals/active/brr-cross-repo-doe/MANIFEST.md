---
id: brr-cross-repo-doe
title: "BRR Cross-Repository DoE — branch, commit, regression, and graph relevance"
author: ChatGPT
posted_at: 2026-11-23
source: "Operator directive: implement a separate cross-repository BRR experiment lane named brr-cross-repo-doe."
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
  - id: ChatGPT
    role: author-executor
    status: executing
related_issues: [5552, 5640]
related_prs: [5630]
related_branches:
  - feat/brr-cross-repo-doe-20261123
gates_required: [proposal-lifecycle, repo-gate, termux-smoke]
---

# MANIFEST — brr-cross-repo-doe

## Summary

Establish a separate Design of Experiments campaign that measures cross-repository discovery quality using the existing Branch Reconciliation Registry (BRR), commit exports, BRR regression feature map, and context/comment graph. The campaign compares retrieval strategies against a frozen, adjudicated task set and records reproducible, source-attributed observations.

## Operator authorization

Operator directive received 2026-11-23: "Implement." This authorizes the bounded campaign, evaluator, tests, and registration in this proposal. The existing BRR v2 private-store export remains an external runtime dependency; this work does not claim access to that data or a completed live run.

## Existing substrates and ownership

- BRR v2 registry/store and delta cycles remain owned by the existing BRR machinery.
- QUE #5552 owns the differential regression check suite and feature-progress map.
- QUE #5640 owns the BRR + commits + regression + comment/context graph join.
- The context-relationship graph and cross-plane graph remain the relationship evidence sources.
- The DoE family owns this campaign's preregistered design, evaluator, experiment records, and analysis.
- The existing QDesk/QUE scheduler, task plane, and promotion authorities remain unchanged.

## Scope

- Add a distinct campaign at `experiments/doe/brr-cross-repo-doe/`.
- Compare lexical baseline, BRR ancestry, context graph, and fused-evidence retrieval.
- Evaluate only frozen, explicitly supplied source snapshots and adjudicated target sets.
- Preserve repository-qualified branch identity, commit SHA, PR/issue identity, regression verdict, graph-edge confidence, source SHA, and coverage.
- Emit records conforming to `docs/ops/corpus/EXPERIMENT.schema.json`.

## Boundaries

- BRR remains a read-only observer with its existing schema and authority boundaries.
- Reuse existing collectors, exports, regression suite, graph stores, event paths, scheduler, and queue.
- Add no second scheduler, queue, branch collector, graph store, dashboard, or promotion engine.
- Do not use lexical similarity or candidate edges as verified evidence.
- Treat private-store absence, partial pagination, missing refs, and untestable regressions as explicit unknown/blocked states.
- Runtime execution and promotion require exact source receipts, a frozen gold set, valid run records, and existing repository gates.

## Runtime dependency

The VM-published BRR v2 registry export and joined commit/regression/comment-graph records are required for live cross-repository execution. GitHub issue #5552 records that the 2026-11-17 private registry export is not accessible through this session and that a full cycle plus consumer read remain outstanding. Until the export and execution receipt are supplied by the existing machinery, campaign state remains `admitted_design_only`.

## Review and promotion

This campaign is observational and decision-support only. It cannot merge, push, close, retarget, delete, archive, or promote branches. Any adoption of a retrieval strategy remains a separately reviewed change under the existing proposal lifecycle and dual gates.

## Checklist

- [x] Proposal registered and work item itemized
- [x] Operator directive recorded
- [ ] Independent review recorded
- [ ] Offline evaluator tests pass on the exact PR head
- [ ] Canonical EXPERIMENT schema validation passes
- [ ] repo-gate and termux-smoke pass on the same immutable head SHA
- [ ] Live cross-repository input export and runtime receipt observed
- [ ] At least one named consumer read recorded before live campaign completion
