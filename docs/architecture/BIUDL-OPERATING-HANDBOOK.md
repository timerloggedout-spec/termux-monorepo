# BIUDL operating handbook

**Status:** navigation and operating contract  
**Repository:** `timerloggedout-spec/termux-monorepo`  
**Updated:** 2026-11-11

This handbook joins the implementation plan with the detailed contracts. It is a navigation layer, not a replacement source of truth.

## Governing architecture

`Foresight → ChronoMancer → HyperForge → Workflow Controls → Admin Web → Admin Graph → independent releases`

Collaborator Management operates concurrently across identity, eligibility, assignment and evaluation. FireSight consumes operational evidence after the event substrate is available and feeds findings back into Foresight.

The loop is iterative: observations and outcomes improve prioritization, context selection, capability choice and subsequent releases.

## Read in this order

1. [Integrated steering and evidence plan](BIUDL-INTEGRATED-STEERING-AND-EVIDENCE-PLAN.md) — system boundaries, event envelope, delivery waves and acceptance.
2. [Control-plane implementation contracts](CONTROL-PLANE-IMPLEMENTATION-CONTRACTS.md) — capability registry, dispatch, authenticated gateway, receipts and graph read model.
3. [Collaborator Management lane contract](../ops/COLLABORATOR-MANAGEMENT-LANE-CONTRACT.md) — identity distinctions, lifecycle, qualification and HyperForge eligibility.
4. [FireSight early-warning contract](../ops/FIRESIGHT-OPERATIONAL-EARLY-WARNING-CONTRACT.md) — detection, finding lifecycle, severity, feedback and non-autonomous boundary.
5. [Independent component releases](../ops/INDEPENDENT-COMPONENT-RELEASES.md) — component release lines, compatibility and ArchW12.9y pinset.
6. [Device-offline hold and continuation](../ops/DEVICE-OFFLINE-WORK-CONTINUATION.md) — device-dependent work boundary and what continues remotely.

## Existing authorities to preserve

| Domain | Existing authority |
|---|---|
| Agent-team operating loop | `docs/architecture/AGENT-TEAM-CONTROL-PLANE.md` |
| Evidence and receipts | `docs/ops/AGENT-EVIDENCE-SUBSTRATE.md` |
| Cross-domain lane/project state | `docs/ops/REPO-TRACKING.md`, `ops/tracking/tracking.json` |
| Open PR disposition policy | `docs/ops/LANE-MATRIX.md` |
| Agent roster and declared adapters | `docs/ops/AGENT-TEAM-ROSTER.md`, `docs/schemas/agent-roster.yaml` |
| Monikers and live triggers | `docs/ops/AGENT-MONIKERS.md` |
| Provider/collaborator capability snapshot | `docs/ops/PROVIDER-COLLABORATOR-CAPABILITY-MAP.md` (dated snapshot; refresh before availability claims) |
| Experiment family and campaign approvals | `docs/ops/DOE-FAMILY.md`, `docs/ops/corpus/EXPERIMENT.schema.json` |
| PR disposition board | `docs/ops/generated/lane-matrix-status.json` |
| Project state | `ops/tracking/tracking.json` |

## Machine-readable contracts

These schemas define payload shape; they do not create a new database or imply that a producer/consumer is implemented:

| Contract | Schema |
|---|---|
| Capability registration | [capability-registration.schema.json](../schemas/capability-registration.schema.json) |
| Collaborator lifecycle projection | [collaborator-lifecycle.schema.json](../schemas/collaborator-lifecycle.schema.json) |
| FireSight finding | [firesight-finding.schema.json](../schemas/firesight-finding.schema.json) |
| Component release manifest | [component-release-manifest.schema.json](../schemas/component-release-manifest.schema.json) |

Producers must validate before emitting. Consumers must reject unknown required versions and preserve unknown optional data only where their contract permits. Schema validation is necessary but does not establish authorization, source authenticity, execution, or correctness.

## Operating principles

- Discover and inspect before changing; use the live repository SHA.
- Keep lane ownership explicit; no competing global registry or state store.
- Preserve immutable source/run/artifact lineage.
- Distinguish proposed, approved, dispatched, committed, executed, validated, promoted and monitored.
- Missing evidence remains missing; it is not a zero, success, or inferred identity.
- A registered integration is not necessarily available or authorized.
- Device hold is scoped; it does not idle unrelated work.
- Never bypass the repository's exact-SHA dual gate, campaign approvals or protected-operation approvals.
- Document every new contract, test boundary, deferred dependency and known limitation alongside its implementation.

## Completion checklist for every lane

- [ ] Canonical owner and source-of-truth boundary identified.
- [ ] Existing implementation and dependencies inspected.
- [ ] Input/output contracts and versioning documented.
- [ ] Security, permissions, secrets and approval boundary documented.
- [ ] Deterministic tests and failure fixtures added.
- [ ] Exact-SHA CI evidence captured.
- [ ] Action/effect and provenance evidence linked.
- [ ] Compatibility and independent release declared.
- [ ] Deferred tests and unavailable environments stated honestly.
- [ ] Explicit promotion authority satisfied.
