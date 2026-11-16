---
type: object
cluster: operations
universe: live
status: initiated
entity: brain.rs
verified_at: 2026-11-16
---

# Monorepo Brain Kernel

The shared, provider-neutral reasoning kernel. It produces typed stage records, a bounded execution plan, and an injected policy decision. It does not execute tools, persist memory, own policy, schedule work, or promote changes.

## Source

- Kernel: [`brain.rs`](../../../../brain.rs)
- Cargo facade: [`brain/`](../../../../brain/)
- Specialist contract: [`brain/src/extensions.rs`](../../../../brain/src/extensions.rs)
- MOSAIC specialist: [`mosaic-brain.md`](mosaic-brain.md)
- Integration design: [MOSAIC ↔ root Brain proposal](../../../proposals/active/continuous-capability-evolution-lab/MOSAIC-BRAIN-ROOT-INTEGRATION-PROPOSAL.md)

## Kernel contract

- Seven stages: Intent, Decomposition, Strategy, ExecutionDesign, Validation, Optimization and Reflection.
- Adaptive/Fast/Standard/Deep modes bound reasoning depth.
- Context selection uses source provenance, sensitivity, relevance and token budgets.
- Execution plans are typed DAGs with bounded dependency validation.
- StageBackend supplies reasoning; PolicyGate delegates to existing policy owners.
- Reflection produces learning candidates; canonical memory owners decide persistence.
- `BrainExtension` provides a statically typed seam for specialist domain crates.

## Ownership boundaries

The root Brain is a shared cognitive kernel, not a policy or orchestration authority. QUE/QDesk owns admission and lifecycle; hub_mcp owns capability policy; existing dispatch, provider routing, memory, evidence and verification systems remain canonical.

## Validation boundary

A Brain run marked Completed means required reasoning stages completed. A decision marked Ready means ready for handoff only. Neither means the task executed, passed its outcome checks, or was promoted.

## If you change this

Run the standalone `termux-brain` format/check/test/Clippy workflow and preserve the extension contract and run/cycle/attempt identity semantics. See [Change and Validate](../../processes/change-and-validate.md).
