# Source map — agentic ecosystem, planning and logistics

**Evidence rule:** a repository README establishes what its owner describes; it does not independently prove maturity, security, license compliance, runtime behavior or production fitness. Fork and watch signals are discovery inputs, not adoption authority.

## Owned repositories and forks

| Repository | Default branch | README-supported description | Proposed use | Evidence / adoption state |
|---|---|---|---|---|
| [timerloggedout-spec/langchain_fork](https://github.com/timerloggedout-spec/langchain_fork) | master | LangChain agent engineering framework; package map includes core, classic and v1 libraries, model profiles, partner integrations, standard tests and text splitters. README links LangGraph, Deep Agents, provider integrations, LangSmith and deployment. | Ecosystem root and integration package census. | Fork confirmed; README and libs/README reviewed. Not installed or modified. Contributor guide required before upstream code changes. |
| [timerloggedout-spec/awesome-LangGraph_fork](https://github.com/timerloggedout-spec/awesome-LangGraph_fork) | main | Broad index of frameworks, apps, integrations, providers, templates, community projects, examples and learning materials around LangGraph/LangChain. | Discovery index; classify candidates into build/observe/evaluate/deploy/security/logistics. | README reviewed; not a trust list or dependency lockfile. |
| [timerloggedout-spec/langchain-runnableparallel-company-research_fork](https://github.com/timerloggedout-spec/langchain-runnableparallel-company-research_fork) | main | Parallel retrievers, typed Pydantic result bundle and partial-failure preservation. | Small example for parallel data acquisition, typed aggregation and source-failure isolation. | README reviewed; not yet tested in this runtime. |
| [timerloggedout-spec/AI-Planning_fork-PDDL-air-transport](https://github.com/timerloggedout-spec/AI-Planning_fork-PDDL-air-transport) | master | Classical PDDL Air Cargo domain with Load/Unload/Fly actions, planning problems, search baselines, heuristics and planning-graph experiments. | Educational seed for logistics action schemas and planner fixtures. | README reviewed; code/license/runtime validation outstanding. |
| [timerloggedout-spec/rl-multiagent-transfer_fork](https://github.com/timerloggedout-spec/rl-multiagent-transfer_fork) | main | README identifies multi-agent path planning based on reinforcement learning for intelligent library logistics. | Candidate research stratum for multi-agent routing; assess baseline and reproducibility. | README only; low evidence maturity. |
| [timerloggedout-spec/FrieghtFlow](https://github.com/timerloggedout-spec/FrieghtFlow) | main | README describes a freight/shipment platform with Next.js, NestJS, PostgreSQL and Stellar smart-contract components. | Domain vocabulary and workflow discovery; compare provenance/traceability requirements. | README claims only; no security, chain, smart-contract or operational audit. |

## Existing monorepo integration surfaces

| Surface | Observed state | Required action |
|---|---|---|
| PR #5045 LangGraph BIUDL | Open; current head d850d8648c8792c85da27a3f94c3f931ef86c674; repo gate failed on invalid_control_plane_yaml ratchet, Termux smoke succeeded. | Remediate the exact gate finding and re-fetch current PR checks before treating it as promoted. |
| docs/ops/TEMPORAL-LANGSMITH-ADAPTER.md | Existing optional adapter connects trajectories/traces for LangChain/LangGraph/Deep Agents and SDK-style agents. | Reuse; do not add another trace ledger. |
| Bifrost gateway integration proposal | Existing integration and benchmark forks/PR history. | Reconcile provider capability interface; no duplicate gateway. |
| #5145 + #5146 | Existing QDesk Observatory/Delphi RFP pipeline and linked review issue. | Reuse RFP gate, Oracle, feed, acceptance matrix and review states. |
| #5160 + #5134 | Free-inference population/cadence task blocked on provider index integration. | Existing owner for endpoint pools and autoQuotaCadence. |
| #5183 + #5136 + #5176 + #4979 | Participant clones, identity and executor/admission sequencing. | No participant issuance or provisioning outside these gates. |
| #5189 | Specialist-role registry proposal includes control-systems-specialist and optimization-researcher. | Extend/match existing role contracts; no parallel registry. |

## External candidate projects for a later license/maintenance review

| Candidate | Intended fit | Boundary |
|---|---|---|
| [AIPlan4EU Unified Planning](https://github.com/aiplan4eu/unified-planning) | Planner-independent problem model, PDDL input/output and multiple planner engines. | Candidate abstraction, not installed/adopted. Verify current package, engines, support and license. |
| [Fast Downward](https://github.com/aibasel/downward) | Classical deterministic planning over its supported PDDL fragment. | Not assumed to support general numeric/temporal scheduling. Validate language compatibility first. |
| [Google OR-Tools](https://github.com/google/or-tools) | CP-SAT, routing, assignment and capacity/time-window optimization. | Complement to PDDL, not a replacement for symbolic action planning. |
| [PDDLStream](https://github.com/caelan/pddlstream) | Sampling-based procedures for task-and-motion planning. | Optional robotics/embodied-planning research only. |
| [Inference Scheduler](https://github.com/summonlabs/Inference-Scheduler) | Research candidate for bounded admission, queueing, batching, fairness and backpressure. | Project claims are not an audit; benchmark/admission review required before considering reuse. |

## Provenance limitations

- No upstream code was installed, copied, built or deployed during this RECON.
- No live provider/model invocation was made, and no account entitlement or remaining quota was inferred.
- Repository licenses other than claims surfaced in individual README badges have not been independently checked; source-specific license and dependency review precedes reuse.
- No new fork was created. The available GitHub connector did not expose a fork/create-repository action in this session; the owned forks above are the confirmed assets.
- The Historical Context Relationship manifest is dated 2026-10-26 and declares PARTIAL_CONTINUATION_REQUIRED; it is not used as current proof of graph completeness.
