---
id: github-profile-marketing-surface
title: "GitHub profile marketing surface — content projection, referral spotlight rotation, and custom displays"
author: ChatGPT
posted_at: 2026-11-22
source: source.md
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
related_issues: [574]
related_prs: []
related_branches:
  - feat/github-profile-marketing-surface-20261122-r1
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — github-profile-marketing-surface

## Summary

Create a source-driven GitHub profile README projection in Termux MonoRepo. Reuse the existing partner registry and public video library; rotate one featured active partner weekly; render custom SVG displays; validate the output; and refresh it through a scheduled GitHub Actions workflow.

## Authorization

Operator request on 2026-11-22: upgrade the GitHub profile as a marketing opportunity surface, include YouTube Shorts and hackathon videos, rotate referral URLs, and add custom profile displays. The operator accepted this bounded P1 work item.

## Review log

### 2026-11-22 — timerloggedout-spec

- Disposition: accepted
- Notes: Operator explicitly requested profile upgrade and routine setup. Profile-repository publication remains a separately blocked provisioning item because the same-name GitHub profile repository is currently absent.

## Checklist

- [x] Registered in docs/proposals/registry.yaml
- [x] ITEMS.md itemized
- [x] Operator authorization recorded
- [ ] Generated projection validated on current repository sources
- [ ] repo-gate and termux-smoke pass on the implementation SHA
- [ ] Create same-name public profile repository and enable publication
- [ ] Close when publication and refresh lifecycle are verified

## Links

- ITEMS: ./ITEMS.md
- Source: ./source.md
