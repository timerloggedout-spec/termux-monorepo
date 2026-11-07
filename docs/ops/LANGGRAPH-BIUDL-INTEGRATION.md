# LangGraph × BIUDL Integration

**Proposal:** `langgraph-biudl-integration`  
**Status:** executing — skill and architecture slice provisioned; runtime adapter remains separately gated  
**Source index:** [vonzosten/awesome-LangGraph](https://github.com/vonzosten/awesome-LangGraph)  
**Framework:** [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)

## Executive decision

Adopt LangGraph as an **optional graph-orchestration treatment** for workflows that need explicit state, conditional routing, fan-out, checkpointed pause/resume, or composable subgraphs.

Do not replace the repository's native manager, orchestration treatment registry, evidence envelope, ATES, OpenTelemetry, Temporal, GitHub execution fabric, proposal governance, or promotion gates.

The initial integration is **skill + architecture + proposal-scoped**. It intentionally does not add a runtime dependency, external service, provider key, database, fork, or deployment. Those require a separate measured implementation item and compatibility/security review.

## Existing capabilities to reuse

| Existing contract | LangGraph integration |
|---|---|
| `docs/ops/ORCHESTRATION-CONTRACTS.md` | Canonical identity, state, receipt, adapter boundary |
| `ORCHESTRATION-TREATMENT.schema.json` | Describe a LangGraph graph as a comparable treatment |
| `ORCHESTRATION-RECEIPT.schema.json` | Project sanitized graph lifecycle/outcome |
| Existing `OrchestratorTracer` + ATES bridge | Existing metadata-first span capture and six whitelisted event mappings; extend only under a versioned schema change |
| OpenTelemetry + ATES JSONL | Canonical execution observations and throughput measures |
| Evidence envelope + orchestration receipt | Sanitized graph-run outcome and SHA-bound provenance |
| Action/effect event schema | PR discussion/review-to-commit follow-through only; not a generic graph-node ledger |
| Context relationship graph | Link graph runs to repo SHA, PR, issue, workflow, and source paths |
| Adaptive wait + production reconciliation | Wait, inspect, classify, re-fetch, compare |
| Temporal self-host + LangSmith adapter | Optional durable execution / trajectory bridge |

## Capability boundary

```text
Manager / BIUDL policy
        |
        v
LangGraph treatment (optional)
  StateGraph / nodes / edges
  reducers / Send / subgraphs
  checkpoint / interrupt / stream
        |
        +---- existing provider + MCP adapters
        |
        +---- Temporal Activity (when cross-worker durability is required)
        |
        v
Sanitized event adapter
        |
        +---- OpenTelemetry
        +---- ATES / action-effect ledger
        +---- evidence envelope / receipt
        |
        v
SHE / 3L0 / MoneyBall / manager evaluation
```

LangGraph owns graph-local control flow and checkpoint state. Temporal owns durable cross-worker workflow execution when selected. GitHub remains the repository/PR/check/run source of truth. The native evidence contracts own project-level provenance and evaluation.

## Selection rules

| Need | Preferred surface | Reason |
|---|---|---|
| Simple linear CLI or tool call | Existing native path | Lower complexity and dependency cost |
| Branching, loops, parallel fan-out, explicit state | LangGraph candidate | Graph-native control flow |
| Ready-made planning, filesystem, skills, and subagents | Deep Agents candidate | Harness capability rather than low-level graph |
| Long-running work surviving worker/process loss | Temporal | Durable execution and replay boundary |
| Cross-run experiment comparison | Native MVT/DoE + ATES | Existing measurement contract |
| Trace visualization / evaluation | OTEL + optional LangSmith/Langfuse/Phoenix | Adapter, not canonical evidence |

## Telemetry contract gap

The current `AGENT-THROUGHPUT-EVENT.schema.json` is closed and allows only six event kinds. The existing bridge in `scripts/ci/bridge_ates_trace_to_events.py` already hashes free-text labels and drops raw context. LangGraph can initially emit graph-run start/completion and true tool/handoff events through this adapter. It cannot safely emit graph node names, transition IDs, graph versions, or checkpoint/thread identifiers yet. LGB-006 must propose a versioned, allowlisted schema extension and regression/privacy tests before those fields are emitted. Do not overload `tool` or reuse `ACTION-EFFECT-EVENT.schema.json`, which currently models review/comment follow-through.

## State and security rules

- State schema is typed and minimal; graph state is not a repository event log.
- Reducers are explicit for accumulated and parallel fields.
- Thread IDs are opaque, stable, and non-identifying.
- Checkpoint payloads are restricted data; no prompts, completions, tool arguments, or checkpoint blobs in Git, public artifacts, ATES, or receipts.
- Production checkpointer choice requires an approved persistence/security item; in-memory is test-only.
- Interrupts require checkpointing and same-thread resume. Nodes restart on resume, so pre-interrupt side effects must be idempotent.
- Tool side effects continue to pass through existing authorization, allowlists, and action/effect evidence.
- Provider/model routing remains with existing provider adapters and manager policy.

## Upstream skill shortlist

The official [LangChain Skills repository](https://github.com/langchain-ai/langchain-skills) provides the layer-selection primer, three core LangGraph skills, optional quickstarts/CLI guidance, and adjacent Deep Agents skills. Their source blob SHAs and load conditions are recorded in `.agents/skills/langgraph-orchestration/SKILL.md`.

1. `ecosystem-primer` — first, to choose LangChain vs LangGraph vs Deep Agents.
2. `langgraph-fundamentals` — mandatory for any graph code.
3. `langgraph-human-in-the-loop` — mandatory for interrupt/approval/resume work.
4. `langgraph-persistence` — mandatory for checkpointer, thread, Store, history, or subgraph persistence work.
5. `langgraph-cli` — optional scaffold/dev/build/deploy lifecycle.
6. Python/TypeScript quickstarts — only for explicit minimal new-project requests.
7. `eval-engineering` — companion for benchmark/task/verifier design and calibration; keep existing MVT/DoE/ATES governance authoritative.
8. `deep-agents-core` + `deep-agents-orchestration` — adjacent alternative when the higher-level harness is a better fit.

The upstream skills README labels the collection early-development; re-check current content and installed APIs before implementation. These skills are upstream references; this repository contains a project-specific adaptation, not copied upstream skill bodies.

## BIUDL implementation sequence

| Item | Slice | Acceptance |
|---|---|---|
| LGB-001 | Source + architecture recon | Existing overlap and no-duplicate boundaries recorded |
| LGB-002 | Repository-native LangGraph skill | Trigger, upstream pins, BIUDL flow, safety, test contract indexed |
| LGB-003 | Orchestration adapter contract | LangGraph mapping to existing receipt/evidence/Temporal boundaries |
| LGB-004 | Minimal Python graph proof | Optional extra, deterministic no-provider graph, compile/invoke tests |
| LGB-005 | Persistence + HITL proof | Checkpointer, stable thread ID, pause/resume, idempotency tests |
| LGB-006 | ATES/OTEL adapter | Sanitized events only; schema and privacy tests |
| LGB-007 | Controlled treatment comparison | Same cohort/tasks/acceptance, manager and LangGraph treatments compared |
| LGB-008 | Dual-gate + promotion | Current-SHA repo gate + Termux smoke, review, verified outcome |

Items LGB-001–003 are the initial documentation/skill slice. LGB-004 onward remain backlog until their implementation plan, dependency impact, and test environment are established.

## Candidate dispositions from source inspection

| Project | Decision | Evidence-based reason |
|---|---|---|
| `langgraph-swarm-py` | Evaluate as a treatment | Official handoff topology; compare to native manager |
| `langgraph-supervisor-py` | Legacy reference only | Upstream recommends tool-based supervisor patterns for most new work |
| `langchain-mcp-adapters` | Do not adopt | Upstream archived the repository on 2026-09-17; MCP support moved to `langchain[mcp]` / `langchain.mcp` |
| `deepagents` | Alternative harness | Select when planning/filesystem/subagents/skills/memory are the actual need |
| `open-swe` | Research only | Upstream warns active development and no correctness/stability guarantees |
| `open_deep_research` | Reference only | Verify maintenance; visible README updates are from 2025 |
| `swarm-at-ledger` | Integrity pattern only | README explicitly labels its records synthetic, not real agent interaction evidence |
| `aport-agent-guardrails` | Security research only | Require independent bypass and threat-model validation |
| `langgraph-starter-kit` | Community reference only | Inspect license, dependencies, test coverage, and security before extraction |

## Non-goals

- No LangSmith-only observability requirement.
- No replacement of Temporal for durable execution.
- No automatic production checkpointer/database selection.
- No blind adoption of every project in the Awesome list.
- No external repo cloning, submodule, vendoring, or secret provisioning.
- No autonomous merge/promotion based on a graph's own output.
