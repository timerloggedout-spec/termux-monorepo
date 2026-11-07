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
| OpenTelemetry + ATES JSONL | Canonical execution observations and throughput measures |
| Evidence envelope + action/effect ledger | Stable evidence IDs and action-to-effect follow-through |
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

The official [LangChain Skills repository](https://github.com/langchain-ai/langchain-skills) provides three directly relevant skills. Their source blob SHAs are recorded in `.agents/skills/langgraph-orchestration/SKILL.md`.

1. `langgraph-fundamentals` — mandatory for any graph code.
2. `langgraph-human-in-the-loop` — mandatory for interrupt/approval/resume work.
3. `langgraph-persistence` — mandatory for checkpointer, thread, Store, history, or subgraph persistence work.

These skills are upstream references; this repository contains a project-specific adaptation, not copied upstream skill bodies.

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

## Non-goals

- No LangSmith-only observability requirement.
- No replacement of Temporal for durable execution.
- No automatic production checkpointer/database selection.
- No blind adoption of every project in the Awesome list.
- No external repo cloning, submodule, vendoring, or secret provisioning.
- No autonomous merge/promotion based on a graph's own output.
