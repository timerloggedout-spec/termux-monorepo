---
id: repository-provisioner
title: "GitHub repository provisioning workflow"
author: ChatGPT
posted_at: 2026-11-21
source: source.md
status: accepted
priority: P1
reviewers:
  - timerloggedout-spec
related_prs: []
related_branches:
  - feat/repository-provisioner-workflow
gates_required: [repo-gate]
---

# MANIFEST — repository-provisioner

## Summary

Add a manually dispatched GitHub Actions workflow that creates a repository under the authenticated GitHub account through the established PAT `POST /user/repos` route, initializes its default branch, seeds a provisioning receipt through the Contents API, and publishes the created repository metadata in the run summary.

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| timerloggedout-spec | operator-authorizer | accepted | 2026-11-21 | Explicit instruction: create and merge the repository-provisioning workflow |

## Review log

### 2026-11-21 — timerloggedout-spec

- Disposition: accepted
- Notes: Authorized the repository-provisioning workflow implementation and merge.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [x] Operator authorization recorded
- [x] PR cites `Implements: RPW-001`
- [ ] Gates green on merge
- [ ] Close + move to `closed/` when terminal

## Links

- ITEMS: ./ITEMS.md
- Source: ./source.md
