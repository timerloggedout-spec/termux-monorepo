---
id: build-orchestration-evaluation
title: "Polyglot build orchestration — evidence-led evaluation and governed pipeline integration"
author: ChatGPT
posted_at: 2026-11-05
source: PROPOSAL.md
status: posted
priority: P1
reviewers:
  - timerloggedout-spec
related_prs: []
related_branches:
  - proposal/build-orchestration-evaluation
gates_required: [proposal-lifecycle, repo-gate, termux-smoke]
---

# MANIFEST — build-orchestration-evaluation

## Summary

Evaluate and introduce a repository-native, adapter-based build/task orchestration layer for the polyglot Termux monorepo. Compare native tooling, Turborepo, Nx, and Moonrepo against the same real workloads; preserve the existing ArchWiz, DOE/MVT, proposal, dependency-phase, GitHub Actions, and Termux governance surfaces; and promote only the smallest proven capability. The initial delivery is proposal and evaluation-contract work only: no build runner, remote cache, workflow dispatch, or runtime behavior is enabled by this registration.

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| ChatGPT | author | posted | 2026-11-05 | Proposal author; no independent approval implied |
| timerloggedout-spec | operator-authorizer | requested | | Review architecture, budget, and promotion boundaries |

## Review log

### 2026-11-05 — ChatGPT

- Disposition: posted
- Notes: Registered an evidence-first proposal with explicit work items, architecture, pilot matrix, safety boundaries, and exit criteria. This is not an acceptance or authorization to deploy a new orchestration engine.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [ ] At least one non-author review recorded
- [ ] Status → accepted before execution merges
- [ ] PRs cite `Implements: BOE-00-01` (or the relevant item)
- [ ] Gates green on merge
- [ ] Closed + moved to `closed/` when terminal

## Links

- ITEMS: ./ITEMS.md
- Proposal: ./PROPOSAL.md
