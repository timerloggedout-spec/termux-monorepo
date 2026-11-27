---
id: gate-admission-optimization
title: "Evidence-driven gate admission optimization"
author: ChatGPT
posted_at: 2026-11-27
source: source.md
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
related_issues: []
related_prs: []
related_branches:
  - feat/gate-admission-optimization-20261127
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — gate-admission-optimization

## Summary

Optimize repository gate admission by matching validation and provider execution to changed surfaces, reference impact, quota, and incremental evidence. Keep the repository gate universal, make Termux smoke conditional on the Termux execution surface, separate bucket-headroom contracts, expand dangle target-path coverage, preserve Vercel's existing quota-aware path selector, and treat Devin as an optional worker pending current entitlement evidence.

## Boundaries

- `repo-gate` remains the universal pull-request and integration-push floor.
- Termux smoke is required only for a Termux-surface change or explicit manual dispatch; unknown diff evidence admits smoke.
- A `SKIPPED` result records applicability and reason separately from execution.
- Dangle census retains its existing baseline, source scopes, rename mode, and read-only report.
- Vercel deployment remains project-scoped and quota/cooldown controlled.
- Devin remains an optional bounded worker; current API eligibility, free quota, billing boundary, and referral credit terms require separate evidence.
- Provider usage, deployment, credential, and account mutations remain within their existing authorization boundaries.

## Review log

### 2026-11-27 — timerloggedout-spec

- Disposition: accepted
- Notes: Operator directive “Yes; gate admission Optimizations; 3xact1y. Do Everything. Continue.” authorizes the bounded gate-admission optimization.

## Checklist

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [x] Operator authorization recorded
- [ ] Implementation tests green on the same head SHA
- [ ] Independent whole-branch review recorded
- [ ] Required CI and conditional gate dispositions recorded
- [ ] Close and move to `closed/` when all items are terminal

## Links

- ITEMS: ./ITEMS.md
- Source: ./source.md
- Design: ../../../superpowers/specs/2026-11-27-gate-admission-optimization.md
- Plan: ../../../superpowers/plans/2026-11-27-gate-admission-optimization.md
