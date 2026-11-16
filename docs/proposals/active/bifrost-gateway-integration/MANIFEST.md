---
id: bifrost-gateway-integration
title: "Bifrost AI gateway + benchmarking forks — RECON, catalog, provider path"
author: grok
posted_at: 2026-09-23
source: operator-maintained proposal
status: executing
priority: P1
reviewers:
  - id: grok
    role: author+executor
    status: executing
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
related_prs: [611]
related_branches:
  - docs/bifrost-gateway-recon-reconcile
related_repos:
  - https://github.com/timerloggedout-spec/bifrost_fork
  - https://github.com/timerloggedout-spec/bifrost-benchmarking_fork
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — Bifrost Gateway Integration

## Summary

Track the Bifrost gateway and benchmark forks as a bounded provider/reference lane. Preserve the existing recon, catalog, provider-path, and benchmark evidence without making the provider a source-of-truth dependency.

## Boundary

- reference/adaptation first;
- no secret values in the repository;
- provider success does not imply task correctness;
- compare providers against the shared evidence contract before adoption.

## Evidence

See RECON.md, ITEMS.md, and BENCHMARK-SMOKE.md. Keep the proposal registry entry and manifest synchronized.
