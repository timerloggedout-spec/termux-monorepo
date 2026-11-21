---
id: pinecone-vector-store-comparison
title: "Pinecone vector-store reference and controlled PostgreSQL comparison"
author: ChatGPT
posted_at: 2026-11-21
source: README.md
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
  - id: ChatGPT
    role: author+executor
    status: executing
related_prs: [5753]
related_branches: [feat/pinecone-vector-store-doe-20261121-v2]
gates_required: [proposal-lifecycle, repo-gate, termux-smoke]
---

# MANIFEST — pinecone-vector-store-comparison

## Summary

Register the existing managed Pinecone integration in refTemplates and Integration Intelligence, then pre-register a quality-first DoE comparing pgvector HNSW, pg_pinecone native, and pg_pinecone remote over the same frozen corpus and vector matrix. The current integrated-inference index remains a separate end-to-end reference. The pure-Python metric evaluator and synthetic golden-ranking fixture are part of the offline contract.

## Reviewers

| ID | Role | Status | At | Notes |
|---|---|---|---|---|
| timerloggedout-spec | operator-authorizer | accepted | 2026-11-21 | Direct implementation instruction |
| ChatGPT | author+executor | executing | 2026-11-21 | Implementation and evidence reconciliation |

## Review log

### 2026-11-21 — timerloggedout-spec

- Disposition: accepted
- Notes: Add Pinecone to refTemplates and smods and wire a compared DoE experiment.

## Checklist (process)

- [x] Registered in docs/proposals/registry.yaml
- [x] ITEMS.md itemized
- [ ] At least one non-author review recorded
- [ ] Status → accepted before execution merges
- [ ] PRs cite Implements: PINE-001
- [ ] Gates green on merge
- [ ] Closed + moved to closed/ when terminal

## Links

- ITEMS: ./ITEMS.md
- Source: ./README.md
- PR: https://github.com/timerloggedout-spec/termux-monorepo/pull/5753
