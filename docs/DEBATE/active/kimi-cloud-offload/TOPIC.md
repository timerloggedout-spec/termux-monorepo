---
id: kimi-cloud-offload
title: "Corrected Cloud Offload & Parallelization Evaluation"
status: open
priority: P1
tags: [cloud, tmux, parallel, P1]
bias_warn: [author-heavy]
proposal: kimi-cloud-offload
source_branch: docs/kimi-cloud-offload-evaluation
opened: 2026-08-04
---

# TOPIC — kimi-cloud-offload

## Claim under debate

Kimi2.6 corrections should become shared intent for cloud offload work:
Impatient User Burst retries, Big-O routing, TMUX retirement in favor of
archwiz/Hermes/chronos, AGY×Jules templates, jules-worker-pool path.

**Full text:** branch `docs/kimi-cloud-offload-evaluation`  
**Pointer:** `docs/proposals/corrected_cloud_offload_evaluation.md`  
**Proposal ledger:** `docs/proposals/active/kimi-cloud-offload/`

## Non-goals

- Merging 24KB body onto master before accept
- Implementing KCO-* without Tier 2–3 accept

## Participants

| ID | Role | Skill | Bias note |
|----|------|-------|-----------|
| kimi | driver | evaluation | author of source text |
| grok-archw1z | registrar | process | registered; not yet accept-voter |

## Open questions

1. KCO-03 TMUX scope: termux-multi-agent only vs monorepo-wide?
2. Full body promote to master after accept?
3. jules-worker-pool: resume fork vs greenfield Rust?

## Links

- VOTES: ./VOTES.md
- THREAD: ./THREAD.md
- MANIFEST: ../../proposals/active/kimi-cloud-offload/MANIFEST.md
- Linear: TER-116
