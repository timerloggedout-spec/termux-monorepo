# CNS Health Model

**Status:** Proposed read-only composite model, version 1  
**Owner:** CNS architecture; each organ owns its underlying measurements.

## 1. Health dimensions

| Dimension | Measurement | Canonical evidence |
|---|---|---|
| Identity integrity | Coverage and validity of task/attempt/actor/provider/model/adapter/run/artifact joins | Native task, orchestration, invocation, and run records |
| Knowledge coverage | Indexed sources, parser coverage, unresolved references, excluded paths | CRG manifest and scope registry |
| Evidence freshness | Age of manifests, feeds, snapshots, and runtime observations | Source timestamps and immutable snapshot metadata |
| Interface integrity | Contract compatibility and verified handoffs | Schemas, adapter tests, exact-head CI |
| Execution health | Admission, dispatch, invocation, completion, failure, and deferral counts | Queue, workflow, and execution receipts |
| Attribution confidence | Share of observations with attributable actor/provider/model/adapter | 3L0 intake and contributor provenance |
| Learning effectiveness | Repeated confirmed outcomes and measured policy improvement | 3L0, MoneyBall, DoE/MVT |
| Governance integrity | Proposal state, permission boundaries, required gate evidence | Proposal registry, branch protection, gate runs |
| Presentation integrity | Snapshot provenance, freshness, source consistency, and accessible fallback | SHE snapshots and Explorer validation |

## 2. Status vocabulary

- `HEALTHY` — required source evidence is present, current, and passes its contract.
- `DEGRADED` — a required source reports a failing or materially impaired state.
- `PARTIAL` — coverage is explicitly incomplete while the available evidence remains usable.
- `STALE` — freshness exceeds the owning source's declared threshold.
- `BLOCKED` — a required dependency or permission gate prevents progress.
- `UNVERIFIED` — evidence is absent, contradictory, or insufficient for classification.

These states describe projections. Native component states remain authoritative.

## 3. Classification rules

1. Every dimension includes `status`, `observed_at`, `source_ref`, `source_sha` where applicable, and `coverage`.
2. The projection preserves the native status and derives a CNS status through a versioned reducer.
3. The reducer exposes the reason and evidence for every derived state.
4. Missing data produces `UNVERIFIED`; it never defaults to `HEALTHY`.
5. Partial corpus coverage remains `PARTIAL` even when all available records validate.
6. A queued or in-progress workflow remains pending until its native terminal event arrives.
7. Workflow success and task outcome remain separate dimensions.
8. A stale source remains visible as stale until a fresh observation replaces it.

## 4. Composite view

The operator overview presents all dimensions together. A single weighted health score is deferred until the repository has validated comparable denominators, freshness thresholds, and outcome coverage. Status and evidence remain inspectable by organ.

## 5. Snapshot contract

Every SHE CNS snapshot carries:

- `schema_version`
- `snapshot_id`
- `generated_at`
- `source_sha`
- `source_manifest_refs`
- `coverage`
- `organ_statuses`
- `unresolved_findings`
- `reducer_version`

Snapshots are immutable projections. Reconciliation creates a new snapshot and preserves the previous one.

## 6. Acceptance tests

- Missing feed → `UNVERIFIED`.
- Old feed beyond configured freshness → `STALE`.
- Partial CRG manifest → `PARTIAL`.
- Failed required gate → `DEGRADED` or `BLOCKED`, with source evidence.
- Pending workflow → pending native status, not terminal success.
- Green workflow with unknown task outcome → workflow healthy, outcome unverified.
- Snapshot with mismatched source SHA → presentation integrity degraded.
- Snapshot without provenance → presentation integrity unverified.
