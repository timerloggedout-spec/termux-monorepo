---
id: agent-stack-48-intake
title: "Agent Stack 48 — LabLab hackathon source intake and OSINT watch"
author: ChatGPT
posted_at: 2026-11-20
source: source.md
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
related_prs:
  - 5725
related_branches:
  - feat/agent-stack-48-intake-20261120
gates_required: [proposal-lifecycle, repo-gate, termux-smoke]
---

# MANIFEST — agent-stack-48-intake

## Summary

Register the official Agent Stack 48 event page as a public-source candidate in the existing challenge coordinator. Preserve sourced dates, tracks, submission requirements, and explicit unknowns; let the existing Challenge OSINT watcher capture page hashes and changes. The intake does not register an entrant, select a project, or claim prize/eligibility details.

## Review log

### 2026-11-20 — timerloggedout-spec

- Disposition: accepted
- Notes: Operator request authorizes adding the supplied event source to the existing ingestion system.

## Checklist

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [ ] Initial official-page snapshot observed from Challenge OSINT watcher
- [ ] Proposal lifecycle, repo-gate, and Termux smoke pass on the same immutable PR head
- [ ] Evidence, limitations, and deferred decisions reconciled
- [ ] Merge/promotion under repository policy

## Links

- ITEMS: ./ITEMS.md
- Source: ./source.md
