# Agent Observability Priority Decision

## Decision

The observability stack is reorganized by dependency rather than by product category.

**P0 — instrumentation + execution substrate + complexity normalization**

- OpenTelemetry: neutral trace/span transport at the agent invocation boundary.
- Docker: reproducible execution substrate for CI and agent jobs; captures environment fingerprints and enables parity experiments.
- Complexity scoring: explicit complexity plus the structural fallback is part of the measurement foundation. Tree-sitter is the preferred language-neutral structural expansion.

**P1 — parallel evaluation providers**

- Langfuse: optional experiment/evaluation adapter over canonical JSONL/OTEL evidence.
- Phoenix: parallel open-source experiment/evaluation adapter, with Docker as its reproducible lab substrate.
- Lizard: fast multi-language CCN/NLOC/token/parameter feature provider.
- Radon: Python-specific CCN/Halstead/maintainability feature provider.
- Codespaces: interactive reproduction lane built on the same environment contract and devcontainer, primarily for operator/agent reproduction rather than canonical execution.

**P2 — comparative research**

- Multi-agent benchmark suites / MASEval: manager-tournament research input after the evidence and complexity foundations are stable.
- Vendor-specific Langfuse/Phoenix persistence/UX remains adapter-level and never becomes the canonical corpus.

## Consolidation rule

Docker and Codespaces are one **Environment Parity** track, but they are not the same implementation:

`Docker = reproducible execution substrate`

`Codespaces = interactive reproduction surface`

The P0/P1 distinction is therefore dependency-driven: Docker moves earlier because P0 agent instrumentation needs a reproducible execution substrate; Codespaces remains P1 because it is principally an interactive reproduction surface.

Complexity also moves earlier because ATES/TCV/WTCV comparisons become more meaningful when task difficulty is normalized. The reducer must preserve raw provider features, provider/version, derived score, and confidence; missing complexity is never silently converted to zero.

## Experimental rule

All providers consume the same bounded cohort and canonical event contract. Compare evidence quality, decision quality, validation, realization, attribution confidence, retries, conflicts, human intervention, operational cost, and variance. Time-to-integration and wait latency are performance dimensions only.

## Phase cadence

### Phase A — instrument

OpenTelemetry-compatible lifecycle events, runtime watcher, immutable SHA/run linkage, and environment fingerprint.

### Phase B — normalize

Complexity providers: explicit score, structural fallback, Tree-sitter, Lizard, Radon.

### Phase C — parallelize

Equivalent GitHub-only, Langfuse, and Phoenix evaluation lanes over the same cohort.

### Phase D — reproduce

Docker and Codespaces environment-parity experiments; classify environment failures separately from model/provider failures.

### Phase E — compete

Manager tournament using complexity-adjusted quality/effectiveness measures rather than isolated speed or model leaderboard scores.

## Non-goals

- no speed-only merge gate;
- no vendor becomes source of truth;
- no synthetic zeroes for missing telemetry or complexity;
- no secrets/PATs in images, workspaces, telemetry, or artifacts;
- no automatic rerun merely to obtain a green dashboard.
