# Competitive Orchestration Lab — LangGraph BIUDL

## Purpose

Compare orchestration approaches as replaceable treatments, then combine independently validated patterns. The lab is not a framework popularity contest and does not authorize a production routing change by itself.

## Treatment portfolio

| Treatment | Primary hypothesis | Strengths to test | Failure modes / costs |
|---|---|---|---|
| Native manager (control) | Existing policy and adapters provide the best baseline | Lowest integration cost, current governance, existing receipts | Routing complexity, hidden coupling, weak graph introspection |
| LangGraph | Explicit graph state and transitions improve complex workflows | Branching, fan-out, checkpointing, interrupt/resume, subgraphs | Dependency/runtime footprint, state leakage, checkpoint complexity |
| Deep Agents | Higher-level harness reduces agent-loop implementation effort | Planning, filesystem context, subagents, skills, memory | Excess abstraction, token/cost overhead, reduced control |
| Swarm / handoff | Peer or specialist handoffs improve parallel expertise | Specialization, delegation, task decomposition | Coordination overhead, loops, ownership ambiguity |
| Supervisor / tool-routed | Central supervisor improves task allocation | Central policy, tool routing, bounded delegation | Bottleneck, supervisor bias, archived package risk |
| Microsoft Agent Framework | Unified agent + workflow primitives reduce multi-framework glue | Graph/functional workflows, sequential/concurrent/handoff/group-chat/Magentic patterns, middleware, sessions, HITL | New platform surface, SDK maturity differs by language, overlap with native manager/Temporal |
| OpenAI Agents SDK | A small agent-loop abstraction accelerates specialist delegation | Agent loop, handoffs, guardrails, sessions, tool integration, built-in tracing | Provider/runtime coupling, trace privacy and retention constraints, graph-level control may require another layer |
| Google ADK | Workflow agents provide deterministic multi-agent composition | Sequential/parallel/loop agents, graph workflows, multi-language SDKs | Ecosystem/provider fit, SDK parity and runtime footprint require verification |
| LlamaIndex Workflows | Event-driven typed steps simplify data/research pipelines | Typed events, async steps, concurrency, validation, streaming, human input and durable-workflow examples | Event bookkeeping, async requirements, integration with non-LlamaIndex retrieval/tool stack |
| CrewAI | Role-based crews plus Flows simplify specialist team composition | Crews, start/listen/router, state, persistence/resume, guardrails and HITL | Role/agent overhead, hidden orchestration cost, external service dependencies to audit |
| PydanticAI | Typed agent APIs plus pluggable durability simplify reliable Python agents | Typed dependencies/output, tool integration, OTEL instrumentation, Temporal/DBOS/Prefect/Restate durability | One durable engine per agent; overlap with existing Temporal; replay/idempotency and provider costs to validate |
| Hybrid | Best-fit components outperform any single treatment | Graph control + native policy + specialized harness + durable execution | Integration complexity, duplicate state, unclear authority |

Candidate rows describe patterns, not endorsements. Archived packages remain reference-only; candidate frameworks must pass current maintenance, license, security, and dependency review before execution.


## Expanded ecosystem candidates (official-source recon)

These candidates extend the original Awesome LangGraph shortlist. They are separate treatments, not dependencies to install together.

| Candidate | Source-backed capability | Initial disposition / test question |
|---|---|---|
| [Microsoft Agent Framework](https://learn.microsoft.com/agent-framework/overview) | Combines agents, harness agents, integrations, and functional/graph workflows. Workflow docs describe sequential, concurrent, handoff, group-chat, and Magentic patterns, plus HITL and checkpoint/resume. | **High-priority comparison.** Test graph execution, multi-agent patterns, observability, language parity, and how cleanly it composes with the existing manager. Its Go SDK is public preview; Python functional workflows are experimental in current docs. |
| [OpenAI Agents SDK](https://developers.openai.com/api/docs/guides/agents/sdk) | Agent loop, handoffs, guardrails, sessions, tool integration, and run tracing. Human review can pause execution before sensitive side effects. | **High-priority thin-runtime comparison.** Test specialist delegation, approval gates, guardrail coverage, trace export controls, and portability. Built-in tracing has a ZDR availability limitation; treat its traces as a source, not canonical project evidence. |
| [Google ADK](https://google.github.io/adk-docs/) | Agent and workflow-agent primitives, including SequentialAgent, ParallelAgent, LoopAgent, and graph-based workflows. | **High-priority portability comparison.** Test multi-language support, graph control, provider neutrality, deterministic routing, and integration cost. |
| [LlamaIndex Workflows](https://developers.llamaindex.ai/python/llamaagents/workflows/) | Event-driven typed steps, async execution, branching/loops/concurrency, workflow validation, streaming, human-input examples, and durable-workflow examples. | **Research/data-lane candidate.** Test evidence collection, document-heavy research, typed event contracts, and interop with the repository's existing retrieval/tool stack. |
| [CrewAI](https://docs.crewai.com/) | Role-based crews and event-driven Flows with state, persistence/resume, guardrails, and human-in-the-loop triggers. | **Specialist-team candidate.** Test role decomposition and Flow control against native team orchestration; measure agent overhead, duplication, and hidden coordination cost. |
| [PydanticAI](https://ai.pydantic.dev/) | Typed agent framework with OpenTelemetry instrumentation and durable execution integrations for Temporal, DBOS, Prefect, Restate, and other engines. | **High-priority Python / Temporal comparison.** Test whether typed contracts and durable wrappers add value without introducing a second durable engine. Docs specify one durable execution engine per agent; don't layer it over an already-durable graph run without a clear boundary. |
| [Microsoft AutoGen](https://github.com/microsoft/autogen) | Historical multi-agent conversation and orchestration patterns. | **Archived / reference-only.** Microsoft says the repository is no longer maintained and directs new users to Microsoft Agent Framework. Do not start new production adoption from AutoGen. |

### Source-selection notes

- Microsoft Agent Framework explicitly combines agent, harness, and workflow capabilities; its docs recommend using ordinary functions before introducing agents and using workflows when execution order must be explicit.
- OpenAI Agents SDK exposes built-in tracing for agent, generation, tool, guardrail, and handoff spans. Tracing can be disabled or redirected, but the documentation notes tracing is unavailable for organizations using API access under Zero Data Retention.
- Google ADK documents deterministic workflow-agent types and multi-agent workflow composition; validate language feature parity rather than assuming all SDKs are identical.
- LlamaIndex Workflows validates event producer/consumer relationships before execution and uses typed events to describe step edges. Its Python API is async-first.
- CrewAI documents Flows as stateful event-driven orchestration around Crews, with persistence/resume and human-review capabilities.
- PydanticAI documents durable execution through multiple workflow engines and explicitly distinguishes crash recovery from run persistence/resume. Its "one durable engine per agent" constraint is especially relevant to this repository's Temporal boundary.

## Benchmark corpus

Use the same immutable task fixtures and acceptance tests across treatments. Start with a small, representative set:

1. **Deterministic tool workflow:** typed inputs, bounded tool call, structured result.
2. **Branching triage:** classify evidence, select a lane, route to a deterministic verifier.
3. **Parallel research:** independent source collection, deduplication, synthesis, citation checks.
4. **Human approval:** pause before a consequential side effect, resume on the same run identity, prove idempotency.
5. **Long-running recovery:** simulate worker interruption, resume from a checkpoint or durable workflow, verify no duplicate effect.
6. **Repository change:** inspect, plan, patch, run tests, produce evidence, stop before merge.
7. **Adversarial input:** prompt injection, malformed tool output, permission escalation attempt, data-exfiltration bait.

Every task has a fixed fixture, expected artifacts, deterministic verifier, side-effect budget, timeout, and explicit stop condition. Never use production secrets or uncontrolled external side effects in the benchmark corpus.

## Measurement contract

Record run-level measurements through existing orchestration treatment and receipt contracts. Use existing OTEL/ATES only where event semantics match. Do not encode graph nodes as tools or put prompts, completions, tool arguments, checkpoint blobs, or private state into telemetry.

Minimum measures:

- **Quality:** verifier pass rate, requirement coverage, factual/citation accuracy where applicable.
- **Reliability:** completion rate, retry rate, recovery success, duplicate-side-effect count.
- **Efficiency:** wall-clock time, model/tool calls, token usage, compute/runtime cost.
- **Governance:** policy violations, approval bypasses, unauthorized effects, evidence completeness.
- **Operability:** setup burden, dependency footprint, observability coverage, reproducibility.
- **Maintainability:** code surface, failure localization, upgrade burden, operator comprehension.

Report distributions and confidence intervals where sample size permits; never rank on one aggregate score alone. Hard safety or governance failures disqualify a treatment regardless of speed or quality score.

## Experiment protocol

1. Freeze task corpus, verifier versions, model/provider configuration, tool permissions, resource budgets, and source SHA.
2. Define one treatment variable at a time; keep all other conditions equivalent.
3. Run baseline and candidate on the same fixtures. Randomize execution order where practical.
4. Repeat enough runs to expose variance; report sample size and missing runs.
5. Separate deterministic harness failures from model variance and external-service failures.
6. Preserve sanitized run receipts, source/config hashes, verifier output, and failure classifications.
7. Review failures blind to framework where practical; record the evidence and reviewer rationale.
8. Repeat after each material improvement; compare against both the prior candidate and native control.

No promotion from a single successful demo. Do not compare treatments with different task difficulty, permissions, model budgets, or acceptance criteria.

## Pattern extraction and recombination

After each comparison, classify patterns as:

- **Keep:** independently validated improvement with no material regression.
- **Adapt:** promising concept requiring a repository-native implementation or stronger boundary.
- **Combine:** two or more validated patterns with compatible state/authority boundaries.
- **Defer:** insufficient evidence, incomplete test coverage, or unresolved dependency/security risk.
- **Reject:** repeatable regression, unsafe behavior, unacceptable cost, or unmaintained upstream.

For every adopted pattern, preserve source attribution, local adaptation rationale, benchmark evidence, owner, rollback route, and upgrade watch. Do not import entire frameworks merely to obtain one useful pattern.

## Hybrid architecture guardrails

- Native manager retains policy and treatment selection authority.
- LangGraph may own graph-local control flow; it does not grant permissions.
- Deep Agents may be evaluated as a harness inside a bounded treatment.
- Temporal remains the durable cross-worker execution layer when required.
- Provider and MCP adapters retain credentials, allowlists, and tool authorization.
- GitHub remains the source of truth for code, PRs, checks, and workflow runs.
- OTEL/ATES/evidence receipts remain the canonical sanitized measurement plane.
- Human approval remains external to agent self-assertion and graph state.
- A treatment cannot approve, score, or promote itself.

## Promotion rule

Promote a treatment or hybrid only when it:

1. Passes all hard safety, privacy, authorization, and deterministic correctness gates.
2. Meets or exceeds the native control on task quality and evidence completeness.
3. Shows a material, repeatable benefit in at least one declared objective (reliability, latency, cost, capability, or maintainability).
4. Has no unexplained material regression in other dimensions.
5. Has reproducible results, a rollback path, and current-SHA repository/Termux validation.

If results are inconclusive, retain the native control and continue measurement. A failed or inconclusive candidate is useful evidence, not wasted work.

## Work items

- **LGB-009:** implement and maintain this treatment portfolio, task corpus, metrics, and decision ledger.
- **LGB-010:** design and test hybrid compositions from validated patterns; add no production routing change until promotion criteria pass.
