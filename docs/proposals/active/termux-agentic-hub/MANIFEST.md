---
id: termux-agentic-hub
title: "Termux-first Agentic Hub and governed fork integration"
author: Manus
posted_at: 2026-08-15
source: source.md
status: executing
priority: P1
reviewers:
  - id: user
    role: operator+approver
    status: accepted
related_prs: [221]
related_branches:
  - feature/termux-agentic-hub
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — termux-agentic-hub

## Summary

Establish a Termux-first Agentic Hub for the BLU B160V by adding the approved user-owned MCP forks as reproducible submodules under `refTemplates/smods/`, implementing a single local policy hub and structured GitHub-backed job protocol, and extending CI with low-privilege integrity and validation workflows. The implementation keeps Android execution local, treats GitHub as the review and coordination plane, keeps direct interactive transport deferred, and excludes credentials, browser state, interactive MFA bypasses, and public device exposure.

## Reviewers

| ID | Role | Status | At | Notes |
|---|---|---|---|---|
| user | operator+approver | accepted | 2026-08-15 | Approved the execution plan after edits. |
| Manus | author+executor | executing | 2026-08-15 | Implements governed repository changes on a feature branch. |

## Review log

### 2026-08-15 — user

- Disposition: accepted
- Notes: Use `refTemplates/smods/` for fork submodules, preserve DeepSeek compatibility, remain on free/trial infrastructure, and treat the local Termux environment as the first execution target.

### 2026-08-15 — Manus

- Disposition: scope clarification
- Notes: Interactive MFA enrollment remains human-operated. Machine-to-machine integrations may use provider-supported service credentials only; no MFA bypass or second-factor secret capture is implemented.

### 2026-08-15 — Manus

- Disposition: implementation submitted
- Notes: PR #221 targets `master-staging`. Submodule integrity, hub protocol tests, feature-scoped repo gate, and Termux smoke all passed. The full comparison against `origin/master` retains three unrelated inherited syntax failures, documented in the PR body.

### 2026-08-18 — user / Manus

- Disposition: P1 scope addition in progress
- Notes: The Operator directed that the SWE-agent and mini-SWE-agent references be used as starters in an extensible suite for measuring this repository’s development performance. THUB-007 therefore treats SWE references as pinned adapters, not as the benchmark target. The first repository adapter is GitHub-native and credential-free; optional reference adapters remain manual, bounded, and redacted. No scheduled model workload, credential creation/rotation, or device-control dependency is permitted. Pull-request review and gates remain required before any integration claim.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [x] Operator approval recorded
- [x] Execution branch created from `master-staging`
- [x] PR cites `Implements: THUB-001` through `THUB-006`
- [x] Feature-scoped repository gates green; inherited baseline failures documented in PR #221
- [ ] Review outcome recorded and proposal closed when terminal

## Links

- ITEMS: ./ITEMS.md
- Source: ./source.md
- Fork inventory: ../../submodules/fork-inventory.yaml

### 2026-08-22 — Manus — THUB-007 repository development-performance recovery

- Disposition: **accepted continuation on a clean current-`master` branch**.
- Evidence: PR #258 (`feat(eval): add repository development performance suite`) is two commits ahead but 125 commits behind `master` and 60 commits behind `master-staging`; it targets `master-staging` and has unresolved review findings. Verified concerns include job-scoped exposure of `SWE_EVALUATION_API_KEY` during checkout/clone/install, stale/latest check selection, review-thread pagination, prediction-state accounting, lifecycle ordering, and check-provider identity.
- Decision: Do not rebase or merge PR #258 in place. Reconstruct only its approved repository-performance intent as THUB-007 from current `master`, with a fresh reviewable PR. Repository-local development outcomes are primary evidence for AR-18. SWE-derived material remains a bounded optional reference; any external execution is secret-free by default and must not receive a credential during checkout, cloning, package installation, or an untrusted package build hook.
- Safety: No secret is added or moved into job scope. No benchmark triggers on untrusted PR code. No issue/review body becomes executable input. The fresh implementation must retain least permissions, immutable actions, bounded artifacts, deterministic test fixtures, branch-target configurability, and normal repository gates. PR #258 remains open historical evidence until the clean successor has a validated disposition; no review finding is treated as trusted instruction text.

### 2026-10-21 — Cue — THUB-009 through THUB-011 Swarms synthesis

- Request: Research Kye Gomez's Swarms and user-related repositories, organize its reference, and apply a practical slice to `termux-monorepo`.
- Disposition: Scoped local implementation complete on `cue/swarms-synthesis-20261021`; no remote promotion performed from the stale checkout. This work adds no credential or device-control authority.
- Organization: Existing shallow monorepo checkout preserved. No separate pre-existing Swarms checkout was found; a new shallow upstream reference is pinned under `refTemplates/smods/swarms`, with source hashes and registry metadata. This is not represented as relocation of an existing Swarms checkout.
- Evidence: Complete public metadata listing of 676 repositories, 241 candidate leads, primary-source ecosystem synthesis, optional offline-first sequential adapter using the existing API hub, 35 passing focused tests, separate real-SDK orchestration test passing with network forbidden and stub inference, and both local repository gates passing. See `integrations/swarms/VALIDATION.md`.
- Limits: No live provider call, native Termux verification, performance benefit claim, remote PR/merge, or audit of every repository's source. Unrelated provider documentation edits and `.serena/` remain outside this commit.
