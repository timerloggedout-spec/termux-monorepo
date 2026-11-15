# Sources and Alternatives — SIP-001

Research snapshot: 2026-11-14. This is a source map, not an endorsement or license opinion. Pin exact commits/releases and archive source evidence before implementation.

## A. Primary references

| Candidate | Official source | What it contributes | Caveat / evaluation question |
|---|---|---|---|
| MiroFish original | https://github.com/666ghj/MiroFish | End-to-end knowledge graph → personas → OASIS social simulation → graph memory/report workflow | Backend package metadata declares AGPL-3.0; do not copy/derive code without review |
| MiroFish LICENSE | https://github.com/666ghj/MiroFish/blob/main/LICENSE | Exact upstream license text | Verify against pinned commit and all bundled assets |
| MiroFish backend dependencies | https://github.com/666ghj/MiroFish/blob/main/backend/pyproject.toml | Python range and explicit OASIS/CAMEL dependency pins | Main currently shows Python >=3.11,<3.13; camel-oasis 0.2.5; camel-ai 0.2.78 |
| Refactored MiroFish fork | https://github.com/mj3b/MiroFish | Workbench session core, resource adapters, composable tools, thin Flask API shells; graph storage abstraction with KuzuDB/JSON backends | Fork state and exact license/dependency delta must be reviewed; still AGPL-3.0 per its README |
| CAMEL-AI OASIS | https://github.com/camel-ai/oasis | Social simulation environment, Twitter/Reddit-like platforms, agent actions, configurable agents/models/tools/prompts | Treat headline million-agent scale as an upstream claim, not a target for this project |
| OASIS environment API | https://github.com/camel-ai/oasis/blob/main/docs/key_modules/environments.mdx | `oasis.make`, AgentGraph, platform, SQLite database path, semaphore; reset/step/close lifecycle | Confirm exact API at pinned tag; environment API is not a durable workflow scheduler |
| OASIS quickstart | https://github.com/camel-ai/oasis/blob/main/docs/quickstart.mdx | Installation and model backend setup | Live inference requires provider configuration; not suitable for default CI |
| OASIS license | https://github.com/camel-ai/oasis/blob/main/LICENSE | Apache License 2.0 | Review transitive packages and model/data terms separately |
| OASIS project metadata | https://github.com/camel-ai/oasis/blob/main/pyproject.toml | Package metadata and dependency compatibility | Main currently declares camel-oasis 0.2.5, Python >=3.10,<3.12, camel-ai 0.2.90 |

## B. Critical version-compatibility observation

The current source pages expose a real pin mismatch that must be resolved before selecting a combined environment:

- MiroFish backend `pyproject.toml`: Python `>=3.11,<3.13`, `camel-oasis==0.2.5`, `camel-ai==0.2.78`.
- OASIS repository `pyproject.toml`: Python `>=3.10,<3.12`, package `camel-oasis` version `0.2.5`, dependency `camel-ai==0.2.90`.
- OASIS README latest-updates section reports CAMEL-AI updated to `0.2.90` on 2026-08-19.

Python overlap is 3.11, but CAMEL-AI pins differ. Do not blindly install both projects into one environment or assume the MiroFish lock is current. Gate 0 must produce a resolver-tested, pinned compatibility matrix. Preferred first integration is an isolated process/container boundary with a versioned protocol, subject to the AGPL review—not a shared Python environment.

## C. Alternative simulation and modeling engines

| Candidate | Official source | Best fit | Why compare |
|---|---|---|---|
| Mesa | https://mesa.readthedocs.io/stable/ | Python-native agent-based modeling, AgentSet, model management, browser visualization and data collection | Apache-2.0; strong candidate for deterministic ABM baseline and reproducible policy studies; does not supply OASIS-style social platform semantics by default |
| Repast Suite | https://repast.github.io/ | Scientific ABM; Repast Simphony, Repast HPC and Repast for Python | Repast for Python 1.3.1 (2026-10-22) offers Python-based distributed ABM; assess maturity, runtime and distributed setup |
| NetLogo | https://www.netlogo.org/ | Established agent-based modeling and educational/research environments | Compare model authoring, experiment tooling, headless execution and integration cost |
| In-repo deterministic simulator | Internal baseline | Small synthetic scenarios, policy invariants, golden tests and common-random-number experiments | Must be used as the offline test oracle; intentionally limited ecological validity |

## D. Workflow and agent orchestration alternatives

| Candidate | Official source | Correct role | Boundary |
|---|---|---|---|
| Temporal | https://docs.temporal.io/temporal | Durable execution runtime with event history and recovery across failures | Consider only if QUE-selected execution surfaces cannot meet durable process recovery; do not create a second queue |
| LangGraph | https://www.langchain.com/langgraph | Agent workflow orchestration, state and persistence | Compare as an agent orchestration alternative, not a social simulation environment |
| Existing Workflow Contract / QUE | Repository PR #5388 and `docs/architecture/WORKFLOW-PLANNING-OPERATING-MODEL.md` on `feat/workflow-planning-operating-model` | Declarative intent, admission, dependency planning, routing, execution and evidence | Preferred control-plane integration; preserve QUE authority |
| Existing DoE / ATES | `docs/ops/DOE-FAMILY.md`, `docs/ops/ATES-ORCHESTRATOR-BENCHMARK-PROTOCOL.md` | Experimental design, deterministic evaluation and trace reduction | Reuse existing experiment and trace records |

## E. Upstream lifecycle and integration failure cases

MiroFish upstream issue tracker and simulation runner sources have reported or exposed the following failure classes. Include these as tests; do not assume every fork/version has the same defect:

- all platform agents emit completion but the subprocess remains alive for IPC/interview;
- process-exit-based monitoring can leave the application status stuck at running;
- report availability must wait for successful finalization;
- graph build authentication failures and dead runner recovery need distinct handling;
- subprocess state, IPC session state and simulation completion are separate facts.

Useful upstream references:
- https://github.com/666ghj/MiroFish/issues
- https://github.com/666ghj/MiroFish/blob/main/backend/app/services/simulation_runner.py
- https://github.com/666ghj/MiroFish/issues/855

## F. Source handling rules

1. Use official repository/docs sources before blog posts or social commentary.
2. Record retrieval timestamp, tag/commit SHA, license file and package metadata.
3. Treat forks as independent source candidates; never infer fork contents from upstream.
4. Pin dependencies and test resolver output; do not combine incompatible version assumptions.
5. Record provider/model terms, dataset terms and attribution requirements.
6. Keep AGPL-derived work outside the monorepo until the legal/architecture review explicitly authorizes a path.
7. Treat marketing scale claims as hypotheses; benchmark the target workload and resource envelope directly.

## G. Repository-local reconciliation (2026-11-14)

This section is decisive: upstream alternatives are not treated as blank-slate integrations where the repository already has work.

| Candidate | Existing repository evidence | SIP disposition |
|---|---|---|
| Mesa | `docs/ops/DOE-FAMILY.md` explicitly places Mesa ABM in the control seat for pre-screening and observation, never live evidence. | Keep that authority unchanged. Add to comparison queue as a reference baseline only; any live-engine claim requires a new design and proof. |
| NetLogo | NetLogo appears in the SFI ABM equivalency rehearsal / findings register alongside the Mesa corpus. | Treat as an existing research corpus/reference, not an installed or validated runtime adapter. |
| LangGraph | PR #5045 provisions BIUDL orchestration; #5062 and #5085 are successor autonomous-escalation/recovery work; #5194 includes LangGraph in agentic logistics/control-plane research. | Reuse existing orchestration contracts. Compare LangGraph as orchestration, not as a social simulation engine. No duplicate integration proposal. |
| Temporal | Existing self-host and Temporal-LangSmith adapter; Delphi-cycle workflow and kill/resume evidence; prior durable-execution RFP #1885 has a recorded Oracle pass with five generated candidates. | Reuse the prior RFP and implementation. Do not open a duplicate Temporal RFP. Evaluate only the SIP-specific lifecycle gap that remains after mapping to QUE/WFC and the existing Temporal capability. |
| Delphic / repository graph | Existing graph and decision-analysis substrate, including DoE candidate-packet work. | Reuse as graph/decision-analysis layer; not a social simulator. |

The exact prior Temporal pass is recorded in `docs/proposals/passes/temporal-durable-execution/pass.json` with `status: recorded`. It already ranked and dispositioned five candidates. A fresh Temporal procurement cycle would duplicate existing work.

## H. Expanded candidate slate

The canonical queue is `candidate-queue.json` (`sip.candidate-queue.v1`). It separates role classes so that unlike systems are not ranked in one undifferentiated contest:

- **Workbench/reference:** MiroFish.
- **Social simulation:** CAMEL-AI OASIS.
- **ABM engines:** Mesa, Repast, NetLogo.
- **Offline control:** deterministic in-repository fake engine.
- **Orchestration:** LangGraph, AutoGen, CrewAI, OpenAI Agents SDK.
- **Durable execution:** Temporal (existing capability and prior RFP, not a new procurement item).

Every candidate remains research-only. The queue is not an adoption order, runtime claim, DoE admission, or authority to install software. Source/license/version pins and repository-state reconciliation are required before any executable comparison.
