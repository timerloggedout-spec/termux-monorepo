---
id: ml-pipelines-init
title: "GitHub ML Pipelines init + Issue #175 matrix + PR minesweeper"
author: Grok (Administrator)
posted_at: 2026-09-05
source: source.md
status: executing
priority: P0
reviewers: []
related_prs: []
related_issues: [213, 175, 192, 337, 265]
related_branches: [feat/ml-pipelines-init-175]
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — ml-pipelines-init

## Summary

Initialize stdlib-only GitHub ML pipelines for commit/PR/Actions
observe-mode scoring, bind the Issue #175 operator matrix to a
machine-checked YAML catalog, and classify open PRs so duplicate
Jules lanes can be mineswept without wholesale merges.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [ ] At least one non-author review recorded
- [ ] Status → accepted before execution merges
- [x] PRs cite `Implements: <ITEM-ID>`
- [ ] Gates green on merge
