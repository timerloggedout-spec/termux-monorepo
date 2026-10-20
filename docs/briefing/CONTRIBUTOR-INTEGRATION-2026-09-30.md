# Contributor Integration Brief — 2026-09-30

## Purpose

This document records the 2026-09-30 morning foresight pass as an evidence-backed integration package for contributors. It does **not** replace the repository contracts; it binds the day's evidence to the existing implementation lanes.

## Canonical contracts

Read these before changing the briefing/evidence system:

1. `docs/briefing/DAILY-DIGEST-SPEC.md` — five-item selection and item contract.
2. `docs/research/BRIEFING-INGEST.md` — provenance, evidence-status, version/date, confidence, and item fields.
3. `docs/research/FOSS-PROCUREMENT-MATRIX.md` — inspectable procurement dimensions and decision states.
4. `docs/research/FORESIGHT-RADAR.md` — H0/H1/H2/H3 semantics.
5. `config/foresight_digest_sources.json` — standing source families and lane registry.
6. `docs/ops/FORESIGHT-EVIDENCE-SPINE.md` — canonical JSONL evidence boundary.
7. `docs/ops/FOSS-FORESIGHT-PROGRAM.md` — research/procurement architecture.
8. `docs/ops/AGENT-OBSERVABILITY-PRIORITY-DECISION.md` — P0/P1/P2 observability ordering.
9. `docs/research/LANE-ARCHITECTURE.md` and `docs/research/RESEARCH-LANES.yaml` — lane/org separation and ingestion boundary.

The repository's current design already treats OpenTelemetry as the neutral telemetry boundary, MCP as an interoperability contract, Docker as reproducible execution substrate, Codespaces as an interactive reproduction surface, complexity tools as measurement providers, and hosted evaluation products as adapters rather than canonical stores.

## Evidence inserted by this pass

### 1. Agent runtime governance

NVIDIA's 2026-09-28 announcement describes OpenShell as open-source runtime software that creates an enforceable boundary around agent execution, with policy and audit controls. HPE describes OpenShell integration into HPE Private Cloud AI.

**Integration:** `agentic-security`, `agent-observability`, MCP admission, sandbox policy.

**Primary citations:**
- NVIDIA: https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Launches-Open-Agent-Safety-Platform-to-Secure-Agents-From-Testing-to-Deployment/
- OpenShell: https://www.nvidia.com/en-us/ai/openshell/
- HPE: https://www.hpe.com/us/en/newsroom/blog-post/2026/09/hpe-and-nvidia-bring-secure-governed-agentic-ai-into-enterprise-production.html

**Contributor rule:** do not treat OpenShell as a new canonical dependency. Evaluate its policy/evidence boundary against the monorepo contract.

### 2. Agent identity and delegation

The AIP preprint proposes invocation-bound capability tokens across MCP/A2A/HTTP and reports experimental results for delegation and audit resistance.

**Integration:** `mcp-admission-security`, provenance, authorization, agent identity.

**Primary research citation:** https://arxiv.org/abs/2603.24775

**Contributor rule:** preserve the evidence status as `research`; do not convert the paper's server scan or security results into an ecosystem-wide fact without replication.

### 3. Heterogeneous inference

Cerebras and Gimlet announced a 2026-09-28 partnership for heterogeneous inference infrastructure. Their announced throughput figures are attributed company claims.

**Integration:** `local-edge-arm-android`, `edge-inference-evidence`, manager routing, accelerator/materials/energy.

**Primary citations:**
- Cerebras: https://www.cerebras.ai/press-release/gimlet-labs-adds-cerebras-to-deliver-ultrafast-ai-inference-through-gimlet-cloud-deployment
- Gimlet: https://gimletlabs.ai/blog/cerebras-announcement

**Secondary context:** Reuters: https://www.reuters.com/technology/cerebras-supply-ai-systems-cloud-computing-startup-gimlet-labs-2026-09-28/

**Contributor rule:** benchmark useful task completion, not advertised token rate alone.

### 4. Traceability/provenance

NIST IR 8536 was finalized 2026-09-09 and describes interoperable traceability, cryptographic linkage, provenance chains, and selective disclosure.

**Integration:** `provenance-supply-chain`, Foresight Evidence Spine, SBOM/AIBOM, benchmark/model/runtime provenance.

**Primary citations:**
- NIST IR 8536: https://csrc.nist.gov/pubs/ir/8536/final
- NIST announcement: https://www.nist.gov/news-events/news/2026/09/finalized-manufacturing-supply-chain-traceability-meta-framework

**Contributor rule:** treat the report as a reference model; separately track the implementation state.

### 5. Memory/packaging/energy

Applied Materials announced collaborations with Micron and SK hynix around next-generation DRAM/HBM/NAND and advanced packaging for AI.

**Integration:** `accelerators-materials-energy`, `edge-inference-evidence`, procurement matrix.

**Primary citations:**
- Applied Materials + Micron: https://www.appliedmaterials.com/us/en/newsroom/press-releases/031026-applied-materials-micron-partner-advance-us-innovation-next-gen-ai.html
- Applied Materials + SK hynix: https://www.appliedmaterials.com/us/en/newsroom/press-releases/031026-applied-materials-and-sk-hynix-announce-long-term-rd-partnership.html

**Contributor rule:** separate vendor roadmap statements from measured device/runtime evidence.

## OpenTelemetry / MCP watch

The current OpenTelemetry GenAI/MCP semantic conventions are explicitly marked **Development**. The current MCP convention document includes tool-call arguments/results as opt-in fields and warns that they may contain sensitive information.

Primary source:
https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/mcp.md

An upstream issue also documents the need to make conventions version-aware as MCP evolves:
https://github.com/open-telemetry/semantic-conventions-genai/issues/437

**Action:** keep the monorepo canonical event schema closed and privacy-aware. Treat upstream GenAI/MCP conventions as an adapter contract until stability is demonstrated.

## Manager tournament integration

OrchBench is directly relevant to the manager-tournament lane. Its July 2026 preprint evaluates orchestration plans through deterministic simulation and reports strong correlation with a tested Claude Code cohort while using substantially fewer tokens/time than live execution.

Primary research source:
https://arxiv.org/abs/2607.25656

**Action:** use deterministic simulation as a preflight research lane; preserve task DAG, manager-policy hash, budget, and cohort identity so simulation evidence cannot be confused with live execution evidence.

## Local/Android runtime integration

The current `llama.cpp` release surface includes Android arm64 CPU builds and Snapdragon-specific Android arm64 builds.

Primary source:
https://github.com/ggml-org/llama.cpp/releases

**Action:** keep `android-edge-evidence-contract` focused on pinned runtime/model hashes, device ABI, memory/thermal/energy observations, and portable JSONL receipts.

## FOSS procurement posture

The existing procurement matrix remains the decision-support record. No aggregate vendor score is introduced by this pass.

Recommended states arising from the evidence:

| Resource / lane | State | Rationale |
|---|---|---|
| OpenTelemetry core | ADOPT boundary / continue adapter validation | Neutral telemetry interoperability |
| OpenTelemetry GenAI/MCP conventions | HOLD / adapter-only | Development status and protocol evolution |
| OpenShell-class runtime controls | INVESTIGATE | Concrete open-source governance reference; portability still needs validation |
| AIP-style delegation | INVESTIGATE | Research result; replication/standardization unresolved |
| OrchBench | INVESTIGATE | Deterministic manager-policy research input |
| llama.cpp Android/ARM | PROTOTYPE | Concrete local inference baseline with published Android artifacts |
| NIST IR 8536 | PROTOTYPE as policy reference | Strong provenance/traceability model; software mapping remains to be designed |
| HBM/advanced-packaging evidence | WATCH / procurement input | Infrastructure constraint, not a software dependency |

These are **descriptive integration states**, not universal rankings.

## Contributor validation loop

Use the repository's existing loop:

`RECON → PLAN/MEASURE → ACT → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD → REPEAT`

Do not interpret queued/in-progress as success. Do not rerun failures merely to obtain green status. Preserve cancellation and admission/routing failures as evidence.

For agent evidence, maintain the existing separation:

`REVIEW → CHECKS → ACTION→EFFECT → ATES/WTCV → LONGITUDINAL RECORD`

ATES is an observation layer; it does not replace correctness or review evidence.

## Files added/updated by this evidence pass

- `data/briefing/briefings/2026-09-30.json`
- `docs/briefing/CONTRIBUTOR-INTEGRATION-2026-09-30.md`
- `data/briefing/resources.jsonl` — append today's primary-source observations
- `data/briefing/procurement.jsonl` — append inspectable procurement records
- `data/briefing/radar.jsonl` — append/update material H1/H2 signals

The dated briefing is a snapshot; the JSONL registries are append-oriented evidence stores. Corrections must append a newer observation rather than overwrite history.

## Provenance

Observation date: 2026-09-30. Primary web evidence was checked during preparation. Web discovery is not itself canonical repository evidence until the cited URL/version/date is recorded in the repository registry.

No secrets, credentials, private tokens, or provider account material belong in these records.
