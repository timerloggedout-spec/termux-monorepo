# CNS-06 source record

## Operator direction

2026-11-20: continue Brain integration with device Termux outside the dependency chain. Use repository CI and provisioned emulators when a device-shaped boundary requires verification.

## Governing work records

- CNS-06: https://github.com/timerloggedout-spec/termux-monorepo/issues/5693
- Brain subsystem integration tracking: https://github.com/timerloggedout-spec/termux-monorepo/issues/5588
- QDesk Brain RFP and Delphi admission: https://github.com/timerloggedout-spec/termux-monorepo/issues/5501
- RFP segmentation: https://github.com/timerloggedout-spec/termux-monorepo/pull/5503

## Merged implementation

- Root Brain kernel and typed extension contract: PR #5525, merge commit 1e784aa0f2717c646de66808b88e0dc26ff54ef6.
- Policy-gated Brain-to-MOSAIC shadow composition and receipt artifacts: PR #5712, merge commit f397a756900040b6d82e5c0b857be749101d9010.
- MOSAIC Rust validation run: 44719961386.
- Rust 1.85.0 receipt artifact: 14620489162.
- Rust 1.100.0 receipt artifact: 14621830842.
- Repository gate: run 44719961406, success.
- CI Termux-compatible smoke: run 44719961351, success.
- DO Statement Style: run 44719961452, success.
- Workflow Surface Evidence and Policy: runs 44719961384 and 44719961423, success.

## Owning sources

- brain/README.md
- docs/icm/objects/operations/brain-kernel.md
- docs/icm/objects/operations/mosaic-brain.md
- docs/ops/ORCHESTRATION-CONTRACTS.md
- docs/ops/ORCHESTRATION-RECEIPT.schema.json
- scripts/dispatch/project_task.py
- scripts/ops/dispatch_executor.py
- hub_mcp/protocol.py
- hub_mcp/policy.py
- src/orchestrator.py
- harmony_hub/workspace/agent/direct_task.py
- docs/proposals/active/continuous-capability-evolution-lab/MOSAIC-BRAIN-ROOT-INTEGRATION-PROPOSAL.md

## Current evidence limits

- ArchW1z dangle census run 44719961405 reported 81 repository-wide findings; the report listed no finding in the two files changed by PR #5712.
- Advisory CodeQL run 44719961534 encountered GitHub installation API rate limiting during SARIF publication/configuration.
- Production QUE/QDesk host and bridge ownership remain unverified in repository source.
- RFP #5501 retains parked status and filing_grants_execution=false.

## QUE/QDesk host and bridge sources

- QDesk scheduled self-repair host: .github/workflows/qdesk-self-repair.yml
- QDesk SIE/QUE self-repair implementation: scripts/que/self_repair.py
- QDesk ownership and promotion boundaries: docs/proposals/active/qdesk-self-repair/MANIFEST.md and PROPOSAL.md
- Generic QUE issue-form admission: .github/workflows/swarm-admission.yml
- Deterministic QUE admission evaluator: scripts/ops/swarm_admission.py
- QUE Mandate/Report schema owner: scripts/que/que_item_fields.py
- QUE model-assessment design: docs/proposals/active/que-superagent/LESSONS.md
- Optional Python-to-Rust JSONL bridge precedent: docs/ops/CONTEXT-RELATIONSHIP-POLYGLOT-ACCELERATION.md and archwiz/context_relationships/rust_accel/src/main.rs

The QDesk self-repair host is verified for its domain. The general Brain invocation point, MOSAIC issue-template route, and Brain JSONL request/response schema remain unimplemented and require QUE owner confirmation.
