---
id: master-staging-reconciliation
title: "Master-staging reconciliation and scope-aware Termux validation"
author: ChatGPT
posted_at: 2026-11-24
source: source.md
status: executing
priority: P0
reviewers:
  - id: timerloggedout-spec
    role: operator+approver
    status: accepted
  - id: ChatGPT
    role: author+executor
    status: executing
related_prs: [5843]
related_branches:
  - master-staging
  - termux-smoke
  - reconcile/master-staging-scope-20261124
gates_required:
  - repo-gate
  - termux-smoke
---

# Master-staging reconciliation

## Objective

Reconcile candidate work from `master-staging` onto canonical `master` through bounded, evidence-backed extraction. Keep Termux validation scoped to Termux runtime and device operations.

## Authority

- Canonical integration branch: `master`
- Candidate source branch: `master-staging`
- Separate Termux runtime lane: `termux-smoke`
- Reconciliation procedure: `.github/skills/production-reconciliation/SKILL.md`

## Operating controls

- Preserve every source branch and commit identity during extraction.
- Classify each staging workstream as already represented, extractable, superseded, blocked, or pending evidence.
- Integrate coherent workstreams through current-master feature branches and reviewable PRs.
- Run `repo-gate` for repository changes.
- Run `termux-smoke` for Termux-related changes.
- Keep quota, provider, general CI, and repository governance tests in their owning workflows.

## Review log

### 2026-11-24 — Operator directive

- Disposition: accepted
- Notes: Reconcile `master-staging` with `master`. Scope `termux-smoke` to Termux-related operations.

### 2026-11-24 — ChatGPT reconnaissance

- Disposition: inventory recorded
- Evidence: `docs/ops/MASTER-STAGING-RECONCILIATION-2026-11-24.md`
- Notes: The branch comparison is diverged. The extraction strategy preserves the 56 staging-only commits and the seven open staging-targeted PRs as separately reviewable source material.
