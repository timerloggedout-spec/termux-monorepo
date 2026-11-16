---
type: object
cluster: operations
universe: live
status: initiated
entity: brain.rs
verified_at: 2026-11-15
---

# Monorepo Brain Kernel

> This file documents the initial P1 reasoning kernel, not the complete monorepo Brain. The broader cognitive architecture, subsystem taxonomy and staged integration roadmap live in [monorepo-brain.md](monorepo-brain.md) and the [subsystem map](../../../architecture/TERMUX-MONOREPO-BRAIN-SUBSYSTEM-MAP.md) and [source-inspected ownership map](../../../architecture/TERMUX-MONOREPO-BRAIN-OWNERSHIP-MAP.md). The associated [qdesk.brain-rs RFP #5501](https://github.com/timerloggedout-spec/termux-monorepo/issues/5501) requests evaluation only.

**Brain** is the shared, provider-neutral cognitive kernel at repository root. It turns a request and bounded context into typed reasoning-stage records, a validated execution plan, and a decision from an injected policy adapter.

## Why this shape

The monorepo already has model providers, planners, dispatchers, capability policy, memory, evidence and execution surfaces. A generic Brain must coordinate reasoning without replacing those authorities or creating another control plane.

## Shape

- Root source: brain.rs; public type: Brain.
- Shared Rust package: brain/, a dependency-free facade over the root source; no root Cargo workspace.
- Seven stages: Intent, Decomposition, Strategy, ExecutionDesign, Validation, Optimization and Reflection.
- Adaptive/Fast/Standard/Deep modes bound the work (Adaptive is the default); Adaptive chooses depth from assessed complexity; optional stages can degrade without hiding failures.
- Context selection uses caller-provided provenance, sensitivity classification, relevance and token estimates.
- Execution plans are typed DAGs; the kernel validates IDs, dependencies, cycles and bounded parallel groups.
- StageBackend supplies model/deterministic reasoning; PolicyGate receives context provenance, stage records and degradation status before delegating to existing repository policy.
- Reflection returns learning candidates only; existing memory/CRG systems own persistence.

## Connected to

- **owned-by:** root brain.rs and the standalone brain/ crate.
- **joins:** existing harness/orchestrator inputs to typed plans, policy decisions and evidence references.
- **delegates-to:** hub_mcp capability policy, scripts/decision_engines.py, existing provider adapters, memory stores and execution hands.
- **looks-like-but-is-not:** a model provider, tool runner, scheduler, persistent memory database, or promotion authority.

## If you change this

- **Hits:** brain contract tests, standalone Cargo checks, path-filtered Rust CI, orchestration contract documentation, ICM index and any crate that consumes termux-brain.
- **Does not hit:** Python runtime imports, provider credentials, device state, existing policy registries or task-execution backends unless a separate adapter proposal explicitly changes them.

## Validation boundary

A Brain run marked Completed means its required reasoning stages completed. A decision marked Ready means only ready for handoff. Neither means the task executed, passed its outcome checks, or was promoted.