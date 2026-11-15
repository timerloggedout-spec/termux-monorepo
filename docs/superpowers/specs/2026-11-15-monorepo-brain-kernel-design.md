# Monorepo Brain Kernel — Research and Design

**Date:** 2026-11-15  
**Proposal item:** THUB-011  
**Status:** implementation design; explicitly directed by the Operator

## Decision

Create one canonical Rust source at the repository root: **brain.rs**, exporting the public type **Brain**. Do not create a case-only Brain.rs twin. Rust module files use snake_case, and case-only duplicates are unsafe across common development filesystems.

The root source is a provider-neutral cognitive kernel. It selects bounded context, coordinates typed reasoning stages, validates plan structure, records degraded/failure states, and hands a typed decision to an injected policy adapter. It does not call an LLM, execute tools, schedule jobs, write memory, or become a second policy/control plane.

A small standalone crate under **brain/** re-exports the root source so every Rust package in the monorepo can depend on one shared implementation without creating a root Cargo workspace. It has no external dependencies.

## Research findings

### Exact-name inventory

- Current monorepo indexed search did not find root or general-purpose brain.py, Brain.py, brain.rs, or Brain.rs implementations.
- The only exact local Python lead found was _1-Projects/ios-termux/src/ios2termux/brains.py. It is deliberately not the source specification for this task and is excluded from the port.
- The same GitHub organization contains AgentincOS-Native_fork/src/lib/brain-engine.ts, a TypeScript seven-stage engine. It is not currently referenced by the monorepo integration catalog and is research material, not an approved dependency.

### Relevant internal systems

| Source | Actual responsibility | Brain-kernel implication |
|---|---|---|
| src/orchestrator.py | Provider calls, code patching, test dispatch, telemetry, retry and rollback in one orchestrator | Separate reasoning/plan from execution and file mutation |
| workspace/llm_map/manager_agent.py | Keyword/path scoring and agent suggestion | Intent/routing output can inform this lane later; do not silently replace it now |
| workspace/llm_map/dispatch_task.py | Task dispatch, workspace preparation, subprocess execution and verdict persistence | It is a hands/dispatcher surface, not the Brain |
| scripts/decision_engines.py | Comparative System-1 decision engines and completion-gate candidates; explicitly not an LLM provider catalog | Inject the existing policy adapter; do not build a parallel decision registry |
| hub_mcp/ | Canonical capability tiers and tool/device policy boundary | The Brain proposes; existing policy decides whether a handoff is permitted |
| docs/ops/ORCHESTRATION-CONTRACTS.md | Four canonical layers, lifecycle states, identity chain and normalized receipts | Brain belongs inside orchestration and reuses canonical identities/evidence |
| docs/architecture/AGENT-TEAM-CONTROL-PLANE.md | Scout, MVT/DoE, telemetry, bilateral review, promotion and synthesis | Reasoning output is not task success or promotion evidence |
| archwiz/context_relationships/rust_accel/ | Existing standalone Rust crate and Python/Rust separation | Keep a small isolated crate; do not create a root Cargo workspace |

### External FOSS research

- **AgentincOS Native:** seven reasoning stages (intent, decomposition, strategy, execution design, validation, optimization, reflection). Useful stage vocabulary. Its pipeline is a sequential LLM chain; its fallback behavior and separate final chat call make it a pattern to improve, not copy verbatim.
- **JARVIS Cognitive OS:** separates a cognitive core (brain, planner, decomposition, execution graph and hypothesis engine) from execution, tools, memory and recovery. Useful subsystem separation.
- **BLADE:** has a Rust brain.rs used for selective context injection and documents a verified agent loop, structured tool errors, stuck detection, cost guards and isolated subagents. Its README says its v1.5 intelligence layer still has operator-UAT debt; claims are reference signals, not independent validation.
- **brainctl:** its Brain class is a persistent-memory API over SQLite (memories, events, entities, decisions and graph). This is a memory substrate, not the monorepo reasoning kernel; porting its database would create a competing memory authority.
- **Tended (formerly brain):** treats the brain as a knowledge/coordination hub rather than a shell/tool harness. Immutable sources, governed synthesis and no scheduled LLM runs are useful boundaries.
- **Rig:** composable Rust provider clients, models, agents, tools, RAG, memory, workflows, hooks and durable runs. A future provider adapter can use this rather than embedding vendor clients into the shared core.
- **LangGraph:** a low-level state-graph runtime mixing deterministic and model-driven nodes, with durable execution, streaming and human approval. Useful orchestration pattern, not a Rust dependency.

### Governing repository contracts

- Native orchestration has four layers: surfaces; orchestration; evidence/state; SSOT/schemas.
- The identity chain is orchestration_id → cycle_id → attempt_id → action_id → event_id → evidence_id.
- Execution state, task outcome and promotion are distinct; an API call or completed agent run is not task success.
- The Brain/Harness/Hands split is already recorded in docs/ops/AGENT-COMPUTE-ENGINE-COMPARISON-2026-10-26.md: Brain decides, harness governs, hands execute explicit commands.
- The polyglot contract keeps one canonical source/contract and optional Rust implementations behind isolated crates. There is no root Cargo workspace.
- Live GitHub comparison shows master-staging is divergent and 19,637 commits behind master (while it has 54 unique commits). This implementation branch therefore starts from current master, not the stale staging tip.

## Architecture

~~~text
CLI / TUI / MCP / GitHub / Python callers
                 |
                 v
        existing harness / orchestrator
                 |
                 v
       root brain.rs — cognitive kernel
       1. Intent
       2. Decomposition
       3. Strategy
       4. Execution design
       5. Validation
       6. Optimization (optional)
       7. Reflection (optional)
                 |
        typed plan + decision
                 |
                 v
       existing PolicyGate adapter
       (hub_mcp / decision engines / lane policy)
                 |
          authorized handoff only
                 |
                 v
         existing hands/executors
~~~

### Seven stages, not seven mandatory LLM calls

BrainMode::Fast, Standard and Deep select a bounded stage set. The backend is injected through StageBackend; it may be an LLM adapter, a deterministic engine, or a test fixture. The kernel does not assume a provider, model, prompt, or network transport.

- Fast: intent → strategy → validation.
- Standard: intent → decomposition → strategy → execution design → validation.
- Deep: all seven stages, with optimization and reflection optional.

Fallback use is explicitly Degraded, never silently recorded as clean completion. Failure in a required stage yields NeedsReview; optional-stage failure yields a degraded run.

### Context boundary

Context is supplied by an owning retrieval adapter with source reference, evidence state, relevance score, token estimate and classification. Selection is deterministic: relevance descending, stable ID tie-break, bounded by the lesser of request and configured budgets. Restricted, Secret and Unknown context is excluded by default. Candidate/observed evidence remains labeled; the kernel does not upgrade it to verified.

### Plan and policy boundary

Execution design returns a typed DAG. The kernel validates unique IDs, dependency existence, cycles and maximum step count, then emits deterministic parallel groups. It never invokes a tool handler.

PolicyGate is required and injected. There is no built-in allow-all policy, duplicated Canny/System-1 registry, or duplicate hub_mcp capability policy. The adapter returns Ready, NeedsApproval, Blocked or NeedEvidence; the kernel preserves that decision. Structural failure or failed/missing validation cannot be overridden by an allow decision.

**Ready means ready for handoff**, not executed, completed, validated or promoted.

### Memory, reflection and evidence

Reflection emits LearningCandidate records with evidence references only. It does not write to a database. Existing memory/CRG/receipt systems remain authoritative. The kernel accepts canonical run identity and returns stage records for the existing evidence adapter to normalize; it does not create another event ledger.

## Non-goals

- No iOS-Termux port or reuse of its eight HOLD gates.
- No root Cargo.toml or workspace.
- No model-provider SDK, HTTP client, API key handling or vendor routing.
- No tool execution, shell, GitHub write, browser, device control or scheduler.
- No SQLite/graph/vector store or persistent memory implementation.
- No replacement of src/orchestrator.py, manager_agent.py, dispatch_task.py, hub_mcp/ or scripts/decision_engines.py in this change.
- No Brain.rs case-only duplicate.

## Public contract

- Brain<B, P>: typed kernel over an injected StageBackend and PolicyGate.
- BrainInput / RunIdentity: request and canonical orchestration identity.
- BrainStage / BrainMode: seven stages and bounded run modes.
- ContextItem / ContextSelectionReport: provenance-aware, sensitivity-filtered context.
- StageOutput / StageRecord: typed stage results and explicit fallback/failure status.
- ExecutionPlan / PlanValidationReport: dependency DAG and parallel groups.
- PolicyGate / PolicyDecision: delegation to existing authoritative policy.
- BrainResult: structured decision and evidence-ready stage records.

The brain/ crate is a thin facade over root brain.rs, allowing other Rust crates to depend on termux-brain through a path dependency without copying source.

## Validation

- cargo fmt --manifest-path brain/Cargo.toml -- --check
- cargo check --manifest-path brain/Cargo.toml --all-targets
- cargo test --manifest-path brain/Cargo.toml
- cargo clippy --manifest-path brain/Cargo.toml --all-targets -- -D warnings
- Path-filtered GitHub Actions runs the same Rust checks on the exact PR SHA.
- Repository dual gates remain python3 scripts/ci/repo_gate.py and python3 scripts/ci/termux_smoke.py.
- Tests cover mode selection, context classification/budget, duplicate IDs, DAG cycles/missing dependencies, policy handoff, validation failure, required/optional stage failures and fallback transparency.

## Promotion boundary

The kernel is committed and remotely tested as a standalone crate. That does not imply the Python orchestrators have been switched to it. A later adapter/integration item must demonstrate protocol parity and task-outcome benefit before existing execution paths are redirected.

## Research references

### Internal monorepo sources

- [Python orchestration entrypoint](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/src/orchestrator.py)
- [Agent manager](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/workspace/llm_map/manager_agent.py)
- [Task dispatcher](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/workspace/llm_map/dispatch_task.py)
- [Decision-engine comparison](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/scripts/decision_engines.py)
- [Orchestration contracts](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/ORCHESTRATION-CONTRACTS.md)
- [Polyglot acceleration contract](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/CONTEXT-RELATIONSHIP-POLYGLOT-ACCELERATION.md)
- [Agent compute-engine comparison](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/AGENT-COMPUTE-ENGINE-COMPARISON-2026-10-26.md)

### External projects

- [AgentincOS Native — seven-stage brain engine](https://github.com/timerloggedout-spec/AgentincOS-Native_fork/blob/main/src/lib/brain-engine.ts)
- [JARVIS Cognitive OS](https://github.com/oguzemirtopuz/JARVIS-Cognitive-OS)
- [BLADE — Rust brain/context implementation](https://github.com/sb-arnav/BLADE)
- [brainctl — persistent-memory architecture](https://github.com/TSchonleber/brainctl/blob/main/ARCHITECTURE.md)
- [Tended — local-first knowledge and coordination hub](https://github.com/misabegovic/tended)
- [Rig — Rust agent framework concepts](https://rig.rs/docs/concepts/)
- [LangGraph — stateful agent orchestration](https://docs.langchain.com/oss/python/langgraph/overview)
