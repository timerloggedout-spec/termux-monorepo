# Briefing Integration Upgrade — 2026-09-29

## Purpose
Convert the 2026-09-29 morning briefing into repository-owned, provenance-preserving research/procurement/evaluation contracts without duplicating the existing OpenTelemetry, ATES, complexity, MCP, provenance, or manager-orchestration systems.

## Integrated upgrades

| Briefing signal | Monorepo integration |
|---|---|
| MCP / agent interoperability | MCP admission evidence contract: server/version, tool-schema hash, declared capabilities, authorization mode, delegation depth, policy decision, request/response hashes |
| OpenTelemetry | remains the P0 neutral transport; MCP admission records can be projected into OTEL without making OTEL the source of truth |
| Reproducible environments | manager and edge experiments require task-contract + environment fingerprints |
| AST / complexity | existing complexity-provider contract remains canonical; Tree-sitter/Lizard/Radon stay feature providers |
| Evaluation infrastructure | manager tournament cohort schema makes identical-cohort comparisons explicit and replayable |
| Local / edge / ARM / Android | edge inference evidence records ABI, model hash, quantization, runtime/backend, latency, memory, thermal and energy proxy, offline state, and fallback |
| FOSS runtimes / open weights | procurement records preserve source/version/provenance and tested platform targets; no provider becomes a permanent route |
| Agentic security | MCP admission is deny-by-default research/prototype evidence, not implicit trust |
| Provenance / supply chain | NIST IR 8536 and SLSA/Sigstore remain policy/provenance inputs; runtime evidence joins the execution provenance graph |
| Compute / memory / energy / accelerators | edge schema provides the measurement substrate; accelerator research remains H1/H2 until reproducible local evidence exists |
| Manager tournaments | deterministic simulation/benchmark research is an input to local tournaments, never a universal model-quality score |

## Evidence rules
- Preserve canonical source URL and observation date.
- Pin release/commit when available; use null or VERIFY rather than inventing a version.
- Keep research findings distinct from confirmed implementation facts.
- Preserve missing measurements as null.
- Do not treat a benchmark score as universal model quality.
- Do not treat a tool-definition score as runtime correctness.
- Do not put credentials, prompts, completions, or sensitive tool payloads into telemetry artifacts.
- Promotion remains an explicit operator/policy decision.

## Research anchors
- OrchBench: https://arxiv.org/abs/2607.25656
- NIST IR 8536: https://csrc.nist.gov/pubs/ir/8536/final
- OpenTelemetry: https://opentelemetry.io/
- MCP: https://github.com/modelcontextprotocol
- llama.cpp: https://github.com/ggml-org/llama.cpp
- SLSA: https://slsa.dev/
- Sigstore: https://www.sigstore.dev/

## Next bounded experiments
1. Run two or more manager policies against the same pinned task cohort.
2. Add MCP admission receipts to the same execution/evidence corpus.
3. Capture one ARM64/Android local-inference baseline with a pinned model/runtime.
4. Compare environment fingerprints between Docker and the existing Codespaces surface.
5. Evaluate evidence completeness through the existing Langfuse/Phoenix adapters without moving canonicality to either system.