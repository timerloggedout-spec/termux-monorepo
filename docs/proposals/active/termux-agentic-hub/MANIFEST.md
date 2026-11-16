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


### 2026-11-15 — user / ChatGPT — THUB-011 monorepo Brain kernel

- Disposition: **accepted by explicit Operator implementation instruction**.
- Research correction: do not treat the iOS-Termux brains.py HOLD-gate module as the Brain specification. It is excluded from this implementation.
- Scope: repository-root brain.rs as a provider-neutral cognitive kernel, with a dependency-free standalone brain/ crate facade and seven typed reasoning stages.
- Architecture: Brain reasons and returns a typed plan/decision; the existing harness governs the run; existing hands execute authorized actions. PolicyGate, memory, provider routing, evidence receipts and scheduling remain owned by existing canonical systems.
- Research references: AgentincOS Native seven-stage engine; JARVIS cognitive/execution split; BLADE selective-context Rust brain; brainctl persistent-memory API; Tended knowledge/coordination hub; Rig composable Rust agent components; LangGraph state-graph orchestration.
- Safety: no model credentials, direct tool execution, persistent memory, new policy registry, root Cargo workspace, or Python runtime switch. A later Python adapter requires separate protocol-parity and task-outcome evidence.


### 2026-11-16 — user / ChatGPT — THUB-012 monorepo Brain architecture and QUE RFP

- Disposition: **accepted continuation by explicit Operator instruction**; RFP #5501 filed for evaluation.
- Scope: expand the initial root Rust kernel into the monorepo-wide Brain architecture covering identity/intent, perception, context, knowledge/memory adapters, repository ontology, research intelligence, capability discovery, reasoning/planning, simulation, policy handoff, QUE/QDesk coordination, execution observation, verification/evidence, observability, adaptation, resilience, security, swarm and owner experience.
- Ownership: [TERMUX-MONOREPO-BRAIN-OWNERSHIP-MAP.md](../../../architecture/TERMUX-MONOREPO-BRAIN-OWNERSHIP-MAP.md) records source-inspected canonical owner paths, authority boundaries, integration contracts and explicit gaps.
- Research: the owner-supplied Perplexity GitHub and academic references are catalogued in [refTemplates/17_Papers/citations/brain-file-and-agent-architecture-survey.md](../../../../refTemplates/17_Papers/citations/brain-file-and-agent-architecture-survey.md), with source classes, limitations and linked_slots metadata. The actual refTemplates category names were reconciled against the repository tree.
- RFP: [qdesk.brain-rs #5501](https://github.com/timerloggedout-spec/termux-monorepo/issues/5501) filed using the existing delphi:rfp intake. Gate disposition: parked 6.69/25, recheck after 2026-12-16T09:39Z. This is an admission score for an unsourced synthetic surface, not a technical architecture verdict or runtime authorization.
- Segmentation: [PR #5503](https://github.com/timerloggedout-spec/termux-monorepo/pull/5503) registers a distinct brain-architecture comparison segment without changing gate scoring or creating a parallel panel.
- Safety: filing_grants_execution=false; existing QUE admission, policy, dispatch, memory, execution and evidence owners remain authoritative. Shadow-only integration precedes any separately authorized vertical slice. No second control plane, scheduler, registry, memory database or evidence ledger.
- Implementation: [PR #5492](https://github.com/timerloggedout-spec/termux-monorepo/pull/5492) remains the kernel and architecture delivery PR. Final Rust CI and repository gates are pending on its latest head; do not merge on stale checks.
