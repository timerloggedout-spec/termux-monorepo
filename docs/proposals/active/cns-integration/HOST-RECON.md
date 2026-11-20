# CNS-06 — Canonical host reconnaissance

## Verified source owners

| Source | Verified responsibility | Integration consequence |
|---|---|---|
| brain/ and brain.rs | Domain-neutral Rust reasoning kernel and typed specialist extension contract. Merged by PR #5525. | Preserve kernel/provider separation and the shared typed extension boundary. |
| archwiz/mosaic_brain/ | Pure methodology-intelligence specialist, typed adapter, deterministic evidence evaluation, and cross-crate tests. | Route specialist work through the typed extension contract. |
| scripts/dispatch/project_task.py | Project-task issue-form intake and receipt generation. | Treat as intake; it does not establish the canonical Brain host. |
| scripts/ops/dispatch_executor.py | Delegates execution from already-admitted QUE state to existing claim/dispatch machinery. | Preserve QUE admission and dispatch ownership. |
| hub_mcp/protocol.py | Versioned job-envelope validation and protocol routing. | Reuse the existing versioned job boundary where the canonical host owner confirms compatibility. |
| hub_mcp/policy.py | Named capability authorization. | Keep production policy decisions with this authoritative owner or the explicitly verified QUE/QDesk policy owner. |
| docs/ops/ORCHESTRATION-CONTRACTS.md | Orchestration lifecycle and identity chain. | Preserve orchestration, cycle, and attempt identity end to end. |
| docs/ops/ORCHESTRATION-RECEIPT.schema.json | Canonical orchestration receipt shape. | Emit receipts through the existing schema. |
| src/orchestrator.py | Legacy provider, patch, test, and telemetry harness. | Treat as a legacy adapter surface; it does not establish canonical QUE/QDesk ownership. |
| harmony_hub/workspace/agent/direct_task.py | Harmony sandbox wrapper. | Treat as a sandbox reference, not the canonical QUE/QDesk host. |
| docs/proposals/active/continuous-capability-evolution-lab/MOSAIC-BRAIN-ROOT-INTEGRATION-PROPOSAL.md | MOS-007 root-Brain/MOSAIC integration design and explicit host-composition follow-on. | Preserve the existing architecture decision and ownership boundary. |

## Host discovery result

Repository source inspection verifies the kernel, specialist, issue intake, admitted dispatch, capability policy, orchestration lifecycle, and receipt schema as distinct owners. The canonical QUE/QDesk Brain host module and its bridge contract remain unlocated in the current master source tree.

The ownership map on feat/root-brain-rust-core-final also classifies the Python orchestrator as a harness/adapter target and records the QUE/QDesk host interface, authority freshness/revocation, dispatch idempotency, and runtime verification contracts as unverified.

## Admission and activation

RFP #5501 remains open with delphi:rfp and delphi:parked labels. Its recorded score is 6.69/25, recheck is after 2026-12-16T09:39Z, and filing_grants_execution is false. PR #5503 segments the RFP in the Delphi feed while preserving the parked decision.

The current shadow-composition test is an advisory, deterministic test fixture. It delegates the policy decision through the injected PolicyGate seam and exercises the specialist only after Ready. It grants no production dispatch, provider, memory-write, or promotion capability.

## Emulator and CI posture

The Rust kernel and MOSAIC integration tests execute on GitHub-hosted Linux runners under Rust 1.85.0 and 1.100.0. Device Termux and Android emulation are unnecessary for this platform-neutral typed composition. Use the provisioned repository emulator surfaces when the verified host contract introduces an Android/device-shaped boundary.
