# Implementation Plan — Monorepo Brain Kernel

**Date:** 2026-11-15  
**Proposal item:** THUB-011  
**Base:** current master (the staging branch is materially divergent)

## Task 1 — Root cognitive contract

- Create brain.rs at repository root.
- Add typed seven-stage API, Fast/Standard/Deep stage profiles, provenance-aware bounded context selection, explicit fallback/degraded states, typed execution DAG validation, and an injected PolicyGate.
- Keep the module provider-neutral and side-effect-free: no model client, tool execution, memory store, scheduler, shell or network.
- Acceptance: stage mismatch/required failure cannot return Ready; optional stage failure and fallback are visible; validation and plan structure are fail-closed.

## Task 2 — Shared Rust crate facade

- Create brain/Cargo.toml and brain/src/lib.rs.
- Re-export the root brain.rs source through a path module.
- Keep this crate standalone, dependency-free, and outside a root Cargo workspace.
- Acceptance: any monorepo Rust crate can depend on the same termux-brain path package; there is only one implementation source.

## Task 3 — Contract tests

- Create brain/tests/brain.rs with fixture stage and policy adapters.
- Cover Fast/Standard/Deep stage selection; deterministic context ranking and sensitivity exclusions; duplicate IDs; DAG dependency/cycle validation; injected policy decision preservation; validation failure; required-stage failure; optional-stage degradation; fallback transparency; wrong-stage output.
- Acceptance: tests pass without network or model credentials.

## Task 4 — Repository documentation and ICM

- Add the design/spec and this plan.
- Add an ICM object card and object-index/route entries.
- Document Brain/Harness/Hands, policy/memory/execution ownership and the Python integration boundary in docs/ops/ORCHESTRATION-CONTRACTS.md and root CLAUDE.md.
- Register THUB-011 in the already-approved Termux Agentic Hub work ledger.
- Acceptance: links resolve; proposal and ICM indexes point to the canonical source; no duplicate registry or control plane is created.

## Task 5 — Focused remote Rust validation

- Add a path-filtered .github/workflows/brain-rust.yml using the repository's reviewed Rust toolchain action pin.
- Run format, check, tests and Clippy on the exact branch SHA.
- Run/re-fetch repository repo-gate and termux-smoke checks; inspect terminal results and review findings before promotion.
- Acceptance: all required checks are terminal and green on the same SHA; no claim of Python runtime integration or device smoke beyond actual evidence.

## Task 6 — Branch closeout

- Review the full diff for unrelated edits, case-only paths, policy duplication, secret exposure and stale staging ancestry.
- Open a PR targeting master with Implements: THUB-011.
- Wait for checks, re-fetch the head SHA/checks, and update the proposal work item with evidence.
- Acceptance: PR is reviewable and all reported lifecycle states are evidence-backed. Do not merge if required gates or task outcome are not verified.