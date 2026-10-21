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

### 2026-10-21 — Cue — THUB-012 Kye Gomez scope correction

- User correction: The intended target is Kye Gomez, profile `https://github.com/kyegomez`, and the supplied Arnon-hs catalog card explicitly names `kyegomez/swarms`. The 676/241 inventory above belongs to `timerloggedout-spec`, not Kye; it remains historical evidence, not completion of the corrected owner scope.
- User deployment guidance: Rust is acceptable and remote services are already in use. Evaluate `The-Swarm-Corporation/swarms-rs` directly rather than imposing Python-only or on-device-only execution.
- Implementation: Added owner-validated public inventory collection with regression tests and a separate 455-repository Kye snapshot (five successful pages, no duplicates/errors). Corrected research provenance; reviewed selected Python implementation paths and Rust source at immutable revisions. The existing correct Python gitlink and runtime adapter remain unchanged.
- Validation: Extended focused suite 43 passed/one optional SDK skip; separate genuine-SDK test passed with stub inference and network forbidden; both local gates passed. Source-review findings are not all-code audits, Android certifications, Rust build results, or deployment claims. The original 676-repository JSON and unrelated working-tree edits are preserved. No remote push or promotion was performed from this stale local branch.

### 2026-10-21 — Cue — THUB-013 Rust-to-hub adapter

- Request: Continue the owner's Swarms integration using `The-Swarm-Corporation/swarms-rs`; Rust and remote inference are acceptable. Preserve the distinction between the historical 676-repository monorepo-owner inventory and Kye Gomez's saved 455-repository listing.
- Implementation: Added a Git-revision-pinned Rust worker with Cargo.lock and a separate offline-first Python CLI wrapper. Explicit execution/model selection, one/two agents and one to three bounded passes, no tools/MCP/planning, default task-completion tool disabled, and explicit hub URL/key mapping. Remote endpoints require HTTPS except loopback. No changes to the existing orchestrator, Python Swarms adapter, device authority, provider routes, or inventory JSON.
- State/result boundary: Child config via stdin, separate result.json protocol, both upstream diagnostic streams forwarded to stderr, conversation-shaped output retained, and sequential metadata written only to the temporary subprocess workspace. Parent cwd/environment remain unchanged; success, errors, and ordinary deadline termination clean local state. This is trusted-process isolation, not an OS sandbox or remote task-service deployment.
- Evidence: Locked Rust build and four unit tests passed. Extended focused suite: 82 passed/one optional Python SDK skip; six included real Rust-to-local-hub HTTP tests with stub inference cover direct execution, handoff, multiple passes, rejected auth/no inference, deadline cleanup, and CLI JSON. Existing genuine Python SDK test separately passed with deterministic stub inference and network forbidden. Independent review's IPv6 loopback mismatch was fixed and regression-tested. See `integrations/swarms/VALIDATION.md`.
- Limits: No live provider calls, Android/Bionic execution, remote deployment, full upstream tests, benchmark gain, broad rebase/pull, remote push/PR/merge, or production promotion from this stale branch. Existing unrelated provider documentation and `.serena/` remain outside the change.
