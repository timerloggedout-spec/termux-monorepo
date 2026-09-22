# System One Decision Experiment Lanes

**Status:** implementation seed / observe-first
**Priority:** P0 experimental instrumentation, P1 active routing only after evidence

## Purpose

Extend the existing Laya decision-engine lane into a controlled System One / System Two experiment plane for termux-monorepo.

The objective is to measure whether bounded decision engines reduce latency, context consumption, duplicate work, escalation cost, and integration failures while preserving correctness. The experiment plane is separate from provider execution:

state -> System One decision -> manager policy -> specialist/provider -> evidence

## Existing implementation anchors

- scripts/decision_engines.py is the registry for System-1/schema decision engines.
- scripts/laya_decision_stub.py provides a CI-safe Laya-shaped offline contract and an optional live adapter.
- scripts/model_router.py remains the provider execution router; its AR-18 capability spine is observe-mode.
- docs/ops/AGENT-TEAM-ORCHESTRATION.md defines manager tournaments and evidence-based culling.
- refTemplates/16_Org_Phased/laya/IMPLEMENTATION.md keeps Laya in IMPLEMENTATION rather than metadata-only status.

## Experiment lanes

| Lane | Decision engine | Role | Execution authority |
|---|---|---|---|
| A | deterministic baseline | control | none |
| B | Laya | local System One | none |
| C | Jev adapter | external System One, when configured | none |
| D | Laya/LLM cascade | System One gate + existing provider route | existing router only |
| E | no-gate | System Two baseline | existing router only |

Jev is an adapter slot, not an availability claim. If credentials/API access are absent, the lane records UNAVAILABLE and is not scored as a model failure.

## Parallel development builds

A manager experiment is a policy, not a model:

- M0-control: no System One gate.
- M1-fast-gate: bounded System One choice/score, escalate on uncertainty.
- M2-parallel-triage: run independent triage decisions concurrently, then integrate once.
- M3-evidence-gate: require decision evidence before expensive execution.
- M4-adaptive: select among M0-M3 using only prior cohort evidence.

Each manager gets a unique policy_version. Parallel lanes must use the same task cohort, task seed, repository SHA, and acceptance criteria.

## Metrics

Record raw measurements before deriving scores: decision latency, execution latency, end-to-end latency, requests/invocations, token counts when exposed, context bytes when available, escalation count, duplicate-work count, retry count, human intervention, task outcome, integration outcome, decision confidence, calibration error when ground truth exists, attribution confidence, provider/model availability, and environment fingerprint.

Derived metrics may include TCV/WTCV/RPI/ATES, but raw observations remain canonical. Latency never upgrades an incorrect result. Missing evidence is null, not zero.

## Self-directed improvement experiment

1. Freeze objective and cohort.
2. Generate manager candidates from a small declared policy set.
3. Run candidates independently.
4. Collect raw receipts.
5. Compare on predeclared metrics.
6. Identify failure classes and wasted work.
7. Generate the next policy generation by changing only declared policy parameters.
8. Rerun on a fresh cohort.
9. Retain both winning and rejected policies with reasons.
10. Require human promotion before active routing changes.

No recursive self-modification, arbitrary prompt mutation, secret mutation, or automatic merge is permitted.

## Promotion gates

A System One lane can move from observe-only to active routing only after two or more comparable cohorts, deterministic regression coverage, calibrated confidence or an explicit uncalibrated state, no unexplained correctness regression, evidence of reduced cost/latency or improved integration quality, attribution/provenance receipts, current-SHA validation, and an explicit ledger decision.

## Environment matrix

Termux/Android is the priority orchestration hub. Additional execution planes are local Linux/macOS, Colab, GitHub Actions, Render, Vercel, and later GCP/AWS/Azure. Environment is recorded as an observation dimension and is never silently conflated with model performance.

## Failure taxonomy

Use explicit classes: ENGINE_UNAVAILABLE, ENGINE_ERROR, BAD_DECISION_SCHEMA, LOW_CONFIDENCE, ROUTING_ERROR, PROVIDER_ERROR, ORCHESTRATION_ERROR, CODE_ERROR, ENVIRONMENT_ERROR, NETWORK_ERROR, CORRECTNESS_FAILURE.

A failed experiment is retained as evidence. It is not automatically retried merely to obtain a green dashboard.

## Implementation order

P0: normalized decision envelope, deterministic control lane, Laya adapter/stub, manager tournament harness, JSONL evidence, calibration/quality fixtures, offline operation.

P1: LangChain adapter boundary, Jev API adapter when legitimately configured, local Laya benchmark, Android/Termux latency and memory telemetry, dashboard ingestion.

P2: Colab burst runner, Render/Vercel service adapters, cloud execution matrix, native C++ inference experiments.
