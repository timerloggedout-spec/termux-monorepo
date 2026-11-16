# Agent Stack Integration — 2026-10-01

## Purpose

Wire the current foresight candidates into the existing FOSS/evidence architecture without creating vendor-specific canonical dependencies.

The machine-readable binding is `config/agent_stack_integrations.json`.

## Integration order

OpenTelemetry → canonical execution/admission evidence → MCP admission + Action→Effect → manager simulation/live cohorts → review + ATES/WTCV → provenance/procurement/radar.

## OpenTelemetry — canonical telemetry boundary

OpenTelemetry remains the neutral observation boundary. Repository-owned JSONL/receipts remain canonical; OTLP is an interoperable export path. Development-status GenAI/MCP semantic conventions remain adapter inputs, not the frozen core schema.

**Status:** H0 / confirmed / ADOPT boundary.

## WSO2 Agent Manager — control-plane adapter

WSO2 Agent Manager is an open-source control plane covering agent lifecycle, identity/security, governance, observability, MCP/A2A interoperability, and OpenTelemetry-based instrumentation.

**Status:** H1 / confirmed / INVESTIGATE.

Integration is adapter-only: ingest identity/lifecycle observations; bind policy decisions to canonical evidence; export trace/span identifiers; preserve deployment/version metadata; compare against the same canonical cohorts used by other adapters.

WSO2 persistence, UI, Kubernetes/OpenChoreo, or SaaS capabilities must not become the evidence system of record.

Primary source: https://github.com/wso2/agent-manager — pinned release `v1.0.0` for this integration record.

## NVIDIA OpenShell — enforceable agent-runtime boundary

NVIDIA's Open Agent Safety Platform combines OpenShell open-source runtime controls with a Sentry reference system. OpenShell is the software-layer research candidate; Sentry/BlueField-4 remains optional hardware research, never a monorepo prerequisite.

**Status:** H1 / confirmed / INVESTIGATE.

Prototype the evidence boundary: agent → runtime admission → policy decision → tool/network/filesystem action → OpenTelemetry span → Action→Effect receipt.

Required evidence includes policy identity/version, decision, agent identity, permitted boundary, tool invocation linkage, and policy-bundle hash.

Primary sources: https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Launches-Open-Agent-Safety-Platform-to-Secure-Agents-From-Testing-to-Deployment/ and https://www.nvidia.com/en-us/ai/openshell/.

## OrchBench — manager preflight

OrchBench evaluates orchestration plans through deterministic simulation using task DAGs, context limits, agent budgets, and controlled information transfers. Its reported correlation is a research result from a tested cohort, not a universal performance guarantee.

**Status:** H1 / research / INVESTIGATE.

Wire it before expensive live manager tournaments: task contract + cohort → manager policy hash → simulation → quality/makespan/token-cost evidence → live execution for selected cohorts → ATES/WTCV/final acceptance.

Simulation and live evidence remain separately attributable.

Primary source: https://arxiv.org/abs/2607.25656.

## NIST IR 8536 — provenance policy mapping

NIST IR 8536 is a finalized September 2026 public framework for interoperable supply-chain traceability, including provenance, secure digital links, and selective disclosure. It is a policy/reference input, not an automatic compliance claim.

**Status:** H0 / confirmed / PROTOTYPE.

Map resource identity, source/version/commit, artifact hash, build environment, runtime/model identity, benchmark cohort, agent/action provenance, and selective-disclosure boundaries.

Primary source: https://csrc.nist.gov/pubs/ir/8536/final.

## llama.cpp + Vulkan — documented, gated, not active

Upstream publishes Android arm64 CPU artifacts and Linux arm64/x86_64 Vulkan artifacts. Current device/resource constraints mean Vulkan is **not admitted to active routing**.

**Status:** H1 / confirmed capability / HOLD.

Future admission requires device Vulkan capability, memory headroom, stable driver/backend behavior, pinned runtime/model hashes, reproducible build, thermal stability, energy-per-completed-task evidence, offline behavior, and an exportable JSONL receipt.

Upstream availability is not device suitability. The Android CPU path remains the simpler bounded baseline.

Primary source: https://github.com/ggml-org/llama.cpp/releases.

## Needle — candidate before Vulkan escalation

The repository already identifies `cactus-compute/needle` as a tiny-device foundation-model candidate for the `01_Agent_Runtime` research lane.

**Status:** H1 / early signal / INVESTIGATE.

Evaluate artifact/build/runtime viability first: Android/Termux buildability, peak memory, latency, structured output, tool-call reliability, offline behavior, energy proxy, and provenance receipt.

No active route changes by this record.

Primary source: https://github.com/cactus-compute/needle.

## Procurement posture

| Candidate | State | Integration role |
|---|---|---|
| OpenTelemetry | ADOPT boundary | neutral telemetry |
| WSO2 Agent Manager | INVESTIGATE | optional open control-plane adapter |
| NVIDIA OpenShell | INVESTIGATE | runtime security reference |
| OrchBench | INVESTIGATE | deterministic manager preflight |
| NIST IR 8536 | PROTOTYPE | provenance policy/reference model |
| llama.cpp Android CPU | PROTOTYPE | bounded local inference baseline |
| llama.cpp Vulkan | HOLD | future accelerator/backend lane |
| Needle | INVESTIGATE | constrained-device candidate |

These states describe repository integration status; they are not universal product rankings.

## Failure taxonomy

Do not collapse model, provider, manager/orchestration, tool, runtime-policy, environment, device/backend, provenance/evidence, and admission/routing failures. Failed or unavailable experiments remain evidence.

## Operational loop

`RECON → PLAN/MEASURE → ACT → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD → REPEAT`

No queued/in-progress state is success. No automatic rerun exists merely to obtain green status.

## Next bounded experiments

1. WSO2: export one bounded agent cohort into canonical OTEL/JSONL evidence.
2. OpenShell: run a non-destructive sandbox/policy experiment and capture admission/effect linkage.
3. OrchBench: translate one existing manager-tournament cohort into a deterministic DAG and compare simulated vs live evidence.
4. NIST: map one evidence receipt end-to-end to provenance/pedigree fields.
5. Needle: evaluate artifact/build/runtime viability before Vulkan.
6. llama.cpp Vulkan: remain HOLD until device capability and resource gates are satisfied.

No active production routing changes are introduced by this integration record.