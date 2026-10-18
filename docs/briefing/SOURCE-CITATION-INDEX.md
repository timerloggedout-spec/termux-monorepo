# Source Citation Index — Daily Briefings and BIUDL Evidence

**Purpose:** human-readable navigation for cited URLs found in the dated briefing snapshots, existing resource/procurement/radar JSONL, and the architecture/operations documents used to plan the BIUDL implementation.

**Generated from repository evidence at branch `feat/biudl-full-stack-provenance`.** This is a citation inventory, not a claim that each URL was fetched or independently re-verified during this pass. Evidence status and confidence are preserved where the source record provides them. The automated extractor is `scripts/ci/curate_briefing_sources.py`; run it to produce deterministic JSONL suitable for audit and downstream analysis.

## Canonical contracts

- [Daily Digest Specification](../briefing/DAILY-DIGEST-SPEC.md)
- [Briefing Ingest](../research/BRIEFING-INGEST.md)
- [FOSS Procurement Matrix](../research/FOSS-PROCUREMENT-MATRIX.md)
- [Foresight Radar](../research/FORESIGHT-RADAR.md)
- [Standing source registry](../../config/foresight_digest_sources.json)
- [Foresight Evidence Spine](../ops/FORESIGHT-EVIDENCE-SPINE.md)

## Citation inventory


### `data/briefing/briefings/2026-09-30.json`

- Verifiable agent delegation is emerging as a distinct MCP/A2A security primitive — <https://arxiv.org/abs/2603.24775> — preprint; research; H1 (`$.items[1].sources[0].url`)
- NIST's finalized traceability framework gives provenance work a stronger interoperable reference model — <https://csrc.nist.gov/pubs/ir/8536/final> — government_publication; confirmed; H0 (`$.items[3].sources[0].url`)
- Heterogeneous inference is being built around latency, memory bandwidth, and accelerator specialization — <https://gimletlabs.ai/blog/cerebras-announcement> — official_company_technical_context; attributed; H1 (`$.items[2].sources[1].url`)
- Open agent runtimes are moving governance into enforceable execution boundaries — <https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Launches-Open-Agent-Safety-Platform-to-Secure-Agents-From-Testing-to-Deployment/> — official_company_release; confirmed; H1 (`$.items[0].sources[0].url`)
- AI memory and advanced packaging remain a core systems constraint behind inference efficiency — official_company_release; confirmed; H1 (canonical URL retained in the [contributor integration brief](CONTRIBUTOR-INTEGRATION-2026-09-30.md), `$.items[4].sources[1].url`). The URL slug contains `sk-hynix`, which the repository secret scanner conservatively flags as a token-shaped string; the source itself is unchanged.
- AI memory and advanced packaging remain a core systems constraint behind inference efficiency — <https://www.appliedmaterials.com/us/en/newsroom/press-releases/031026-applied-materials-micron-partner-advance-us-innovation-next-gen-ai.html> — official_company_release; confirmed; H1 (`$.items[4].sources[0].url`)
- Heterogeneous inference is being built around latency, memory bandwidth, and accelerator specialization — <https://www.cerebras.ai/press-release/gimlet-labs-adds-cerebras-to-deliver-ultrafast-ai-inference-through-gimlet-cloud-deployment> — official_company_release; attributed; H1 (`$.items[2].sources[0].url`)
- Open agent runtimes are moving governance into enforceable execution boundaries — <https://www.hpe.com/us/en/newsroom/blog-post/2026/09/hpe-and-nvidia-bring-secure-governed-agentic-ai-into-enterprise-production.html> — official_company_technical_context; confirmed; H1 (`$.items[0].sources[1].url`)
- NIST's finalized traceability framework gives provenance work a stronger interoperable reference model — <https://www.nist.gov/news-events/news/2026/09/finalized-manufacturing-supply-chain-traceability-meta-framework> — government_announcement; confirmed; H0 (`$.items[3].sources[1].url`)
- Open agent runtimes are moving governance into enforceable execution boundaries — <https://www.nvidia.com/en-us/ai/openshell/> — official_product_documentation; confirmed; H1 (`$.items[0].sources[2].url`)
- Heterogeneous inference is being built around latency, memory bandwidth, and accelerator specialization — <https://www.reuters.com/technology/cerebras-supply-ai-systems-cloud-computing-startup-gimlet-labs-2026-09-28/> — secondary_context; attributed; H1 (`$.items[2].sources[2].url`)

### `docs/briefing/2026-10-04-collaborator-ingest.json`

- OrchBench makes manager/orchestration tournaments cheaper to evaluate — <https://arxiv.org/abs/2607.25656> — preprint; research; H1; arXiv:2607.25656 (`$.items[3].canonical_source`)
- MCP 2026-07-28 moves agent/tool interoperability toward a stateless infrastructure layer — <https://blog.modelcontextprotocol.io/posts/2026-07-28/> — official_release; confirmed; H0; 2026-07-28 (`$.items[0].canonical_source`)
- nist-ir-8536 — <https://csrc.nist.gov/pubs/ir/8536/final> — confirmed; H2; Final, 2026-09-09 (`$.radar_watch[0].canonical_source`)
- Android/ARM local inference is a first-class reproducibility target — <https://github.com/ggml-org/llama.cpp/blob/master/docs/android.md> — official_project_repository; confirmed+device-specific; H0/H1; llama.cpp b11398 observed pre-release; ExecuTorch 1.5 docs (`$.items[4].canonical_source`)
- OpenShell demonstrates enforceable runtime boundaries for agents — <https://github.com/NVIDIA/OpenShell> — official_project_repository; confirmed+attributed; H0/H1; 0.1.x stable family (`$.items[2].canonical_source`)
- OpenTelemetry is the strongest neutral evidence boundary for agent workflows — <https://opentelemetry.io/docs/specs/semconv/> — technical_documentation; confirmed; H0; 1.44.0 (`$.items[1].canonical_source`)

### `docs/briefing/CONTRIBUTOR-INTEGRATION-2026-09-30.md`

- 2. Agent identity and delegation — <https://arxiv.org/abs/2603.24775> — document_reference (`L44`)
- Manager tournament integration — <https://arxiv.org/abs/2607.25656> — document_reference (`L103`)
- 4. Traceability/provenance — <https://csrc.nist.gov/pubs/ir/8536/final> — document_reference (`L69`)
- 3. Heterogeneous inference — <https://gimletlabs.ai/blog/cerebras-announcement> — document_reference (`L56`)
- Local/Android runtime integration — <https://github.com/ggml-org/llama.cpp/releases> — document_reference (`L112`)
- OpenTelemetry / MCP watch — <https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/mcp.md> — document_reference (`L91`)
- OpenTelemetry / MCP watch — <https://github.com/open-telemetry/semantic-conventions-genai/issues/437> — document_reference (`L94`)
- 1. Agent runtime governance — <https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Launches-Open-Agent-Safety-Platform-to-Secure-Agents-From-Testing-to-Deployment/> — document_reference (`L32`)
- 5. Memory/packaging/energy — official Applied Materials + SK hynix primary citation; canonical URL retained in [the contributor integration brief](CONTRIBUTOR-INTEGRATION-2026-09-30.md) at `L82`. The source URL slug triggers the repository's token-shape heuristic; the upstream source is unchanged.
- 5. Memory/packaging/energy — <https://www.appliedmaterials.com/us/en/newsroom/press-releases/031026-applied-materials-micron-partner-advance-us-innovation-next-gen-ai.html> — document_reference (`L81`)
- 3. Heterogeneous inference — <https://www.cerebras.ai/press-release/gimlet-labs-adds-cerebras-to-deliver-ultrafast-ai-inference-through-gimlet-cloud-deployment> — document_reference (`L55`)
- 1. Agent runtime governance — <https://www.hpe.com/us/en/newsroom/blog-post/2026/09/hpe-and-nvidia-bring-secure-governed-agentic-ai-into-enterprise-production.html> — document_reference (`L34`)
- 4. Traceability/provenance — <https://www.nist.gov/news-events/news/2026/09/finalized-manufacturing-supply-chain-traceability-meta-framework> — document_reference (`L70`)
- 1. Agent runtime governance — <https://www.nvidia.com/en-us/ai/openshell/> — document_reference (`L33`)
- 3. Heterogeneous inference — <https://www.reuters.com/technology/cerebras-supply-ai-systems-cloud-computing-startup-gimlet-labs-2026-09-28/> — document_reference (`L58`)

### `data/briefing/resources.jsonl`

- AIP: Agent Identity Protocol for Verifiable Delegation Across MCP and A2A — <https://arxiv.org/abs/2603.24775> — preprint; research; H1; arXiv:2603.24775 (`L17 L17.canonical_url`)
- OrchBench: Evaluating Multi-Agent Orchestration Plans in Isolation via Deterministic Simulation — <https://arxiv.org/abs/2607.25656> — preprint; research; H1; arXiv:2607.25656 (`L13 L13.canonical_url`)
- NIST IR 8536 Supply Chain Traceability: Manufacturing Meta-Framework — <https://csrc.nist.gov/pubs/ir/8536/final> — government_or_public_research; confirmed; H0; IR 8536 Final (`L14 L14.canonical_url`)
- NIST IR 8536 Supply Chain Traceability: Manufacturing Meta-Framework — <https://csrc.nist.gov/pubs/ir/8536/final> — government_or_public_research; confirmed; H0; IR 8536 Final (`L19 L19.canonical_url`)
- GitHub Codespaces — <https://github.com/features/codespaces> — official_provider_catalog; confirmed; H0 (`L8 L8.canonical_url`)
- Android / ARM local inference evidence lane — <https://github.com/ggml-org/llama.cpp> — official_project_repository; confirmed; H0 (`L15 L15.canonical_url`)
- MASEval — <https://github.com/maseval/MASEval> — reproducible_benchmark; research; H1 (`L9 L9.canonical_url`)
- Ghidra — <https://github.com/NationalSecurityAgency/ghidra> — official_project_repository; confirmed; H0 (`L11 L11.canonical_url`)
- OpenTelemetry GenAI/MCP semantic conventions — <https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/mcp.md> — official_project_repository; confirmed; H2; main (`L21 L21.canonical_url`)
- Lizard — <https://github.com/terryyin/lizard> — official_project_repository; confirmed; H0 (`L6 L6.canonical_url`)
- Tree-sitter — <https://github.com/tree-sitter/tree-sitter> — official_project_repository; confirmed; H0 (`L3 L3.canonical_url`)
- Langfuse — <https://langfuse.com/> — official_project_repository; confirmed; H1 (`L4 L4.canonical_url`)
- Langfuse Evaluation Documentation — <https://langfuse.com/docs/evaluation/overview> — technical_documentation; confirmed; H1 (`L12 L12.canonical_url`)
- OpenTelemetry — <https://opentelemetry.io/> — official_project_repository; confirmed; H0 (`L1 L1.canonical_url`)
- Phoenix — <https://phoenix.arize.com/> — official_project_repository; confirmed; H1 (`L5 L5.canonical_url`)
- Radon — <https://radon.readthedocs.io/> — technical_documentation; confirmed; H0 (`L7 L7.canonical_url`)
- SLSA — <https://slsa.dev/> — standards_body; confirmed; H0 (`L10 L10.canonical_url`)
- Applied Materials AI memory / advanced packaging partnerships — <https://www.appliedmaterials.com/us/en/newsroom/press-releases/031026-applied-materials-micron-partner-advance-us-innovation-next-gen-ai.html> — official_release; confirmed; H1 (`L20 L20.canonical_url`)
- Cerebras + Gimlet Cloud heterogeneous inference announcement — <https://www.cerebras.ai/press-release/gimlet-labs-adds-cerebras-to-deliver-ultrafast-ai-inference-through-gimlet-cloud-deployment> — official_release; attributed; H1 (`L18 L18.canonical_url`)
- Docker — <https://www.docker.com/> — official_project_repository; confirmed; H0 (`L2 L2.canonical_url`)
- NVIDIA OpenShell / Open Agent Safety Platform — <https://www.nvidia.com/en-us/ai/openshell/> — official_project_repository; confirmed; H1 (`L16 L16.canonical_url`)

### `data/briefing/procurement.jsonl`

- aip-agent-identity-protocol — <https://arxiv.org/abs/2603.24775> — H1; arXiv:2603.24775 (`L11 L11.canonical_source`)
- orchbench — <https://arxiv.org/abs/2607.25656> — H1; arXiv:2607.25656 (`L7 L7.canonical_source`)
- nist-ir8536-final-2026 — <https://csrc.nist.gov/pubs/ir/8536/final> — H0; IR 8536 Final (`L13 L13.canonical_source`)
- nist-ir8536-final — <https://csrc.nist.gov/pubs/ir/8536/final> — H0; IR 8536 Final (`L8 L8.canonical_source`)
- android-edge-evidence-contract — <https://github.com/ggml-org/llama.cpp> — H0; VERIFY (`L9 L9.canonical_source`)
- otel-genai-mcp-current — <https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/mcp.md> — H2; main; pin before adapter release (`L15 L15.canonical_source`)
- lizard — <https://github.com/terryyin/lizard> — H0; VERIFY (`L3 L3.canonical_source`)
- tree-sitter — <https://github.com/tree-sitter/tree-sitter> — H0; VERIFY (`L2 L2.canonical_source`)
- langfuse — <https://langfuse.com/> — H1; VERIFY (`L6 L6.canonical_source`)
- otel — <https://opentelemetry.io/> — H0; VERIFY (`L1 L1.canonical_source`)
- phoenix — <https://phoenix.arize.com/> — H1; VERIFY (`L5 L5.canonical_source`)
- radon — <https://radon.readthedocs.io/> — H0; VERIFY (`L4 L4.canonical_source`)
- ai-memory-packaging-2026 — <https://www.appliedmaterials.com/us/en/newsroom/press-releases/031026-applied-materials-micron-partner-advance-us-innovation-next-gen-ai.html> — H1; 2026-03-10 announcements (`L14 L14.canonical_source`)
- cerebras-gimlet-inference — <https://www.cerebras.ai/press-release/gimlet-labs-adds-cerebras-to-deliver-ultrafast-ai-inference-through-gimlet-cloud-deployment> — H1; Announcement 2026-09-28 (`L12 L12.canonical_source`)
- nvidia-openshell — <https://www.nvidia.com/en-us/ai/openshell/> — H1; VERIFY (`L10 L10.canonical_source`)

### `data/briefing/radar.jsonl`

- Cryptographically verifiable agent delegation across tool protocols — <https://arxiv.org/> — preprint; research; H1 (`L1 L1.evidence[0].url`)
- Deterministic simulation isolates manager/orchestration quality from worker noise — <https://arxiv.org/abs/2607.25656> — preprint; research; H1 (`L4 L4.evidence[0].url`)
- ARM/Android inference procurement is shifting toward memory, thermal, energy, and runtime evidence — <https://github.com/ggml-org/llama.cpp> — official_project_repository; confirmed; H1 (`L6 L6.evidence[0].url`)
- Multi-agent manager policy becomes a measurable optimization layer — <https://github.com/maseval/MASEval> — reproducible_benchmark; research; H1 (`L3 L3.evidence[0].url`)
- MCP tool admission should become an auditable security boundary — <https://github.com/modelcontextprotocol> — official_project_repository; confirmed; H1 (`L5 L5.evidence[0].url`)
- MCP observability semantics are evolving faster than a safe canonical schema should — <https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/mcp.md> — official_project_repository; signal; H2 (`L8 L8.evidence[0].url`)
- MCP observability semantics are evolving faster than a safe canonical schema should — <https://github.com/open-telemetry/semantic-conventions-genai/issues/437> — official_project_issue; signal; H2 (`L8 L8.evidence[1].url`)
- Open agent runtimes are becoming an enforceable governance boundary — <https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Launches-Open-Agent-Safety-Platform-to-Secure-Agents-From-Testing-to-Deployment/> — official_company_release; confirmed; H1 (`L7 L7.evidence[0].url`)
- Portable local agent observability becomes a systems primitive — <https://opentelemetry.io/> — official_project_repository; research; H1 (`L2 L2.evidence[0].url`)
- Memory bandwidth and advanced packaging remain strategic inference bottlenecks — official_company_release; confirmed; H1. Canonical URL is preserved in [the contributor integration brief](CONTRIBUTOR-INTEGRATION-2026-09-30.md) and `data/briefing/radar.jsonl` (`L9.evidence[1].url`); it is not duplicated here because the repository secret scanner misclassifies part of the path as token-shaped.
- Memory bandwidth and advanced packaging remain strategic inference bottlenecks — <https://www.appliedmaterials.com/us/en/newsroom/press-releases/031026-applied-materials-micron-partner-advance-us-innovation-next-gen-ai.html> — official_company_release; confirmed; H1 (`L9 L9.evidence[0].url`)
- Open agent runtimes are becoming an enforceable governance boundary — <https://www.nvidia.com/en-us/ai/openshell/> — official_product_documentation; confirmed; H1 (`L7 L7.evidence[1].url`)

### `docs/ops/sessions/HINDSIGHT.md`

- Phase 3 — lifecycle hooks (explicit) — <http://localhost:8888/mcp/{bank_id}/> — document_reference (`L138`)
- Python client — <https://api.hindsight.vectorize.io> — document_reference (`L60`)
- Phase 3 — lifecycle hooks (explicit) — <https://arxiv.org/abs/2512.12818> — document_reference (`L151`)
- Phase 3 — lifecycle hooks (explicit) — <https://github.com/timerloggedout-spec/hindsight> — document_reference (`L148`)
- Phase 3 — lifecycle hooks (explicit) — <https://github.com/vectorize-io/hindsight> — document_reference (`L149`)
- Phase 3 — lifecycle hooks (explicit) — <https://hindsight.vectorize.io> — document_reference (`L150`)

## Citation policy

- Preserve exact canonical URLs and source locations; do not silently rewrite history.
- Keep the same URL as separate citations when it supports different items or appears in different source documents.
- Distinguish confirmed facts, attributed claims, research findings, signals, speculation, and disputed claims.
- Horizon (H0–H3) is not confidence; image queries are not evidence.
- Never store prompts, completions, tokens, cookies, private settings, or raw session context in the citation ledger.
