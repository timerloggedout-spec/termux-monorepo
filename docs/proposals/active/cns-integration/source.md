# CNS Integration — Source and Evidence Basis

## Repository source of truth

This proposal is based on the inspected `master` tree at commit `939ecc225675541d1ad5b829b427c7ac77ac2642` on 2026-11-20, plus the exact files and active pull requests linked below.

CNS is a repository-wide architectural synthesis. The inspected tree contains the component organs; this proposal establishes their integration contract and status model.

## Canonical architecture sources

- `CLAUDE.md` — FA-ADE posture, BIUDL motion, governance sequence, dual gates, and adaptive wait.
- `docs/architecture/AGENT-TEAM-CONTROL-PLANE.md` — manager, scout, telemetry, review, MoneyBall/3L0, and BIUDL.
- `docs/ops/AGENT-TEAM-ORCHESTRATION.md` — manager/router separation, contributor identity, admission, and execution adapters.
- `docs/ops/CONTEXT-RELATIONSHIP-INDEX.md` — context graph model, edge confidence, context deltas, temporal traversal, and authority.
- `docs/ops/3L0-PLANE.md` — 3L0 scoring authority and separation from MoneyBall.
- `docs/ops/SHE-DASHBOARD-ARCHITECTURE.mmd` — evidence corpus, reducers, snapshots, and read-only presentation.
- `docs/proposals/PROCESS.md` and `docs/proposals/registry.yaml` — proposal lifecycle and active-work registry.

## Active implementation evidence

- [PR #5525 — Brain kernel and MOSAIC](https://github.com/timerloggedout-spec/termux-monorepo/pull/5525): merged Rust kernel and specialist contract.
- [PR #5544 — ORBIT / SHIELD](https://github.com/timerloggedout-spec/termux-monorepo/pull/5544): open draft at assessment; arbitration and context-admission implementation.
- [PR #5637 — Synaptic Bus](https://github.com/timerloggedout-spec/termux-monorepo/pull/5637): open draft at assessment; envelope, registry, compatibility, and receipt adapter.
- [PR #5635 — notation enforcement](https://github.com/timerloggedout-spec/termux-monorepo/pull/5635): open at assessment; notation and style enforcement proposal.
- [PR #5665 — PCDOE-008](https://github.com/timerloggedout-spec/termux-monorepo/pull/5665): open draft at assessment; prioritization policy and shadow implementation.
- [CRG proposal](../context-relationship-graph/MANIFEST.md): canonical relationship graph and Historical Corpus Explorer extension.

## Status discipline

Repository presence proves that an artifact exists. A merged PR proves that its commit entered the branch. A green workflow proves the checks represented by that workflow. A runtime integration claim requires an attributable runtime receipt. This proposal preserves those distinctions.

The registry and map classify each connection as verified, derived, proposed, or unresolved. The CNS health model reports freshness and coverage from canonical records.
