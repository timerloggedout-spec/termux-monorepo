# CNS-06 Brain host integration plan

Date: 2026-11-20
Work item: CNS-06
Proposal: docs/proposals/active/cns-integration/
Status: shadow composition validated; production host discovery remains blocked.

## Task 1 — Verify merged kernel and specialist contracts

Status: complete.

- Inspect the root Brain public API, typed extension contract, MOSAIC adapter, and cross-crate tests.
- Confirm PR #5525 is merged and the root kernel remains provider-neutral.
- Confirm MOSAIC remains a one-way specialist dependency and preserves run identity.

## Task 2 — Build the bounded shadow composition proof

Status: complete in PR #5712.

- Add a deterministic host-composition integration test.
- Run the standard Brain reasoning path through an injected PolicyGate.
- Route methodology_intelligence to MOSAIC only after a Ready decision.
- Preserve orchestration_id, cycle_id, and attempt_id through the typed extension response.
- Verify NeedsApproval blocks specialist handoff.
- Retain exact test output as a GitHub Actions artifact for Rust 1.85.0 and 1.100.0.

Validation evidence:
- MOSAIC Rust matrix run 44719961386: both toolchains passed fmt/check/test/Clippy.
- Each toolchain ran 22 specialist tests and 2 shadow-composition tests successfully.
- Receipt artifacts: 14620489162 and 14621830842.
- Repository gate 44719961406 and CI Termux-compatible smoke 44719961351 passed.

## Task 3 — Identify canonical QUE/QDesk host and bridge owner

Status: existing QDesk and QUE host surfaces identified; Brain-specific route and bridge owner confirmation remain open.

- Verify the QDesk self-repair host at .github/workflows/qdesk-self-repair.yml and scripts/que/self_repair.py.
- Verify generic QUE issue-form admission at .github/workflows/swarm-admission.yml and scripts/ops/swarm_admission.py.
- Review the QUE Superagent inferred-candidate model-assessment design.
- Confirm the QUE owner-approved Brain invocation point and define the versioned JSONL request/response contract, identity propagation, policy owner, authority freshness/revocation, dispatch idempotency, and receipt consumer.
- Treat project_task.py as issue intake and dispatch_executor.py as admitted dispatch delegation.
- Treat src/orchestrator.py and the Harmony sandbox as legacy harnesses until the canonical owner confirms otherwise.
- Record verified QDesk/QUE host owners and the unimplemented Brain-specific bridge in HOST-RECON.md.

## Task 4 — Secure fresh production admission

Status: blocked on Delphi admission.

- Reconcile the parked qdesk.brain-rs RFP #5501 with the actual host/bridge evidence.
- Obtain a fresh admission decision through the repository Delphi process.
- Keep filing_grants_execution=false until the authoritative RFP record changes.

## Task 5 — Implement one bounded production vertical slice

Status: queued behind Tasks 3 and 4.

- Add the host-owned adapter at the verified composition point.
- Delegate capability authorization to the authoritative policy owner.
- Preserve orchestration/cycle/attempt identity across request, specialist result, and receipt.
- Keep tool execution and memory persistence with existing host owners.
- Add host integration tests that exercise the actual bridge and emit a schema-valid ORCHESTRATION-RECEIPT.
- Validate both repository gates and capture a runtime receipt tied to the exact SHA.

## Completion rule

Promote CNS-06 only after the canonical host and bridge are verified, fresh Delphi admission is recorded, the bounded production route passes host integration tests, and the attributable runtime receipt confirms the requested handoff.
