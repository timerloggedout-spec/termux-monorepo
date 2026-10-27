---
id: doe-live-method-competition
title: "DOE/MVT live method-competition framework — repo-wide, sandbox-free"
author: timerloggedout-spec
posted_at: 2026-10-27
source: docs/proposals/active/doe-live-method-competition/PROPOSAL.md; Issue #1573; Issues #1595/#1596
status: posted
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
related_issues: [1573, 1595, 1596]
related_prs: [1848]
related_branches: [doe-live-method-competition]
gates_required: [proposal-lifecycle]
---

# MANIFEST — doe-live-method-competition

## Summary

Registry entry and lifecycle metadata for the DOE/MVT live method-competition framework proposal. The source PROPOSAL.md defines the live-mode substitution map, unit-of-observation discipline, fair-competition rules, coverage ledger, experiment contract record shape, and the 8-phase implementation sequence with two pilot proposals.

## Scope

- Docs-only proposal: no workflow, secret, provider, or deployed service is modified.
- Prerequisites are the derived quota census (#1595, run-budget ledger) and the cadence reconciliation fan (#1596, assignment-integrity gate); both remain open.
- Promotion authority is unchanged: existing gates, drift guard, and human merge remain binding on any experiment outcome.

