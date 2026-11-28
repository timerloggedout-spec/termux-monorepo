# Benchmark Family Registry — cross-domain agent evaluation

**Snapshot:** 2026-11-19  
**Authority:** Agent Evaluation Framework (AEF) + this family registry  
**Purpose:** register comparable task families, preserve native metric semantics, and route every run through the existing DoE / QUE / compute / provenance / 3L0 / MoneyBall planes.

This registry extends the existing AEF and SWE cohort registry while preserving their scoring authorities and recording adapter admission state.

## 1. Operating rule

A benchmark family is a task-and-verifier contract with native score semantics. Every adapter MUST bind an immutable benchmark version, task set, environment image/digest, verifier version, source revision, agent treatment, and execution receipt. Every dispatched task instance produces one run record and one DoE experiment record.

**Comparability rule:** keep native metrics native. SWE-bench resolution, Terminal-Bench resolution rate, BFCL function-call accuracy, τ-bench pass^k, OSWorld task success, MLE-bench medal rate, and memory accuracy/latency are distinct measures. The fleet compares treatments within each family and builds a multi-axis portfolio view; raw family scores retain their native scales.

**Authority separation:**
- AEF owns the evaluation taxonomy and treatment contracts.
- Benchmark adapters own benchmark-specific setup, task identity, and verifier invocation.
- QUE / Temporal / compute mesh own admission, scheduling, placement, retry, and checkpoint execution.
- `chat-provenance/v1` and execution receipts own attribution evidence.
- DoE owns preregistration, arm assignment, repetitions, and stopping rules.
- 3L0 consumes confirmed dispatch outcomes for agent/provider suitability.
- MoneyBall remains a separate valuation plane and consumes verified artifacts under its own authority; 3L0 and benchmark-native scores retain their own records.
- ForeSight / HindSight project evidence while AEF and benchmark verifiers retain result authority.

## 2. Status vocabulary

| Status | Meaning |
|---|---|
| **IN-REPO** | A canonical registry, adapter, or contract exists in the current repository. |
| **EXECUTED** | A run receipt proves a specific execution. This status is scoped to that run and version. |
| **WIRED** | An automated trigger or adapter is present; execution still requires receipts. |
| **CANDIDATE** | Evaluated for adoption; production adapter admission awaits a verified run receipt. |
| **RESEARCH** | External benchmark or instrument retained for comparison. |
| **GATED** | A specific access, safety, resource, or verifier condition blocks admission. |
| **UNVERIFIED** | Evidence is insufficient to assign a stronger state. |

Repository mentions, workflow dispatches, task executions, and benchmark resolutions are four distinct states. Infrastructure checks and benchmark passes also retain separate evidence.

## 3. Current in-repository baseline

The existing `docs/architecture/AGENT-EVALUATION-FRAMEWORK.md` and `docs/evaluations/swe-performance/COHORTS.md` already provide these families or contracts:

| Family | Existing evidence | Current interpretation |
|---|---|---|
| SWE-agent treatment cohort | `swe-agent-fork`, `mini-swe-agent-fork`; pinned mini-SWE revision and bounded reference workflow | **IN-REPO** reference cohort; preserve exact fork SHA per run |
| SWE-bench Full / Lite / Verified | Named in SWE cohort registry | **IN-REPO** cohort definitions; benchmark execution is separately receipted |
| SWE-bench Multimodal / Multilingual / Live | Named in SWE cohort registry | **IN-REPO** cohort definitions; task and modality setup remains versioned |
| Repository-history replay | AEF family | **IN-REPO** internal evaluation family |
| Custom environment | AEF family | **IN-REPO** internal evaluation family |
| Deterministic regression | AEF family | **IN-REPO** correctness control |
| Trajectory validation | AEF family | **IN-REPO** trajectory/evidence control |
| Tool/API boundary | AEF family and external instrument registry | **IN-REPO** family; adapters vary by instrument |
| Tool-definition quality (TDQS) | `she/metrics/tdqs.py`, `tests/test_tdqs.py`, `docs/ops/TDQS-ADMISSION-MATRIX.md`, `docs/ops/TDQS-EVIDENCE.schema.json` | **IN-REPO** deterministic extraction/aggregation and evidence schema; external evaluator supplies rubric dimensions |
| Cognitive regression | AEF family | **IN-REPO** internal family |
| Oversight / security | AEF family and governance assurance instruments | **IN-REPO** family; specific external benchmark adapters remain selective |
| Patch quality / long-horizon / adversarial robustness | AEF dimensions | **IN-REPO** evaluation dimensions; each requires an explicit task and scorer contract |
| Orchestration / provider-model / manager-team policy / scout selection | AEF dimensions | **IN-REPO** treatment dimensions; evaluate with matched tasks and recorded dispatch lineage |

The existing mini-SWE adapter is a bounded reference implementation; QUE and Temporal remain the fleet scheduling authorities. Its benchmark-resolution field remains distinct from task execution. The full SWE-agent fork remains a candidate reference treatment pending its adapter and independent scorer.

## 4. External benchmark portfolio

The following is a prioritized portfolio for the next adapters. Each row is a candidate/research instrument until an in-repository adapter and execution receipt are linked.

| Priority | Family / instrument | What it measures | Native result semantics | Proposed fleet use | Admission state |
|---|---|---|---|---|---|
| P0 | **Terminal-Bench 4.1** | Real terminal work across software, science, ML, operations, security, hardware, and media tasks | Task resolution rate with trial-level outcomes and confidence intervals | Primary complement to SWE-bench for terminal-native agent work; pin 4.1 tasks, Harbor image, verifier SHA, resource profile, and trial artifacts | **CANDIDATE — local adapter implementation pending** |
| P1 | **SWE-bench Pro / SWE-bench-Live** | More demanding and/or continuously refreshed software engineering tasks | Dataset-specific patch resolution | Add as distinct cohorts beside Full/Lite/Verified; preserve task release and contamination window | **RESEARCH / CANDIDATE** |
| P0 | **MCPMark** | Realistic MCP tasks with curated initial state and programmatic verification across CRUD and multi-step interactions | pass@1 and pass^4 | Highest-fit external MCP workflow benchmark; build a local/synthetic server cohort from the 127-task suite and preserve programmatic effect checks | **CANDIDATE — local adapter implementation pending** |
| P0 | **DynamicMCPBench** | Live MCP server workflows, trace-grounded effect checkpoints, and multi-step tool execution; paper reports 24 models, 121 servers, and 750 tasks across 15 categories | pass^3 over independent attempts; task effects rather than final-answer matching | Best candidate for repeatable evaluation of the fleet's own MCP servers; start with sandbox servers and synthetic data | **CANDIDATE — local adapter implementation pending** |
| P1 | **MCP-Atlas** | Real MCP servers/tools with natural-language tasks requiring multi-server discovery and orchestration | Claims-based partial credit plus tool discovery, parameterization, syntax, recovery, and efficiency diagnostics | Cross-server orchestration and tool-selection benchmark; use public subset first | **CANDIDATE — local adapter implementation pending** |
| P1 | **MCPAgentBench** | Real-world MCP definitions with simulated tools and distractor tool lists | Task completion and execution efficiency | Tool discovery/selection and difficulty-aware evaluation using simulated tool execution | **CANDIDATE — local adapter implementation pending** |
| P1 | **MCP-Bench** | Multi-step tasks across live MCP servers and complementary tools | Multi-faceted tool/schema, planning, and task-completion score | Cross-domain tool coordination and intermediate-output grounding | **CANDIDATE — local adapter implementation pending** |
| P1 | **BFCL v4** | Function/tool calling, multi-turn use, irrelevance detection, web search, and memory dimensions | Category accuracies and published overall accuracy | Tool-schema correctness and API selection; map function names/arguments to tool contract tests | **CANDIDATE — audit task defects before promotion** |
| P1 | **OSWorld** | Multimodal agents operating real desktop and web applications across multi-app workflows | Per-task environment-state success | Computer-use and GUI workflow treatment; requires isolated desktop VM/emulator and deterministic state reset | **CANDIDATE — resource-gated** |
| P1 | **WebArena / WebArena-Verified / VisualWebArena** | Realistic self-hosted browser tasks, visual and DOM/accessibility observations | Task functional correctness | Browser navigation, multi-step forms, retrieval, transactions, and state mutation; use BrowserGym as a possible adapter harness | **CANDIDATE — self-hosted environment required** |
| P2 | **WebArena-Pro** | New multimodal browser benchmark with 300 tasks across 20 self-hosted applications and six domains, including audio/video observations | Task-level success with reproducible isolated runs | Research candidate for multimodal browser and cross-application work; validate task release and verifier maturity before admission | **RESEARCH — recent preprint** |
| P1 | **BrowserGym / AgentLab** | Reusable benchmark execution environment across MiniWoB, WebArena, WorkArena, AssistantBench, WebLINX, TimeWarp, and related suites | Benchmark-specific metrics | Reuse as harness where its supported benchmark fits; keep each benchmark ID/version distinct | **RESEARCH / CANDIDATE** |
| P1 | **τ²-bench / τ³-bench lineage** | Tool-agent-user interaction under written policies and evolving backend state; text and voice tracks | pass^k / task success under benchmark protocol | Policy compliance, customer-service workflows, tool side effects, and repeated reliability | **CANDIDATE — pin exact generation and grading revision** |
| P1 | **ToolSandbox** | Stateful conversational tool use, implicit state dependencies, intermediate/final milestones | Trajectory milestone and final-state correctness | Internal API and workflow integration evaluation; strong complement to single-turn function-call tests | **CANDIDATE** |
| P2 | **GAIA** | General assistant tasks requiring multi-step reasoning, tools, and heterogeneous evidence | Task answer correctness under GAIA protocol | Broad assistant capability and retrieval/reasoning control; preserve level and release | **RESEARCH / CANDIDATE** |
| P2 | **AgentBench** | Multiple interactive environments: OS, DB, knowledge graph, games, puzzles, household, shopping, browsing | Original suite composite and environment-specific results | Broad cross-environment screening; distinguish original 8-environment, OS-only ports, and AgentBench FC variants | **RESEARCH / CANDIDATE** |
| P2 | **AndroidWorld** | Autonomous Android agents across real apps on an emulator, with dynamically parameterized tasks | Programmatic per-task success | Termux/mobile workflows, app navigation, device-side automation and recovery | **CANDIDATE — device/emulator lane required** |
| P2 | **MLE-bench** | 75 Kaggle ML engineering competitions; data preparation, training, experiments, model evaluation | Any Medal (%) by Low/Lite, Medium, High, and All splits; at least 3 seeds recommended | Evaluate ML Ops agents; full canonical setup is 24 hours, 36 vCPU, 440 GB RAM, and one 24 GB A10 GPU. Low/Lite covers 22 competitions. Competition datasets retain their individual license and access terms. Upstream leaderboard submissions are paused per the 2026-04-24 notice | **CANDIDATE — resource/data-license gated** |
| P2 | **AgentDojo** | Prompt-injection attacks and defenses in dynamic tool-using agent environments | Attack success / defense success by task and scenario | Security and trust-boundary tournaments; run only in isolated, synthetic environments | **CANDIDATE — security gate** |
| P2 | **LongMemEval / LongMemEval-V2** | Information extraction, multi-session and temporal reasoning, knowledge updates, abstention; V2 adds trajectory-derived experience and query latency | Accuracy and latency | HindSight / ForeSight memory quality and retrieval regression; preserve data split and privacy rules | **CANDIDATE — privacy and dataset gate** |
| P2 | **METR time-horizon evaluations** | Task duration and agent success over increasing task horizons | Horizon curves / fitted time horizon | Long-running agent reliability and planning depth; pair with checkpoint/recovery and intervention telemetry | **RESEARCH** |
| P2 | **Terminal-Bench-Science 0.1** | Scientific research workflows executed in terminal environments | Benchmark-specific task success | Scientific-compute agents and reproducible research workflows | **RESEARCH / CANDIDATE** |

### 4.1 Terminal-Bench 4.1 admission notes

Terminal-Bench 4.1 is the immediate next terminal benchmark. Its November 9, 2026 release hardens verifier correctness and resistance to reward hacking. The release re-grades saved 4.0 artifacts with updated verifiers; the official release notes report 162 trials changing score, manual review of 134 expected changes and 28 measurement discrepancies, and all updated agent scores remaining within the original 4.0 confidence intervals. The release also describes a separate-process `Worker` boundary for untrusted agent-authored code, with cleanup before the trusted grader reads the result.

Implementation consequences:

1. Store benchmark version `terminal-bench/4.1`, task ID, task revision, environment digest, Harbor version, RewardKit/verifier revision, agent harness revision, and artifact URI.
2. Preserve the original 4.0 result and 4.1 regrade as linked immutable observations.
3. Preserve the published 4.0 confidence interval when a saved artifact is regraded; record score deltas and the release's measurement-discrepancy class.
4. Execute untrusted candidate code in an isolated worker/process/container; the trusted verifier owns the reward file and grading state.
5. Capture full trajectory artifacts under the benchmark's policy and scrub secrets before any fleet telemetry projection.
6. Start with a small CPU-only slice only after resource and environment checks; expand by task/domain after receipt and verifier stability are demonstrated.
7. Keep terminal-benchmark scores separate from SWE-bench patch-resolution scores.

### 4.2 Benchmark quality and contamination controls

- **BFCL v4:** its official leaderboard describes tool-call, multi-turn, and agentic categories. An external September 2026 audit sampled 50 tasks and reported defects affecting 24. Use task-level issue annotations and an independent local sanity set before treating its composite as a high-confidence decision input.
- **MLE-bench:** upstream's GitHub page stated on April 24, 2026 that new leaderboard submissions were paused while submission fairness was improved. Internal use remains possible subject to its license and setup requirements; label results as internal reproductions rather than official leaderboard submissions.
- **AgentBench:** distinguish the original eight-environment benchmark, the OS-only `inspect_evals` port, and the newer AgentBench FC variant. Label each port and suite separately; preserve the original full-suite AgentBench metric semantics.
- **Web and desktop environments:** task state, account credentials, reset fixtures, network access, and application versions are part of the environment fingerprint. Use synthetic accounts and seeded data.
- **Long-memory suites:** retain dataset permissions, split identity, privacy boundaries, retention rules, and abstention behavior. Evaluate memory recall separately from memory write volume.
- **All families:** pin data and verifier revisions; track known contamination, task exposure, benchmark saturation, reward-hack disclosures, and scorer changes.

## 4.3 MCP-specific portfolio and existing TDQS lane

The MCP-specific portfolio is the highest-priority addition for this repository. The current repo search identifies MCPMark, DynamicMCPBench, MCP-Atlas, MCPAgentBench, MCP-Bench, and OSWorld-MCP as external candidates awaiting adapter registration. **TDQS is already implemented locally** and forms the static quality preflight.

| Instrument | Distinct value | Fleet integration |
|---|---|---|
| **TDQS** | Static quality of MCP tool definitions: purpose, usage guidance, behavioral transparency, parameter semantics, structure, and context completeness | **IN-REPO.** `she/metrics/tdqs.py` implements deterministic context extraction, hard gates, aggregation, tiers, and server rollups; `tests/test_tdqs.py` covers fixtures; `TDQS-ADMISSION-MATRIX.md` defines gh-mcp, termux-mcp, and Toolshed cohorts. The external rubric evaluator remains a separate provider/evaluator lane. |
| **MCPMark** | 127 curated real-world MCP tasks with curated initial state and programmatic verification; includes CRUD and multi-turn interactions | Best first static/reproducible MCP task cohort. Pin task set and state fixture; record pass@1 and pass^4 independently. |
| **DynamicMCPBench** | Live MCP servers, successful trace construction, path-agnostic effect checkpoints, and replayable state changes | Best candidate for testing the actual fleet's own MCP servers. Run against synthetic accounts and isolated sandboxes; score effects rather than response prose. |
| **MCP-Atlas** | 36 real MCP servers, 220 tools, 1,000 tasks with a 500-task public subset; natural-language tasks require multi-tool/multi-server planning | Cross-server discovery, selection, and orchestration. Preserve partial-credit claims and diagnostic metrics. |
| **MCPAgentBench** | Simulated MCP tools based on real definitions, with distractor tool lists and difficulty-aware tasks | Controlled tool discovery/selection experiments without live external-server dependency. |
| **MCP-Bench** | Multi-step workflows across 28 representative MCP servers and 250 tools | Cross-tool coordination, parameter control, and intermediate-result grounding. |
| **OSWorld-MCP** | Combined computer-use, MCP tool invocation, and decision-making in a real-world GUI environment | Research candidate after OSWorld/BrowserGym environment admission. |
| **TDQS public specification** | Tool-definition rubric and server-coherence scoring | Track public spec version separately from the local implementation; the repo's TDQS module currently declares v1.3. Reconcile upstream version drift before any rubric update. |

### MCP adapter order

1. Reuse TDQS for static `tools/list` schema quality and tool/server coherence.
2. Add MCPMark as the first deterministic task suite with curated initial state and programmatic verifier.
3. Add DynamicMCPBench against the fleet's own synthetic MCP servers for stateful, effect-based validation.
4. Add MCP-Atlas / MCPAgentBench for cross-server discovery and distractor handling.
5. Add MCP-Bench and OSWorld-MCP as broader research tracks after the first adapters are stable.

This order maximizes reuse: TDQS provides a cheap preflight signal for every server/tool schema change, while task benchmarks measure actual behavior. A good tool description measures schema clarity; a passing task measures behavior. Keep both complementary measurements.

## 5. Canonical run envelope

Every benchmark adapter MUST emit or join the following envelope. Existing schemas may supply fields; this table is the target crosswalk to canonical data stores.

| Field | Purpose |
|---|---|
| `benchmark_id`, `benchmark_version`, `task_id`, `task_fingerprint` | Stable benchmark and task identity |
| `source_revision`, `task_revision`, `verifier_revision` | Reproducibility and re-grade lineage |
| `environment_digest`, `resource_profile` | Reproducible runtime and allocation |
| `experiment_id`, `arm_id`, `instance_key`, `seed`, `replicate` | DoE assignment and repeated-trial identity |
| `dispatch_id`, `attempt_id`, `workflow_run_id`, `worker_id`, `surface_id` | Queue, scheduler, worker, and compute provenance |
| `agent_id`, `provider`, `model`, `endpoint`, `prompt_hash`, `tool_hash` | Treatment identity and attribution |
| `started_at`, `ended_at`, `latency_ms`, `tokens`, `cost`, `retries` | Resource and efficiency measurements |
| `outcome_status`, `native_score`, `native_metric`, `verifier_result` | Native outcome semantics |
| `artifact_refs`, `trajectory_ref`, `stdout_ref`, `stderr_ref`, `redaction_receipt` | Evidence pointers and safety proof |
| `supersedes`, `regrade_of`, `parent_attempt_id` | Retry, resume, and regrade lineage |

The envelope should reference canonical artifacts instead of copying whole transcripts, tool payloads, or private data into multiple stores. Credentials remain names/refs only. An unconfirmed outcome remains observational.

## 6. Execution and scheduling contract

The benchmark portfolio uses the existing system-managed execution path:

`benchmark registry → task/seed registry → DoE preregistration → QUE admission → Temporal/worker execution → compute mesh placement → provenance + verifier receipt → native result → ForeSight/3L0/MoneyBall projections`

- Schedules discover eligible work; QUE owns admission and leases.
- Temporal owns durable long-running workflow history, retry policy, and checkpoint/recovery where its deployed integration is proven.
- GitHub Actions owns event triggers, bounded orchestration, and CI gates; route bulk compute to allocated VM/worker surfaces.
- Muse owns existing daily/long-running orchestration and ML Ops/HindSight workloads as recorded in the allocation registry.
- Hark owns bounded, isolated evaluation/export/hygiene slices when its current lease and capacity are verified.
- The inference pool supplies model inference; benchmark execution and result ledgers remain separate authorities.
- Retries are idempotent by `dispatch_id + task_fingerprint + attempt_id`; an uncertain side effect is reconciled before replay.
- Checkpoints and receipts allow unclaimed work to be safely reallocated after host loss.
- Schedules and QUE own recurring operation; manual dispatch remains an authorized entry point.

## 7. Prioritized adapter sequence

| Slice | Deliverable | Exit condition |
|---|---|---|
| B0 | Registry + canonical envelope | Existing AEF and SWE cohort docs link here; schema crosswalk is reviewed |
| B1 | Terminal-Bench 4.1 adapter pilot | Pinned Harbor/task/verifier; CPU slice; isolated verifier; complete receipts; repeatable re-grade |
| B2 | Tool-use adapter (BFCL v4 + ToolSandbox) | Function/schema correctness and stateful multi-turn outcomes recorded separately |
| B3 | Browser / desktop adapter (BrowserGym + WebArena, then OSWorld) | Reproducible synthetic accounts, state resets, screenshots/DOM evidence, and deterministic verifier |
| B4 | Memory / policy adapter (LongMemEval + τ²-bench) | Memory/privacy gates, policy compliance, pass^k, and abstention captured |
| B5 | Mobile + ML engineering (AndroidWorld + MLE-bench) | Dedicated resource profile, device/GPU access evidence, and reproducible run receipts |
| B6 | Multi-agent and long-horizon tournament | Matched task set, manager/team policies, seed/repetition plan, intervention accounting |

## 8. Promotion gates

A benchmark adapter becomes **WIRED** only after:
1. The source and license are reviewed.
2. Benchmark/task/verifier revisions are pinned.
3. Environment isolation and reset behavior are demonstrated.
4. The adapter emits the canonical run envelope and a redaction receipt.
5. A deterministic fixture passes and a small live run produces an immutable receipt.
6. Failure, timeout, cancellation, retry, worker loss, and regrade paths are exercised.
7. Native score semantics and confidence/repetition requirements are documented.
8. The adapter is added to the registry with exact commit and test evidence.

Promote a treatment after replicated, independently verified outcomes and a separate governance review. Benchmark scores inform decisions within existing routing, credential, spending, and safety controls.

## 9. External source register

- Terminal-Bench 4.1 release: https://www.tbench.ai/news/terminal-bench-4-1
- Terminal-Bench current benchmark/leaderboard: https://www.tbench.ai/
- SWE-bench-Live: https://swe-bench-live.github.io/
- BFCL v4: https://gorilla.cs.berkeley.edu/leaderboard.html
- MCPMark: https://proceedings.iclr.cc/paper_files/paper/2026/hash/8138d211ce8790fdfbeeeb9781838a37-Abstract-Conference.html
- DynamicMCPBench: https://aclanthology.org/2026.emnlp-industry.202/
- MCP-Atlas: https://arxiv.org/abs/2602.00933
- MCPAgentBench: https://aclanthology.org/2026.realm-1.51/
- MCP-Bench: https://github.com/Accenture/mcp-bench
- OSWorld-MCP: https://openreview.net/pdf/91303321154efd692e9af4570fc166b9d9b43efe.pdf
- WebArena-Pro: https://arxiv.org/abs/2611.17955
- TDQS: https://tdqs.dev/spec
- BFCL v4 independent quality review: https://epoch.ai/benchmarks/berkeley-function-calling-leaderboard/review
- OSWorld: https://os-world.github.io/
- BrowserGym: https://github.com/ServiceNow/BrowserGym
- WebArena: https://webarena.dev/
- τ²-bench: https://github.com/sierra-research/tau2-bench
- ToolSandbox: https://machinelearning.apple.com/research/toolsandbox-stateful-conversational-llm-benchmark
- GAIA: https://huggingface.co/gaia-benchmark
- AgentBench: https://github.com/THUDM/AgentBench
- AndroidWorld: https://github.com/google-research/android_world
- MLE-bench: https://openai.com/index/mle-bench/ and https://github.com/openai/mle-bench
- AgentDojo: https://agentdojo.spylab.ai/
- LongMemEval: https://proceedings.iclr.cc/paper_files/paper/2025/hash/d813d324dbf0598bbdc9c8e79740ed01-Abstract-Conference.html
- LongMemEval-V2: https://github.com/xiaowu0162/LongMemEval-V2

**Snapshot:** external benchmark releases and leaderboards evolve. Refresh upstream release notes and licenses at adapter admission; this registry is a dated source map.
