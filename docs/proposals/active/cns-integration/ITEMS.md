# ITEMS — CNS Integration Programme

| ID | Work | Priority | Owner | Status | GitHub issue | Acceptance evidence |
|---|---|---:|---|---|---:|---|
| CNS-01 | Establish the canonical CNS organ registry. | P0 | ChatGPT | executing | [#5688](https://github.com/timerloggedout-spec/termux-monorepo/issues/5688) | Versioned registry validates; each organ records canonical source, owner, interfaces, status, provenance, and authority boundary. |
| CNS-02 | Publish the CNS integration map. | P0 | ChatGPT | executing | [#5689](https://github.com/timerloggedout-spec/termux-monorepo/issues/5689) | Mermaid renders; every edge carries verified, derived, proposed, or unresolved classification. |
| CNS-03 | Reconcile CRG historical corpus coverage and lineage. | P0 | ChatGPT | executing | [#5690](https://github.com/timerloggedout-spec/termux-monorepo/issues/5690) | Fresh manifest, coverage receipt, parser and reference reconciliation, checkpoint decision. |
| CNS-04 | Define shared CNS identity and receipt mapping. | P0 | ChatGPT | executing | [#5691](https://github.com/timerloggedout-spec/termux-monorepo/issues/5691) | One task traces across available lifecycle stages with exact source identifiers and explicit unknowns. |
| CNS-05 | Publish the CNS authority matrix. | P0 | ChatGPT | executing | [#5692](https://github.com/timerloggedout-spec/termux-monorepo/issues/5692) | Every state mutation maps to one canonical owner, interface, and permission boundary. |
| CNS-06 | Integrate the Brain kernel through its canonical host. | P1 | ChatGPT | todo | [#5693](https://github.com/timerloggedout-spec/termux-monorepo/issues/5693) | Host integration test proves typed reasoning-to-handoff with policy delegation and attributable receipt. |
| CNS-07 | Complete Synaptic Bus v1 interoperability. | P1 | ChatGPT | executing | [#5694](https://github.com/timerloggedout-spec/termux-monorepo/issues/5694) | Versioned envelope, idempotent adapters, compatibility tests, and canonical record resolution. |
| CNS-08 | Integrate ORBIT and SHIELD in observe-only mode. | P1 | ChatGPT | executing | [#5695](https://github.com/timerloggedout-spec/termux-monorepo/issues/5695) | Invocation-boundary observations with exact-head tests and unchanged production routing. |
| CNS-09 | Reconcile 3L0 intake attribution and feed freshness. | P1 | ChatGPT | executing | [#5696](https://github.com/timerloggedout-spec/termux-monorepo/issues/5696) | Repeated confirmed dispatch outcomes with actor/provider/model/instance attribution. |
| CNS-10 | Measure orchestration policies through controlled DoE/MVT. | P1 | ChatGPT | executing | [#5697](https://github.com/timerloggedout-spec/termux-monorepo/issues/5697) | Reproducible cohorts, predeclared metrics, immutable treatment identity, attributable outcomes. |
| CNS-11 | Enforce cross-platform single-writer coordination. | P1 | ChatGPT | todo | [#5698](https://github.com/timerloggedout-spec/termux-monorepo/issues/5698) | Lease and concurrency tests prove one active corrective writer per repository/PR/revision. |
| CNS-12 | Build the read-only SHE CNS overview. | P2 | ChatGPT | todo | [#5699](https://github.com/timerloggedout-spec/termux-monorepo/issues/5699) | Provenance-bound overview displays status, freshness, coverage, execution, learning, and attention. |
| CNS-13 | Complete Historical Corpus Explorer deployment. | P2 | ChatGPT | executing | [#5700](https://github.com/timerloggedout-spec/termux-monorepo/issues/5700) | Accessible deployed read-only projection with validated lineage and truthful partial-state display. |
| CNS-14 | Consolidate the adaptive wait-loop skill. | P2 | ChatGPT | executing | [#5701](https://github.com/timerloggedout-spec/termux-monorepo/issues/5701) | One canonical loop skill with explicit evidence, terminal states, scope, and verification. |
| CNS-15 | Reconcile Jules skills and GitHub workflows. | P2 | ChatGPT | executing | [#5702](https://github.com/timerloggedout-spec/termux-monorepo/issues/5702) | Tested trigger/action contracts, reproducible setup, secure prompt intake, attributable invocation evidence. |
| CNS-16 | Complete notation registry enforcement. | P2 | ChatGPT | executing | [#5703](https://github.com/timerloggedout-spec/termux-monorepo/issues/5703) | Registry-backed lint and CI checks with documented exceptions and fixture coverage. |

## Programme rules

1. Existing organ owners retain canonical state and mutation authority.
2. CNS registry, map, health, and dashboard surfaces are projections and coordination contracts.
3. Each implementation PR cites `Implements: CNS-<id>`.
4. Runtime evidence binds to exact source SHA, run identity, attempt, and artifact.
5. Proposed integrations remain labeled proposed until exact-head validation and runtime evidence establish them.
6. The repository's proposal lifecycle, repo gate, Termux smoke, and permission boundaries apply to every item.


## Current integration state

- CNS-01, CNS-02, CNS-04, CNS-05, and CNS-14 have an initial implementation in [PR #5709](https://github.com/timerloggedout-spec/termux-monorepo/pull/5709); exact-head CI and review remain pending.
- CNS-03 uses the existing operator-controlled CRG backfill workflow. The trusted Jules issue lane has been requested; the backfill dispatch itself remains an operator workflow action.
- CNS-06 follows the existing MOSAIC/Brain proposal and is gated by the parked QDesk RFP #5501 and its fresh owner admission.
- CNS-07 follows open draft PR #5637. CNS-08 follows open draft PR #5544.
- CNS-09 reuses the 41-record append-only 3L0 intake; all 41 outcomes are unconfirmed and the committed feed is stale.
- CNS-10 consumes the existing DoE/MVT plane, PR #5531, and PCDOE-008 PR #5708.
- CNS-11 has a documented enforcement gap: internal workflow serialization and external provider write enforcement require separate evidence.
- CNS-12 reuses SHE/Tribute dashboard reducers and snapshots; current feeds require freshness reconciliation.
- CNS-13 extends the existing CRG-15 Explorer implementation through publication and deployment.
- CNS-15 adds the Jules integration reconciliation artifact; exact-head tests and a live invocation receipt remain pending.
- CNS-16 consumes the notation enforcement work in PR #5635.
