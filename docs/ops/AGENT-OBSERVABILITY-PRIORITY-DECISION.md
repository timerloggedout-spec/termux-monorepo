# Agent Observability Priority Decision

## Decision

The observability stack is reorganized by dependency rather than by product category, while preserving the fact that Docker and Codespaces serve multiple distinct purposes.

**P0 — instrumentation + execution substrate + complexity normalization**

- OpenTelemetry: neutral trace/span transport at the agent invocation boundary.
- Docker: reproducible execution substrate for CI and agent jobs; useful for controlled experiments, isolated tooling, environment fingerprints, and reproducible failure reproduction.
- Complexity scoring: explicit complexity plus the structural fallback is part of the measurement foundation. Tree-sitter is the preferred language-neutral structural expansion.
- ATES Phase A: the pure reducer, event schema, focused tests, and quality verification are already implemented; subsequent phases instrument the runtime around this foundation.

**P1 — parallel evaluation and reproduction surfaces**

- Langfuse: optional experiment/evaluation adapter over canonical JSONL/OTEL evidence.
- Phoenix: parallel open-source experiment/evaluation adapter, with Docker as one possible reproducible lab substrate.
- Lizard: fast multi-language CCN/NLOC/token/parameter feature provider.
- Radon: Python-specific CCN/Halstead/maintainability feature provider.
- Codespaces: interactive development/reproduction/sandbox surface. It can host exploratory agent work, debugging, operator reproduction, and environment experiments; it is not merely a Docker-parity mirror and is not the canonical evidence store.

**P2 — comparative research**

- Multi-agent benchmark suites / MASEval: manager-tournament research input after the evidence and complexity foundations are stable.
- Vendor-specific Langfuse/Phoenix persistence/UX remains adapter-level and never becomes the canonical corpus.

## Docker vs Codespaces

Docker and Codespaces belong in the same **Environment Experimentation** family because both can reproduce a declared environment, but they are deliberately **not collapsed into a single purpose**:

- **Docker:** automation substrate, deterministic CI execution, isolated provider/tool experiments, image-level reproducibility, and environment-fingerprint capture.
- **Codespaces:** interactive sandbox, human/agent development surface, debugging, exploratory workflows, and reproduction of issues that benefit from a full workspace.
- **Shared contract:** image/devcontainer/toolchain versions and environment fingerprints should be comparable where useful.
- **Non-equivalence:** a Codespaces sandbox is not required to be Docker's production twin, and Docker execution does not replace the interactive sandbox.

## Experimental rule

All providers consume the same bounded cohort and canonical event contract. Compare evidence quality, decision quality, validation, realization, attribution confidence, retries, conflicts, human intervention, operational cost, and variance. Time-to-integration and wait latency are performance dimensions only.

ATES is an observation inside this quality-first frame, not the objective function by itself.

## Phase cadence

### Phase A — measure **[IMPLEMENTED]**

Pure ATES/WTCV reducer, sanitized event schema, focused fixtures, missing-evidence invariants, structural complexity fallback, and a visible Actions quality check. No external telemetry dependency.

### Phase B — emit

Teach eligible agent workflows to emit sanitized JSONL and publish a receipt alongside existing Action artifacts. Add immutable run/attempt/SHA linkage and environment fingerprints where available.

### Phase C — correlate

Join execution events to GitHub run attempts, SHAs, PRs, Action→Effect events, and corpus observations. Re-run the PR review/evidence cycle over comparable cohorts with ATES attached as an observational layer.

### Phase D — parallelize/reproduce

Run equivalent telemetry through Langfuse and Phoenix adapters, and use Docker/Codespaces for distinct reproduction/experiment purposes. Compare completeness, decision quality, cost, privacy surface, and variance.

### Phase E — compete

Manager tournament using complexity-adjusted quality/effectiveness measures rather than isolated speed or model leaderboard scores.

## Review layering rule

The repository review remains authoritative. The ATES layer is additive:

`REVIEW → CHECKS → ACTION→EFFECT → ATES/WTCV → LONGITUDINAL RECORD`

A later Phase C review may show that a policy was faster but less effective, or slower but more reliably validated. That distinction is the intended use of ATES.

## Non-goals

- no speed-only merge gate;
- no vendor becomes source of truth;
- no synthetic zeroes for missing telemetry or complexity;
- no secrets/PATs in images, workspaces, telemetry, or artifacts;
- no automatic rerun merely to obtain a green dashboard;
- no assumption that Docker and Codespaces are interchangeable environments.
