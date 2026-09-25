# Evidence Projection Surface (EPS)

**Status:** telemetry-first implementation contract  
**Priority:** P0 telemetry / P2 visualization  
**Scope:** repository-wide evidence production, normalization, projection, and downstream analysis

## Purpose

EPS is the repository's **telemetry-first projection contract**. It turns independently verifiable repository events into small, immutable, provenance-bound records that can be consumed by analytics, ML, Hex, Grafana, agentic orchestration, and later visualization surfaces.

EPS is **not** a second source of truth, database, scheduler, provider router, or merge authority.

The authority chain remains:

`GitHub / Git / Actions / artifacts → EPS event → validated evidence bundle → reducers / ML / Hex / Grafana / visualization`

If a projection conflicts with source evidence, regenerate the projection.

## First implementation gap

The existing production ledger is a useful read-only evidence producer, but the current implementation writes a human-readable job summary and does not emit the previously planned agent-throughput JSONL receipt. The repository's own audit identified this gap: the throughput schema was a contract rather than a runtime emitter.

EPS closes that gap incrementally without requiring every agent workflow to be rewritten at once.

### Phase 1 producer

`.github/workflows/pr-production-ledger.yml` emits an EPS NDJSON artifact for each applicable PR event.

### Phase 2 producers

`.github/workflows/agent-throughput-evidence.yml` now observes the explicitly admitted Gemini/Jules/DeepSeek agent workflows and emits sanitized ATES JSONL plus reducer/receipt artifacts. The existing Hex Moneyball grain contracts become EPS-compatible consumers rather than a parallel telemetry format.

The observer is read-only and source-independent: it does not checkout or execute the triggering SHA. Structural complexity is attached only when exactly one associated PR supplies concrete additions/deletions/files-changed evidence.

## Envelope

Every EPS record should carry:

- `schema_version`
- `event_id` — deterministic/idempotent identity
- `event_type`
- `occurred_at`
- `source`
- `repo`
- `git_sha` when known
- `run_id` / `run_attempt` when Actions-backed
- `entity_id` and `entity_type`
- `status`
- `provenance`
- bounded `attributes`

No prompts, completions, tool payloads, credentials, arbitrary comments, or repository contents belong in EPS.

## Provenance rule

An EPS record is useful only if a reviewer can navigate back to source evidence. Prefer:

`run → job → step → event → PR/issue → SHA → artifact`

Unknown values remain unknown. Do not manufacture timestamps, attribution, success, causality, or zero-valued metrics.

## Downstream lanes

| Consumer | Role | EPS boundary |
|---|---|---|
| Agentic orchestration | routing/manager evidence | consumes validated records; does not rewrite source evidence |
| ML / Moneyball | cohorting, regression, anomaly detection | derived metrics only |
| Hex | analytical/evidence presentation | read-only consumer; not system of record |
| Grafana | operational telemetry/alerts | operational projection; no write authority |
| Context Relationship Graph | relationship/provenance projection | metadata-only; no causal inference |
| Gource | temporal repository visualization | renderer/projection consumer, never canonical telemetry |
| Vercel/SHE | interactive evidence surface | presentation/query layer |
| future Web/WASM visualization | custom interaction | secondary lane after telemetry contracts stabilize |

## Required downstream distinction

**Telemetry first:** capture and validate evidence before optimizing dashboards or interaction design.

**Visualization second:** visualization may reveal anomalies and aid exploration, but findings must resolve to EPS/source evidence.

## Idempotency

Consumers must deduplicate by `event_id`. Replays of the same source observation must not inflate counts.

Actions with the same GitHub `run_id` but different `run_attempt` are distinct execution attempts.

## Evaluation

EPS success is evaluated by:

1. source-to-event coverage;
2. provenance completeness;
3. idempotent replay behavior;
4. freshness;
5. schema validity;
6. attribution-confidence correctness;
7. reducer reproducibility;
8. downstream agreement across Hex/Grafana/ML;
9. ability to reconstruct a source event from its evidence identifiers.

Visualization utility is evaluated separately and never substitutes for telemetry completeness.
