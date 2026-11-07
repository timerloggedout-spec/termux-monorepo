---
name: langgraph-orchestration
description: "Design, implement, test, and evaluate LangGraph workflows in termux-monorepo. Use when building stateful graph orchestration, multi-agent fan-out, routing, resumable approvals, graph persistence, streaming, or LangGraph-to-Temporal/ATES adapters."
---

# LangGraph Orchestration — BIUDL integration skill

Use this skill when a task genuinely benefits from explicit graph control flow. It adapts official LangChain/LangGraph guidance to the repository's BIUDL, FA-ADE, proposal, evidence, and security contracts.

## Required repository context

Load, in order and only as needed:

1. `CLAUDE.md` — BIUDL, proposal authorization, dual gates, promotion.
2. `docs/proposals/registry.yaml` and `docs/proposals/active/langgraph-biudl-integration/ITEMS.md` — authorized scope.
3. `docs/ops/ORCHESTRATION-CONTRACTS.md` — canonical orchestration identity, state, receipt, and adapter boundaries.
4. `docs/ops/AGENT-TEAM-ORCHESTRATION.md` — manager/team optimization.
5. `.agents/skills/adaptive-wait/SKILL.md`, `.agents/skills/adaptive-feedback-cycle/SKILL.md`, `.agents/skills/context-relationship-graph/SKILL.md`, and `.github/skills/production-reconciliation/SKILL.md` when the task touches their domains.
6. The upstream layer-specific LangGraph skill below before writing LangGraph code.

## BIUDL execution

| BIUDL phase | LangGraph work | Required evidence |
|---|---|---|
| **Broad** | Recon the existing manager, task, workflow, provider, memory, and telemetry surfaces. Select graph use only where explicit branching, fan-out, state, or pause/resume is valuable. | Current source paths, proposal item, alternatives considered |
| **Integrate** | Design state schema, nodes, edges, reducers, persistence, interrupt points, and adapter seams. Keep provider calls behind existing interfaces. | Graph diagram, state contract, treatment descriptor |
| **Validate** | Test node behavior, routing, reducers, fan-out aggregation, checkpoint/resume, idempotency, and failure classes. Run the graph under a deterministic fixture. | Focused tests, graph run receipt, expected/observed transition set |
| **Develop** | Integrate only the validated slice. Preserve repository dual gates and current-SHA evidence. | PR, checks, tests, action/effect evidence |
| **Learn** | Record outcomes, latency, retries, tool delay, context cost, useful parallel yield, and attribution in existing ATES / evidence contracts. Compare orchestration treatments on equivalent cohorts. | Receipt, outcome classification, longitudinal evidence |

## When to use LangGraph

Prefer LangGraph when the workflow needs one or more of:

- explicit conditional or cyclic control flow;
- parallel fan-out and deterministic aggregation;
- a state machine spanning multiple agent/tool steps;
- checkpointed pause/resume or state inspection;
- streaming intermediate state or progress;
- composable subgraphs with separately testable contracts.

Prefer the existing direct CLI/tool path for simple linear tasks. Prefer Deep Agents when the primary need is a ready-made planning, filesystem, skills, or subagent harness. Prefer Temporal when the primary requirement is durable cross-process / cross-worker execution, scheduling, and replay across worker failure. LangGraph can run inside a Temporal Activity; it does not replace Temporal's durable execution boundary.

## Official upstream skill set

The canonical upstream source is [langchain-ai/langchain-skills](https://github.com/langchain-ai/langchain-skills). These are the best first-load skills for LangGraph implementation:

| Skill | Load when | Pinned source blob |
|---|---|---|
| `langgraph-fundamentals` | Any LangGraph code: StateGraph, state, nodes, edges, Command, Send, invoke, streaming, errors | `adf7bff81897aa99d9505195a1196fced6047b97` |
| `langgraph-human-in-the-loop` | Interrupts, approval, validation, pause/resume, recoverable errors | `d762f2a170c30310b5641642af3e19ce7866a28a` |
| `langgraph-persistence` | Checkpointers, thread identity, cross-thread Store, history/time travel, subgraph checkpoint scope | `bbcf0ea77bf2b374a99e5d08cae147c12da03e82` |

Read the source SKILL.md and its language reference from the pinned upstream repository before code changes. Do not copy an entire upstream skill into this repository; retain provenance and adapt only the invariants needed by this project.

- Fundamentals: https://github.com/langchain-ai/langchain-skills/tree/main/config/skills/langgraph-fundamentals
- Human-in-the-loop: https://github.com/langchain-ai/langchain-skills/tree/main/config/skills/langgraph-human-in-the-loop
- Persistence: https://github.com/langchain-ai/langchain-skills/tree/main/config/skills/langgraph-persistence
- Upstream catalog: https://github.com/langchain-ai/langchain-skills

## Graph design contract

1. Draw the graph before implementation. Every node must have a single responsibility and explicit inputs/outputs.
2. Define a typed state schema. Return partial state updates; do not mutate the shared state object in place.
3. Define reducers for accumulated fields. In fan-out graphs, parallel result fields must have an explicit reducer and stable task identity; never rely on last-write-wins for concurrent results.
4. Use static edges for deterministic transitions, conditional edges for routing, `Command` when a node must update state and route, and `Send` for dynamic fan-out.
5. Treat `Command` routing and static edges as additive: if both are configured from a node, both paths may execute. Test the actual transition set.
6. Every cycle must have a named continuation/termination condition, bounded iteration or a provable exit, and an observable terminal state.
7. Compile the builder before invocation. Pin library/API versions in the owning dependency manifest when a runtime dependency is approved; inspect the installed API rather than relying on remembered signatures.
8. Use the project's established model/provider adapters. A graph is an orchestration strategy, not a new credential or provider-routing authority.

## Persistence and replay

- Use a stable, opaque `thread_id` for every checkpointed execution; do not derive it from secrets or expose user-identifying content.
- In-memory checkpointers are for tests/development only. Select a production backend through an explicit proposal and data-retention/security review; PostgreSQL is a candidate, not an automatic dependency.
- Keep graph checkpoint state separate from canonical repository evidence. Checkpoints may contain prompts, messages, tool arguments, or user data and are therefore not eligible for Git, ordinary artifacts, ATES JSONL, or public receipts.
- Use LangGraph checkpoint history for graph-local debugging/replay. Use GitHub SHA, workflow run/job/step/artifact IDs, and the repository evidence envelope for project provenance.
- If Temporal is present, use Temporal workflow history as the durable cross-worker execution record and map only sanitized identifiers/events into the repository evidence plane.

## Human approval and side effects

- Use `interrupt()` only with a checkpointer and the same stable `thread_id` on resume.
- Resume with `Command(resume=...)`; do not substitute a normal input dict for a resume command.
- The node restarts from its beginning on resume. Place side effects after the interrupt where possible; otherwise make them idempotent (upsert / check-before-create) and test duplicate prevention.
- Human approval is not a generic escape hatch. Follow `docs/proposals/AGENTIC-PERMISSIONS.md` for credential, production, financial, privacy, and destructive edges.
- Never infer approval from a graph reaching an approval node, a model response, a timeout, or a missing interrupt result.

## Error, retry, and loop policy

Classify errors before retrying:

| Class | Treatment |
|---|---|
| Transient network / rate limit | Bounded retry with backoff and attempt evidence |
| Tool failure recoverable by agent | Return a typed tool error and allow one policy-bounded recovery route |
| Missing human input / approval | Interrupt and wait; preserve checkpoint identity |
| Validation / contract failure | Fail closed; route to repair or terminal failure |
| Unexpected exception | Surface failure with traceback reference in restricted logs; do not silently convert to success |

Retries must be informative, bounded, idempotent, and represented as distinct attempts. Do not hide failures behind graph loops. A loop that makes no measurable progress becomes `stagnated`, not success.

## Observability and ATES adapter

Emit only sanitized metadata to existing contracts:

- orchestration / cycle / attempt / action / event IDs;
- graph name and version, node name, transition type, and sequence number;
- repository, ref, immutable SHA, workflow/run identifiers where applicable;
- actor/provider/model identifiers only when attributable;
- start/end timestamps, duration, retry classification, and terminal state;
- evidence IDs, validation outcome, and promotion classification.

Never export prompts, completions, message bodies, arbitrary graph state, tool payloads, secrets, tokens, checkpoint blobs, or raw user content. Reuse the existing OpenTelemetry, ATES JSONL, evidence-envelope, action/effect, and orchestration receipt contracts. Do not invent a second trace schema or score.

For parallel work, record fan-out count, completed/failed workers, useful accepted outputs, merge conflicts, duplicate effort, and integration outcome. `parallel yield` is not simply worker count.

## Testing contract

At minimum, cover:

- graph compiles and completes the happy path;
- every conditional route and terminal branch;
- reducer behavior under multiple parallel updates;
- duplicate / missing / out-of-order event handling;
- bounded loop termination and retry ceilings;
- interrupt pause + same-thread resume;
- side-effect idempotency across resume/replay;
- persistence behavior under the selected checkpointer;
- sanitized telemetry schema and absence of raw state;
- failure classification and non-success terminal states.

Use deterministic stub nodes and fixtures for structural tests. Keep provider/model calls out of unit tests. Run the focused suite, then the repository gates:

```bash
python3 scripts/ci/repo_gate.py
python3 scripts/ci/termux_smoke.py
```

Report commands actually run; never claim a gate passed from its existence or queued status.

## External ecosystem shortlist

The source index [vonzosten/awesome-LangGraph](https://github.com/vonzosten/awesome-LangGraph) is a discovery catalogue, not an endorsement or dependency manifest. Highest-value candidates to evaluate selectively:

- Official `langgraph-supervisor` / `langgraph-swarm`: alternative coordination topologies; compare against the native manager treatment registry before adopting.
- `langchain-mcp-adapters`: MCP tool bridge candidate; compare with the existing MCP catalog and adapter/foundry boundary.
- `deepagents`: planning, context/filesystem, subagent, skill, and memory harness; use only where its built-ins solve a demonstrated gap.
- `open_deep_research` / `open-swe`: reference architectures for research and coding agents; inspect code, licenses, dependencies, and security before any extraction.
- Security references such as `aport-agent-guardrails` and `sidclawhq/platform`: research-only until threat model, enforcement boundary, maintenance, and license are independently verified.

No repository forks, vendoring, submodules, dependencies, provider credentials, or deployments are created by reading this shortlist.

## Completion and promotion

Use the existing lifecycle:

`RECON → PLAN → ACT → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD → REPEAT`

Keep `COMMITTED`, `EXECUTED`, `VALIDATED`, and `PROMOTED` independent. LangGraph cannot self-approve, self-merge, or override repository promotion policy.
