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
related_prs:
  - 5873
related_branches:
  - feat/repository-provisioner-workflow
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — repository-provisioner

## Summary

Maintain a manually dispatched GitHub Actions workflow that creates repositories under the authenticated personal account or an explicitly selected Free organization. The workflow verifies operator identity, organization-owner membership, destination Free plan, duplicate-name state, and created repository metadata. User-owned creation uses `POST /user/repos`; organization-owned creation uses `POST /orgs/{org}/repos` with an exact confirmation string. GitHub auto-initializes the default branch with a README.

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
- [x] RPW-001 personal-account route retained
- [x] RPW-002 organization-owned route implemented
- [ ] Gates green on merge
- [ ] Close + move to `closed/` when terminal

## Links

- ITEMS: ./ITEMS.md
- Source: ./source.md
