# Laya Runtime / CADENCE Operating Plan

Status: implementation on feat/system-one-experiment-lanes
Priority: P0 operational runtime, P1 comparative sweeps, P2 native classifier work.

## Runtime topology

| Plane | Role | Runtime |
|---|---|---|
| Termux | operator/orchestration hub | gh workflow dispatch + local mock |
| GitHub Actions | canonical automated live smoke | Laya 0.3.5, Python 3.12 |
| GitHub Environment | secret boundary | laya-live |
| Hugging Face | model/weight source | pulled by pinned Laya package |
| Colab | GPU/large-memory benchmark | live category sweep |
| Render | persistent bounded HTTP adapter | /healthz + /decide |
| Vercel | control/observation surface | no model residency |

## Laya operating modes

1. PR mode: dependency-free mock and receipt-contract tests.
2. Live mode: pinned Laya package, real Router inference, model cache, artifact receipts.
3. CADENCE mode: scheduled category sweep producing comparable cohorts.
4. Termux mode: dispatch live/cadence/jev workflows through gh; local execution remains an explicit mock unless the device has a compatible ML stack.
5. Render mode: long-lived HTTP decision endpoint for applications that need a resident process.
6. Colab mode: GPU benchmark and large-memory experiments.

## Category expansion

The adapter catalog is intentionally category-oriented rather than provider-oriented:

- routing
- security
- agent
- code
- ops
- general

New engines implement the same DecisionRequest -> DecisionResponse contract and declare supported categories. Adding an engine does not grant provider, shell, branch, merge, or secret authority.

## Jev API block

The optional Jev adapter targets TypeSafe's System One API:

- POST /v1/systemone
- GET /v1/models remains a future discovery action
- request: model, state, questions
- authentication: TYPESAFE_API_KEY as a GitHub Environment secret
- question families: noul, choice, score
- absent key: UNAVAILABLE, not model failure
- configured but transport/API error: ENGINE_ERROR

The live Jev workflow is manual by design so credentials and service access are never implied.

## CADENCE

Default automated cadence:

- Laya live smoke: every 6 hours.
- Laya category sweep: daily.
- Jev live adapter: manual until credentials and service policy are explicitly configured.
- PR contract checks: every relevant change.

## Receipt requirements

Every sweep receipt records:

- schema version
- case/category
- mode and engine
- latency
- routing metadata
- answers/confidence
- runtime fingerprint
- cohort identity

Correctness evidence remains separate from latency. Missing evidence is null rather than zero.

## Comparative optimization loop

Build -> Run -> Watch -> Measure -> Diagnose -> Refactor -> Compete -> Cull -> retain/reject -> repeat.

A candidate policy can be promoted only after matched cohorts, regression evidence, provenance, and explicit review. No live workflow mutates repository code, provider routing, credentials, or merge state automatically.

## Next implementation steps

1. Obtain terminal CI evidence for this branch.
2. Configure the laya-live GitHub Environment only if the deployment needs credentials.
3. Execute the first live Actions smoke and retain its artifact.
4. Execute two or more CADENCE cohorts and compare raw receipts.
5. Add labeled task fixtures for correctness/calibration rather than relying on latency alone.
6. Add Laya/LLM cascade and M0-M4 manager tournament execution over the same cohort.
7. Enable the Jev workflow after an API key is explicitly configured.
8. Benchmark Colab GPU and Render resident-service latency separately.
9. Add the Vercel observation/control surface after the receipt schema stabilizes.
10. Promote only evidence-backed routing changes.
