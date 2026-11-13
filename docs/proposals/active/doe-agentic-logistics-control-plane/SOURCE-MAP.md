# Source map — agentic ecosystem, planning and logistics

**Evidence rule:** a repository README establishes what its owner describes; it does not independently prove maturity, security, license compliance, runtime behavior or production fitness. Fork and watch signals are discovery inputs, not adoption authority.

## Owned repositories and forks

| Repository | Default branch | README-supported description | Proposed use | Evidence / adoption state |
|---|---|---|---|---|
| [timerloggedout-spec/langchain_fork](https://github.com/timerloggedout-spec/langchain_fork) | master | LangChain agent engineering framework; package map includes core, classic and v1 libraries, model profiles, partner integrations, standard tests and text splitters. README links LangGraph, Deep Agents, provider integrations, LangSmith and deployment. | Ecosystem root and integration package census. | Fork confirmed; README and libs/README reviewed. Not installed or modified. Contributor guide required before upstream code changes. |
| [timerloggedout-spec/awesome-LangGraph_fork](https://github.com/timerloggedout-spec/awesome-LangGraph_fork) | main | Broad index of frameworks, apps, integrations, providers, templates, community projects, examples and learning materials around LangGraph/LangChain. | Discovery index; classify candidates into build/observe/evaluate/deploy/security/logistics. | README reviewed; not a trust list or dependency lockfile. |
| [timerloggedout-spec/langchain-runnableparallel-company-research_fork](https://github.com/timerloggedout-spec/langchain-runnableparallel-company-research_fork) | main | Parallel retrievers, typed Pydantic result bundle and partial-failure preservation. | Small example for parallel data acquisition, typed aggregation and source-failure isolation. | README reviewed; not yet tested in this runtime. |
| [sunsided/pddl-rs](https://github.com/sunsided/pddl-rs) | main | Strongly typed PDDL 3.1 Rust parser using nom; parses domain/problem structures and PddlFile; optional pretty-print feature and examples/tests. It is not a planner. | Candidate parser/AST adapter for fixture validation and round-trip checks. | README, Cargo.toml and pretty_print example inspected; crate license EUPL-1.2; legal/compatibility review required before dependency adoption. |
| [timerloggedout-spec/AI-Planning_fork-PDDL-air-transport](https://github.com/timerloggedout-spec/AI-Planning_fork-PDDL-air-transport) | master | README describes a classical PDDL Air Cargo exercise (Load/Unload/Fly) and Python implementations of grounded actions, search baselines, heuristics and planning graphs. The inspected tree contains no `.pddl` domain/problem files. | Educational seed for translating symbolic action schemas into a real PDDL fixture and planner comparison. | README, Python implementation and unit tests inspected; no root LICENSE; not yet executed. See LOGISTICS-PLANNING-ASSESSMENT.md. |
| [timerloggedout-spec/rl-multiagent-transfer_fork](https://github.com/timerloggedout-spec/rl-multiagent-transfer_fork) | main | Full Python multi-agent library-logistics RL prototype: two-floor 9×9 GridWorld, Q-learning brain, curriculum/stage training, shared-policy multi-agent coordination, transfer-learning helpers, visualization, logs, serialized Q-table and reward/figure artifacts. | Existing domain-specific research implementation and baseline candidate for library logistics; preserve as a source project and integrate through a reproducible adapter/benchmark, not by replacing it with a newly invented simulator. | Fork parent confirmed as `Hiago013/rl-multiagent-transfer`; main branch only; 7 commits (2023-10-21→2024-01-10). Tree includes `GridWorld.py`, `brain.py`, `multi_agent.py`, `training.py`, `view.py`, curriculum/transfer/logger modules, library map data, 74,166,360-byte `qtable.txt`, 72,923,780-byte backup, 45 reward plots, 42 figures and an 11.5 MB animation. Source code and artifacts confirmed; runtime was not executed in this RECON. No root LICENSE, dependency manifest or test suite was found in the inspected tree; reuse and reproducibility gates remain. |
| [timerloggedout-spec/FrieghtFlow](https://github.com/timerloggedout-spec/FrieghtFlow) | main | README describes freight/shipment management with Next.js/React frontend, NestJS/TypeORM/PostgreSQL backend and Stellar components. Backend package is private and declares UNLICENSED. | Domain vocabulary and workflow discovery only; not a dependency or deployable logistics service for this program. | README and package manifests inspected; no root LICENSE; backend package is private/UNLICENSED. No security, chain, smart-contract or operational audit. |

## Existing monorepo integration surfaces

| Surface | Observed state | Required action |
|---|---|---|
| PR #5045 LangGraph BIUDL | Open; current head d850d8648c8792c85da27a3f94c3f931ef86c674; repo gate failed on invalid_control_plane_yaml ratchet, Termux smoke succeeded. | Remediate the exact gate finding and re-fetch current PR checks before treating it as promoted. |
| docs/ops/TEMPORAL-LANGSMITH-ADAPTER.md | Existing optional adapter connects trajectories/traces for LangChain/LangGraph/Deep Agents and SDK-style agents. | Reuse; do not add another trace ledger. |
| Bifrost gateway integration proposal | Existing integration and benchmark forks/PR history. | Reconcile provider capability interface; no duplicate gateway. |
| #5145 + #5146 | Existing QDesk Observatory/Delphi RFP pipeline and linked review issue. | Reuse RFP gate, Oracle, feed, acceptance matrix and review states. |
| #5160 + #5134 | #5160 autoQuotaCadence repair merged via PR #5258 at `87dd55c618fd4c4dc2fdc71a5902539ae9a32a1e` (2026-11-13); conversion machinery landed, first live conversion remains unobserved. | Existing owner for endpoint-pool derivation and cadence; no duplicate pool/ledger/scheduler. |
| #5183 + #5136 + #5176 + #4979 | Participant clones, identity and executor/admission sequencing. | No participant issuance or provisioning outside these gates. |
| #5189 | Specialist-role registry proposal includes control-systems-specialist and optimization-researcher. | Extend/match existing role contracts; no parallel registry. |

## Validated ML platform research input

The owner-ingested [platform validation set](https://github.com/timerloggedout-spec/termux-monorepo/tree/master/ml/labbook/platform-validation-2026-11-03) is a separate research source, not an owned upstream dependency and not an adoption decision. It was committed to master at `e4082fa6cde41c31cbbd62322143a1fe45631122` and contains:

- `SYNTHESIS.md`: comparative design record across MLflow, Metaflow, ClearML, ZenML, Flyte, MLRun, Kubeflow Pipelines, Dagster, Kedro and DVC.
- `VALIDATION.md`, `VALIDATION_Dagster.md`, `VALIDATION_DVC.md`, `VALIDATION_MLRun.md`, `VALIDATION_ClearML.md`, `VALIDATION_flyte.md`: platform-specific workload, environment, read-back and verdict evidence.

**Decision use:** derive requirements for local queryable run records, append-only asset history, portable native-format/content-addressed artifacts, explicit pipeline IR/node verdicts, independent-process reproduction and failure transparency. Preserve each report's verified/claimed/unestablished distinctions. The MLRun source-server/SQLite and mock-serving experiments do not establish Kubernetes/Iguazio or a live serving endpoint; Flyte cluster behavior is likewise unestablished. See RFP §4 and ARCHITECTURE.md for the resulting constraints.

## Neighboring repository excluded from the LangChain ecosystem set

- timerloggedout-spec/LibreChat_fork was returned by an account-wide search for the word LangChain, but its current README does not mention LangChain or LangGraph. It is therefore not counted as a LangChain ecosystem dependency in this proposal. It may be evaluated separately as a chat/UI surface if a concrete integration requirement appears.

## External candidate projects for a later license/maintenance review

| Candidate | Intended fit | Boundary |
|---|---|---|
| [AIPlan4EU Unified Planning](https://github.com/aiplan4eu/unified-planning) | Planner-independent problem model, PDDL input/output and multiple planner engines. | Candidate abstraction, not installed/adopted. Verify current package, engines, support and license. |
| [Fast Downward](https://github.com/aibasel/downward) | Classical deterministic planning over its supported PDDL fragment. | Not assumed to support general numeric/temporal scheduling. Validate language compatibility first. |
| [Google OR-Tools](https://github.com/google/or-tools) | CP-SAT, routing, assignment and capacity/time-window optimization. | Complement to PDDL, not a replacement for symbolic action planning. |
| [PDDLStream](https://github.com/caelan/pddlstream) | Sampling-based procedures for task-and-motion planning. | Optional robotics/embodied-planning research only. |
| [Inference Scheduler](https://github.com/summonlabs/Inference-Scheduler) | Research candidate for bounded admission, queueing, batching, fairness and backpressure. | Project claims are not an audit; benchmark/admission review required before considering reuse. |

## License observations

- langchain_fork root LICENSE: MIT (blob SHA 3957738673765912ca83a0048f833e095d61e087).
- awesome-LangGraph_fork root LICENSE: CC0 1.0 (blob SHA 1625c1793607996fcfc46420e8aa2f3d2b7efd1e); this does not relicense linked third-party projects.
- langchain-runnableparallel-company-research_fork root LICENSE: MIT (blob SHA 14fac913ccf80234b1848540089a3bbcb6e5283d).
- PDDL Air Cargo and rl-multiagent-transfer have no root LICENSE file at the inspected default-branch path; reuse remains blocked pending license verification. FrieghtFlow also has no root LICENSE, and its backend package explicitly declares private: true and license: UNLICENSED; treat as non-reusable absent an explicit owner grant.

## Provenance limitations

- No upstream code was installed, copied, built or deployed during this RECON.
- No live provider/model invocation was made, and no account entitlement or remaining quota was inferred.
- Repository licenses other than claims surfaced in individual README badges have not been independently checked; source-specific license and dependency review precedes reuse.
- No new fork was created. The available GitHub connector did not expose a fork/create-repository action in this session; the owned forks above are the confirmed assets.
- The Historical Context Relationship manifest is dated 2026-10-26 and declares PARTIAL_CONTINUATION_REQUIRED; it is not used as current proof of graph completeness.
