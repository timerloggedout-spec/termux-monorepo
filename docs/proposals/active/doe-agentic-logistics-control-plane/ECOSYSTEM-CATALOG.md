# LangChain / LangGraph ecosystem catalog

## Source identity and extraction

- Owned catalog fork: timerloggedout-spec/awesome-LangGraph_fork, default branch main.
- README blob SHA: e54d875ae645a03100346e2997acb8cfc43b0a14.
- README size observed: 103,076 characters.
- Markdown link references extracted: 565. This is a raw reference count, not 565 unique projects; it includes repeated docs, badges, API links and project references.
- Related root fork: timerloggedout-spec/langchain_fork, default branch master, README SHA aeea8c38765f4a33c777e8755ac2f439132ffbb0, 5,891 characters.
- Inventory method: source README heading hierarchy, package maps, links and owned repo metadata; no packages were installed and no third-party entry was promoted.

## Framework and official product map

| Catalog area | README scope | Integration role in this program | Initial disposition |
|---|---|---|---|
| LangChain | Agents, models, messages, tools, short/long-term memory, streaming, guardrails, context engineering, structured output, MCP, HITL, multi-agent, retrieval, runtime and middleware. | Component, model/tool/retriever interface and agent composition. | Existing fork is the ecosystem entry; review exact package and provider before use. |
| Core packages | Python and JS/TS packages; core, langchain, community, MCP adapters, text splitters, experimental, CLI and legacy packages are linked. The owned Python fork README also lists core, classic/v1, model-profiles, partners, standard-tests and text-splitters. | Pin compatible interfaces; avoid monolithic installs and deprecated/legacy assumptions. | Package-by-package inventory and version pinning required. |
| LangGraph | Python/JS libraries, CLI, SDKs, quickstarts, interrupts, tests and observability. | Stateful workflow graph, conditional cycles, parallel branches and checkpointed orchestration. | Continue existing BIUDL integration PR #5045; no second runtime. |
| Deep Agents | Planning/task decomposition, context management, subagents, memory, HITL, sandboxes, streaming, skills and CLI. | Higher-level harness when delegated planning/filesystem workflows justify it. | Compare against direct LangGraph patterns; do not run both by default. |
| LangSmith | Deployment, observability, evaluation, prompt engineering, Studio, sandboxes and Agent Server. | Optional trace, evaluation and deployment surface. | Adapter experiment only; canonical evidence remains repo-native/neutral. |
| LangSmith Fleet | No-code agent builder, connected tools, channels, schedules, access and oversight. | Potential management/user-approval surface. | Research only; do not treat as execution authority. |
| Integrations and partners | Provider integrations and partner ecosystem links. | Model, vector-store, retriever, loader and tool connectors. | Every provider needs its own route, license, entitlement, security and quota checks. |

## Official LangGraph project categories in the README

| Category | Extracted linked references | Typical purpose |
|---|---:|---|
| Specialized Agent Libraries | 27 | Prebuilt agent patterns and domain-specific agent abstractions. |
| Apps & Agents | 30 | Runnable application and agent examples. |
| Development Tools | 3 | Developer tooling, CLIs and related build utilities. |

## Community project taxonomy

The README groups community entries into these categories. Reference counts below are raw links in each heading section and may include docs or badges; they are not unique-project counts.

| Category | Linked references | Potential value to this program |
|---|---:|---|
| Bio & Health | 2 | Domain-constrained data workflows; not a priority runtime dependency. |
| Web Automation & Scraping | 6 | Acquisition, browser/tool workflows and source evidence. |
| Business Intelligence & Market Research | 1 | Parallel research and typed synthesis; relate to the RunnableParallel fork. |
| Chat Interfaces & GUIs | 5 | Human-facing interface options; avoid coupling UI to orchestration core. |
| Cloud & DevOps | 1 | Deployment/runtime integrations; review permissions and operational cost. |
| Coding/Dev Agents | 3 | Repository automation and engineering-agent patterns. |
| Customer Ops | 2 | Workflow examples for triage and support. |
| Data Platforms | 3 | Storage and data-service integrations. |
| Data Science | 3 | Analysis, experiment and evaluation tooling. |
| Developer Tools | 28 | Framework, debugging, testing and integration utilities. |
| Packages | 2 | Reusable software components. |
| Finance & Fintech | 7 | Sensitive-domain examples; separate authorization and risk review. |
| Marketing | 0 | Heading present; no linked references found in that section snapshot. |
| Media & Podcasts | 4 | Media ingestion and processing examples. |
| Robotics & Embodied AI | 1 | Potential PDDLStream/task-and-motion planning connection. |
| RAG & Document Processing | 8 | Retrieval, parsing, chunking and document pipelines. |
| Research Agents | 16 | Research/delegation and evidence-synthesis patterns. |
| Cybersecurity | 1 | Security tools; strict threat-model and safety review required. |
| Security & Governance | 4 | Guardrails, permissions and governance references. |
| Sustainability | 0 | Heading present; no linked references found in that section snapshot. |
| Templates & Starters | 6 | Bootstrap patterns; evaluate maintenance before reuse. |
| Workplace & Productivity | 10 | Task/workflow automation examples. |
| Learning Resources / Official LangChain Academy | 14 | Official training and onboarding. |
| Community Courses | 1 | External learning references. |
| Additional Resources | 22 | Talks, tutorials, papers and links. |
| Communities | 2 | Community support and participation. |

## Cross-cutting operating dimensions

The list is best treated as a supply map over the lifecycle rather than a package to install wholesale:

1. Build: core framework, LangGraph, Deep Agents, official libraries, app templates, partner integrations.
2. Observe: LangSmith, OpenTelemetry patterns, traces, state changes, routing decisions, latency and cost attribution.
3. Evaluate: datasets, experiments, graders, replay/benchmark harnesses and independent verification.
4. Deploy: Agent Server, SDKs, CLI, cloud/runtime and sandbox options.
5. Govern: HITL, access/oversight, security, guardrails, policy, provenance and source hygiene.
6. Apply: research, RAG, developer tooling, data platforms, robotics/embodied AI, customer ops and workplace automation.

## Owned companion implementations

| Repository | Observed purpose | Program mapping |
|---|---|---|
| timerloggedout-spec/langchain_fork | LangChain core README + Python package monorepo. Root LICENSE is MIT. | Framework source and provider/package inventory. |
| timerloggedout-spec/awesome-LangGraph_fork | Full ecosystem catalog; root LICENSE is CC0 1.0. | Discovery and taxonomy source; does not change the license of linked projects. |
| timerloggedout-spec/langchain-runnableparallel-company-research_fork | Parallel retrieval, typed Pydantic results and partial-failure preservation; root LICENSE is MIT. | Parallel acquisition and resilient aggregation example. |
| timerloggedout-spec/multi-agent-observability-opentelemetry_fork | LangGraph + OpenTelemetry reference patterns for routing, latency, errors, state, lineage and token-cost attribution. | Observability patterns; root LICENSE file not found despite README badge. |
| timerloggedout-spec/LibreChat_fork | Chat UI/product README; no LangChain or LangGraph terms in inspected README. | Neighboring UI candidate, excluded from the core ecosystem set. |

## Admission and adoption rules

- A link in this README is a discovery signal, not a dependency recommendation.
- Each selected item requires exact upstream, owner, default ref/SHA, maintenance/activity, license, security, transitive dependencies, compatibility and an isolated test.
- Keep provider identity separate from framework identity and configured instance identity.
- Keep graph orchestration separate from durable cross-worker workflow execution.
- Keep trace/evaluation products as adapters over canonical evidence, never as a second source of record.
- Candidates that cannot pass the license or provenance gate remain catalog-only.
- Update this file from source README changes only after review; preserve upstream README as the source of truth and record the extraction SHA.
