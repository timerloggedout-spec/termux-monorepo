# CNS-06 — Canonical host and bridge reconnaissance

## Verified runtime owners

| Source | Verified responsibility | Integration consequence |
|---|---|---|
| .github/workflows/qdesk-self-repair.yml | Canonical scheduled QDesk execution plane for the self-repair domain; one batched cycle every three hours; invokes the repository's QDesk self-repair script; retains BRR evidence artifacts. | This is the QDesk host for self-repair work. Its domain boundary and kill switch remain authoritative. |
| scripts/que/self_repair.py | QDesk SIE loop: groups failing master workflows and stale feeds, creates idempotent QUE items, evaluates self-repair PR promotion, and records learned role weights. | Candidate advisory reasoning belongs before issue filing; the deterministic promote_decision and external DoE/Owner checks retain authority. |
| docs/proposals/active/qdesk-self-repair/MANIFEST.md and PROPOSAL.md | Define QDesk as the single scheduled execution plane and BRR as a read-only observer inside that cycle. | Reuse the existing QDesk cycle; preserve QUE ranking, claim, lease, reclaim, escalation, Desk, DoE, CI, and owner gates. |
| .github/workflows/swarm-admission.yml | Generic QUE admission workflow for issue-template filings carrying SWARM-DISPATCH blocks. | Admission precedes the template-declared execution route. |
| scripts/ops/swarm_admission.py | Deterministic tier → after → chain → flow admission evaluator; stamps swarm-admitted or deferred-by-tier. Its contract states that it spawns no work itself. | Preserve the existing admission decision and route execution to the template's declared owner. |
| scripts/que/que_item_fields.py | Owns immutable que-mandate/v1 and structured que-report/v1 fields. | Preserve explicit/inferred Mandate strength, policy version, receiving scope, trigger identity, and structured attention. |
| docs/proposals/active/que-superagent/LESSONS.md | Defines the planned QUE model-assessment layer for inferred candidates and the Mandate/Report lifecycle. | Candidate Brain seam: advisory model assessment after deterministic gates, with QUE admission remaining authoritative. |
| hub_mcp/policy.py | Named capability authorization for the local hub; current registry is observation and deterministic repository checks. | Keep capability authorization with the hub/host policy owner. Brain supplies no execution authority. |
| scripts/ops/dispatch_executor.py | Delegates execution from already-admitted QUE state to existing claim/dispatch machinery. | Preserve admission, claim, lease, and dispatch ownership. |
| docs/ops/ORCHESTRATION-CONTRACTS.md | Orchestration lifecycle and identity chain. | Preserve orchestration, cycle, and attempt identity end to end. |
| docs/ops/ORCHESTRATION-RECEIPT.schema.json | Canonical orchestration receipt shape. | Emit receipts through the existing schema. |
| docs/ops/CONTEXT-RELATIONSHIP-POLYGLOT-ACCELERATION.md and archwiz/context_relationships/rust_accel/src/main.rs | Existing optional Python-to-Rust accelerator; JSONL over stdin/stdout; Python retains collection, privacy, schema, and publication authority. | Reuse as a bridge-pattern precedent only; it is not a Brain bridge. |
| brain/ and brain.rs | Domain-neutral Rust reasoning kernel and typed specialist extension contract. Merged by PR #5525. | Preserve provider neutrality and typed extension boundaries. |
| archwiz/mosaic_brain/ | Pure methodology-intelligence specialist, typed adapter, deterministic evidence evaluation, and cross-crate tests. | Route specialist work through the typed extension contract. |
| scripts/dispatch/project_task.py | Project-task issue-form intake and receipt generation. | Treat as an intake surface; the file does not establish the Brain host. |
| src/orchestrator.py | Legacy provider, patch, test, and telemetry harness. | Treat as a legacy adapter surface; the file does not establish canonical QUE/QDesk Brain ownership. |
| harmony_hub/workspace/agent/direct_task.py | Harmony sandbox wrapper. | Treat as a sandbox reference, not the canonical Brain host. |

## Host discovery result

The repository contains two distinct production surfaces:

1. QDesk self-repair: .github/workflows/qdesk-self-repair.yml → scripts/que/self_repair.py. This host owns batched CI-failure/stale-feed observation, QUE self-repair issue intake, promotion evaluation, and learning.
2. Generic QUE admission: .github/workflows/swarm-admission.yml → scripts/ops/swarm_admission.py. This host owns issue-template admission and routes an admitted filing to its template-declared workflow. The admission evaluator itself launches no task.

The QUE Superagent proposal identifies a future model-assessment stage for inferred candidates. The current swarm_admission.py implementation remains a deterministic admission evaluator. This is the strongest candidate seam for a general Brain shadow assessment, subject to QUE owner confirmation.

Current master code search finds no production call to Brain::new, invoke_extension, or MosaicBrain outside the Brain/MOSAIC package tests and the merged shadow-composition test. The repository also has no methodology_intelligence SWARM-DISPATCH issue-template route. The Brain-specific host invocation and bridge contract therefore remain unimplemented.

## Bridge precedent

The Context Relationship accelerator establishes a language-neutral JSONL-over-stdin/stdout pattern. Python remains authoritative for collection, evidence classification, privacy, schema validation, and canonical artifact publication; Rust owns optional deterministic CPU-dense operations.

This pattern is a candidate for a Brain bridge. The Brain request/response envelope, host input mapping, policy adapter, failure semantics, and receipt mapping require agreement from the QUE host owner before the bridge becomes canonical.

## Admission and activation

RFP #5501 remains open with delphi:rfp and delphi:parked labels. Its recorded score is 6.69/25, recheck is after 2026-12-16T09:39Z, and filing_grants_execution is false. PR #5503 segments the RFP in the Delphi feed while preserving the parked decision.

The current shadow-composition test is a deterministic test fixture. It delegates the policy decision through the injected PolicyGate seam and exercises MOSAIC only after Ready. Production dispatch, provider calls, memory persistence, and promotion remain with existing owners.

## Emulator and CI posture

The Rust kernel and MOSAIC integration tests execute on GitHub-hosted Linux runners under Rust 1.85.0 and 1.100.0. Device Termux and Android emulation are unnecessary for this platform-neutral typed composition. Use the provisioned repository emulator surfaces when the verified host contract introduces an Android/device-shaped boundary.
