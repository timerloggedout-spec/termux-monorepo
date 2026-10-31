# Flywheel Capability Overlap Audit

**Status:** Evidence-backed repository-side audit; upstream component execution and security review remain pending.
**Date:** 2026-10-23
**Scope:** Dicklesworthstone Agentic Coding Flywheel Setup (ACFS) core loop and supporting tools, compared with existing `termux-monorepo` control planes.
**Related records:** [ACFS integration contract](DICKLESWORTHSTONE-FLYWHEEL-INTEGRATION.md), [repository-native adapter](FLYWHEEL-RUNTIME.md), [upstream core-loop methodology](https://github.com/Dicklesworthstone/agentic_coding_flywheel_setup/blob/main/docs/methodology/THE_FLYWHEEL_CORE_LOOP.md).

## Decision

**Do not install or fork ACFS components yet.** The repository already has a local, executable validation adapter and canonical task/dependency, dispatch, cadence, and Delphi outcome-feedback surfaces. The next useful increment is evidence gathering against those contracts—not another scheduler, task ledger, scoring ledger, or installer path.

The upstream core-loop guide names three operating tools: Agent Mail for coordination, Beads Rust (`br`) for dependency-aware task management, and Beads Viewer (`bv`) for graph-aware triage. It explicitly separates these from plan creation. The repository-native adapter already reuses its dependency-phase engine, deterministic admission waves, existing claim/dispatch path, repository gate, and Termux smoke command. This establishes overlap at the *capability-contract* level; it does not establish that the upstream tools are interchangeable or that every edge case is covered.

## Capability matrix

| Capability | Existing repository contract/evidence | Upstream candidate | Disposition | Evidence still required |
|---|---|---|---|---|
| Planning and acceptance criteria | Proposal/ITEMS workflow and PR contracts; plans are inputs to the local adapter | Multi-model planning methodology | **Reuse existing** | Validate template coverage against one representative multi-phase change; no new planning runtime needed |
| Dependency-aware task graph | `docs/agentic/dependency-phases.json` and `dependency_phase_engine.evaluate_plan`; adapter validates dependencies, approvals, claims, readiness, digest, and admission waves | Beads Rust (`br`) | **No second ledger** | Disposable fixture round-trip: dependency direction, blocked/ready states, stable IDs, metadata preservation, conflict/recovery; decide only from measured gaps |
| Graph-aware triage | Local adapter sorts eligible work by admission wave and phase identifier; no graph mutation | Beads Viewer (`bv`) | **Benchmark read-only** | Same frozen graph fixture for `bv` and local output; compare determinism, explanation quality, blocker-unblocking value, and runtime footprint |
| Multi-agent coordination and file reservations | Existing dispatcher and canonical issue/routing checks; local adapter emits a handoff only. Its process lock is local concurrency protection, not a distributed lease | MCP Agent Mail | **Highest-priority gap assessment** | Inspect the actual existing Agent Mail actions/service and contract; prove identity, reservation expiry, idempotency, stale-owner recovery, concurrent conflict handling, and no duplicate dispatch |
| Destructive-command safety / approval | Existing approval checks, repository policy gates, and project permission boundaries are present in the local validation path | DCG and SLB | **Map before adding** | Build a command-policy mapping and negative test corpus; verify fail-closed behavior, bypass resistance, and compatibility with Termux. Do not infer equivalence from naming |
| Interactive multi-agent terminal | Existing GitHub Actions and Cadence/Gantt controls own repository automation and dispatch cadence | NTM / tmux fleet | **Optional operator layer** | Demonstrate a human-visible gap not served by current interfaces; check process lifecycle, cancellation, logs, Linux/Termux support, and no hidden background service |
| Session search and memory | Repository has indexed/tool-taxonomy and session-security-related artifacts, but this audit has not established a canonical, privacy-reviewed session-search service | CASS and CASS Memory | **Defer** | Inventory existing implementations first; define data classification, redaction, retention/deletion, access control, provenance, retrieval-quality baseline, and resource budget |
| Decision-quality feedback | `scripts/delphi/gate.py`, `ops/delphi/panel.json`, tests, and Delphi workflow maintain the existing outcome-feedback and weights path | Potential evaluation evidence from any candidate tool | **Reuse existing ledger** | Define a versioned evidence adapter only after a real, attributable task outcome; a green validation run is not a confirmed/missed forecast |
| Scheduling, cooldown, and provider dispatch | Existing Cadence/Gantt/Flywheel controls and WAIT/WATCH/VALIDATE/RE-FETCH/COMPARE policy | NTM / ACFS orchestration | **No second scheduler** | Any proposed integration must pass existing cadence, idempotency, and current-SHA checks |
| Bootstrap and installation | Existing repository gates validate the local adapter; no ACFS installer is part of the runtime | ACFS bootstrap installer | **Metadata-only** | Disposable Linux environment, immutable upstream revision, reviewed install manifest, license/security review, rollback proof, and platform-specific evidence before any fork/pin |

## Evidence boundaries

Confirmed from the repository's current integration/runtime documentation:

- The local adapter is implemented in `scripts/agentic/flywheel.py` and documented in `docs/ops/FLYWHEEL-RUNTIME.md`.
- It uses existing dependency-phase validation and deterministic admission waves; it does not create a Beads database.
- Handoffs are emitted for the existing dispatcher; the adapter does not claim a live Agent Mail reservation or distributed lease.
- It runs fixed repository-gate and Termux-smoke commands under a local process lock.
- It does not modify Delphi weights, fabricate votes, or deploy a service.
- The upstream ACFS installer and its component binaries remain uninstalled by this integration.

Not yet proven by this audit:

- Functional parity between the local task graph and `br`.
- Triage quality parity between local admission ordering and `bv`.
- Whether the existing Agent Mail actions provide the full reservation/lease semantics needed by the upstream core loop.
- Whether existing destructive-command controls match DCG/SLB policy coverage.
- Native Android/Termux compatibility of any ACFS upstream component.
- A measured production outcome or net productivity benefit.

## Recommended next experiment

Run a **disposable Linux, no-production-data comparison** with one small multi-phase task fixture and pinned upstream revisions:

1. Capture a baseline using the existing plan validator, admission waves, dispatcher handoff contract, repository gate, and Termux smoke path.
2. Test `br` and `bv` against the same fixture in isolated temporary state; record install footprint, task/dependency round-trip, triage stability, and operator steps.
3. Inspect existing Agent Mail actions before standing up any second service. Test duplicate claims, lease expiry, stale-owner recovery, and competing reservations only where a real service is available.
4. Run the safety-tool comparison as a separate negative-test suite; never use destructive commands against a real workspace.
5. Record command lines, immutable source SHAs, raw test outcomes, elapsed time, resource footprint, and observed limitations. Do not treat a synthetic fixture as a production outcome.
6. Recommend a fork or gitlink only if the experiment identifies a concrete capability gap and passes the existing inventory, repository-gate, security, and platform checks.

## Promotion gate

No component is promoted based solely on stars, upstream claims, installer success, or a green local adapter run. Promotion requires all of: demonstrated gap, immutable source pin, license/security review, minimal fork delta if patched, reproducible tests, privacy/retention review where applicable, existing cadence/dispatch compatibility, strict reference inventory, repository gate, Termux smoke where relevant, and a real task outcome before any Delphi feedback is considered.

## Sources

- [Upstream ACFS repository](https://github.com/Dicklesworthstone/agentic_coding_flywheel_setup)
- [Upstream core loop](https://github.com/Dicklesworthstone/agentic_coding_flywheel_setup/blob/main/docs/methodology/THE_FLYWHEEL_CORE_LOOP.md)
- [Local Flywheel runtime contract](FLYWHEEL-RUNTIME.md)
- [Existing ACFS integration and security gates](DICKLESWORTHSTONE-FLYWHEEL-INTEGRATION.md)
