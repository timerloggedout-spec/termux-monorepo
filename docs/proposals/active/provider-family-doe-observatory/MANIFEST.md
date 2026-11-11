---
id: provider-family-doe-observatory
title: "Provider Family × Configured Instance × DoE settings observatory"
author: ChatGPT
posted_at: 2026-11-11
source: source.md
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
related_issues: [5136]
related_prs: [5145]
related_branches:
  - feat/provider-family-doe-observatory-20261111
gates_required: [proposal-lifecycle, repo-gate, termux-smoke]
---

# MANIFEST — provider-family-doe-observatory

## Summary

Restore a navigable, evidence-backed view across the existing provider population, nested execution family, configured-instance identity and DoE version/settings register. Reuse the existing registries and feed contracts; expose the DoE settings register as a versioned, source-attributed projection and preserve the existing `nested-family/v1` payload.

## Scope boundaries

- Swarm Quota remains the provider/capacity projection.
- Nested Family remains the execution-history projection and retains `nested-family/v1`.
- Configured-instance identity remains the DoE tuple and is grouped by `instance_key`, never model alone.
- The machine-readable DoE settings projection is derived from the register in `docs/ops/DOE-FAMILY.md`; unknown singular DoE version remains `NOT_ESTABLISHED`.
- QDesk participant issuance, account provisioning, credentials and suspension rehearsal remain in issue #5136 and its own evidence gates.
- The QDesk Observatory/Delphi implementation proposal in PR #5145 remains a separate review/runtime lifecycle; this work adds navigation and observability, not a competing scheduler or execution engine.

## Authorization and review record

Owner instruction received 2026-11-11: "Do it ALL". This authorizes the bounded implementation items below on a feature branch. Integration remains subject to repository validation and review.

## Checklist

- [x] Registered and itemized on the implementation branch
- [ ] Independent review recorded
- [ ] repo-gate and termux-smoke green on the same head SHA
- [ ] Review/check disposition reconciled
- [ ] Merge only under repository promotion policy
