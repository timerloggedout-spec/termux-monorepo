# Agent Team Orchestration

## Purpose

`termux-monorepo` is an Agentic Development Environment. The optimization target is **teamwork**, not raw model popularity or nominal API price.

A useful route is the one that produces a correct, integrated change with the least wasted human/agent time, redundant context, conflicting edits, retries, and feedback cycles.

## Moneyball / 3L0 model

Treat each agent/model/provider as a player and each orchestration policy as a manager. Managers compete through controlled multivariate experiments; weak policies are culled and strong policies are cherry-picked into the next generation.

The custom 3L0 score is an inference matrix, not a claim of objective model intelligence. It should combine:

- task outcome / acceptance
- useful feedback cycles
- time to integrated result
- latency and requests used
- retry / failure rate
- conflict and duplicate-work rate
- human intervention
- context efficiency
- attribution confidence
- provider availability and quota

`$0` is therefore **not** the ROI metric. Free capacity is valuable only when its return on effort/time/context is better.

## Contributor identity model

Provider ecosystems are contributors to the ADE, but **contributor identity is not GitHub authorship**. The roster separates provider, agent, model, execution adapter, orchestration role, and research/evaluation lane.

Required contributor coverage has two separate populations:

**Agent / collaborator identities** — Gemini CLI, Jules, DeepSeek CI, Devin, CodeRabbit, Copilot, Tembo, Mistral Vibe, the manager/scout/orchestrator workflows, and the operator lane. These identities can review, implement, route, or coordinate only where their real invocation workflow exists. A provider API key is not an agent identity, and an agent's GitHub handle is not its model identity.

**Provider API and research-service lanes** — OpenRouter, FELO, Hugging Face, OmniRoute, Groq, Mistral API, Cerebras, NVIDIA NIM, Aion, LLM7, ModelScope, SiliconFlow, Kilo, OVHcloud, SambaNova, Cloudflare Workers AI, Cohere, and Ollama Cloud. The machine-readable contributor roster tracks these independently from agent roles. Z.ai remains a candidate with an unverified catalog contract, not a completed adapter. Firecrawl's fixed-URL keyless scrape is a public-research service, not an inference provider.

The six-hour [provider availability workflow](../../.github/workflows/provider-availability.yml) follows the canonical catalog-adapter registry. It performs catalog-only probes for configured expanded providers and public LLM7/OVHcloud/ModelScope catalogs; only OpenRouter and Gemini retain inference probes. Unconfigured credentialed providers are not contacted. A passing catalog probe does not prove account entitlement, accepted terms, free quota, inference health, or routing admission. New provider lanes must not be inserted into the agent routing candidate pools unless a real execution adapter and explicit admission contract exist.

Contributor provenance must retain the provider/model/adapter/role dimensions alongside workflow run/job/step, triggering event, PR/issue, SHA, and attribution confidence. A model response incorporated into a commit does not establish provider authorship. PAT owner, commit author, workflow actor, and model provider are separate fields.

The display-moniker SSOT is `docs/ops/AGENT-MONIKERS.md`; capability/routing declarations are in `docs/schemas/agent-roster.yaml`. See Issue #921 for the continuing moniker/role expansion track.

## Team roles

### Manager

Chooses a coordinated plan: sequencing, parallelism, waiting, escalation, and culling. A manager should optimize the whole workstream rather than maximize calls.

### Router

Selects an eligible provider/model from the current live catalog. Model IDs are **data**, not architecture. No model should be hardcoded as a permanent special route when it can be selected from catalog state.

### Dependency-phase admission routing

Agentic-Agile dependency waves are **admission evidence**, not an execution-provider choice. The dependency-phase dispatcher must resolve a manager-approved specialist route before creating an execution claim. The route is resolved from the approved specialist allowlist plus `docs/schemas/agent-roster.yaml` capability routing and records a routing envelope before any specialist adapter runs.

The control path is therefore:

`dependency DAG → wave/readiness → manager policy → specialist route → execution adapter → evidence`

A direct `ready → Jules` path is prohibited because Jules is one bounded specialist in the roster, not the manager or universal execution sink. If the selected specialist has no configured execution adapter, an applied dispatch must stop before claiming work rather than silently falling through to Jules.

### Specialists

Gemini CLI, OpenRouter peers, OmniRoute, Jules, Felo models, and other agents are specialists. Jules is an escalation/specialist worker, not the default sink for every task.

### Evidence collector

Records actual invocations and outcomes. A declared route earns no performance credit until it actually executes.

### Evaluation / PR boundary

Continuous evaluation is a state/evidence loop, not a pull-request generator.

Every observation may update the longitudinal catalog/evidence plane: provider/model eligibility, role routing, invocation telemetry, outcomes, attribution, rankings, and evaluation epochs. A moving live-master SHA is an observation dimension and does not justify opening another PR.

**PR invariant:** create a PR only for a durable implementation or policy change. Do not create PRs for session recon/bind/stamp receipts, live-master refreshes, catalog observations, ranking recalculations, evaluation manifests, or repeated evidence-only skill updates.

The canonical loop is:

`action → observation → outcome → evidence/catalog → next selection → next evaluation`

Evaluation identity must preserve `run_id + run_attempt + head_sha + manager + task/cohort + provider + model + role`. Preserve the catalog snapshot/hash used for each epoch so rankings remain reproducible without freezing runtime catalog state.

The repository's PR scope guard closes session/evaluation-only PRs as **not planned** when they cross this boundary. That guard is containment; the evidence/ledger is the system of record.


## Dynamic libraries and parallelism

The provider/model library is continuously expanding. `continuous-evaluation.yml` therefore builds its MVT matrix from the **live provider catalogs on every run** instead of maintaining a fixed five-model list.

A newly discovered eligible model can become a treatment automatically; a disappeared model becomes stale/unavailable evidence rather than a permanent routing failure.

The workflow deliberately does **not** specify `strategy.max-parallel`. GitHub's default behavior maximizes matrix jobs according to runner availability. GitHub still imposes platform/account limits, including a documented maximum of 256 matrix jobs per workflow run; those are platform constraints, not an application-imposed concurrency ceiling. The manager should optimize admission, quota, cooldown, and sequencing rather than encode an arbitrary local `max-parallel` number.

The long-term matrix is:

`project + scope + task + cohort + provider + model + prompt + manager + sequencing + validation`

This permits simultaneous A..Z lanes when capacity and task independence justify them while retaining the ability to wait when downstream context depends on another lane.

## Synchrony, not fallback drift

The intended behavior is cooperative orchestration:

1. classify the work
2. split independent work
3. run genuinely independent tasks concurrently
4. wait when downstream context depends on another agent
5. ingest the useful response once
6. integrate once
7. escalate only when the team lacks a needed capability

"Fallback" should not mean a permanent hierarchy such as Gemini-primary → OpenRouter-secondary → Jules. It should mean **dynamic recovery from unavailable capacity or an unmet capability**.

The conductor must prevent duplicate work, conflicting writers, stale-SHA work, needless parallel prompt consumption, and quota waste.

## Adaptive waiting / steering

Latency is primarily a **lead/lag and control signal**, not a correctness score.

A long-running task should continue while it produces useful state change, evidence, computation, or a changing response. A manager should distinguish:

- progressing → keep waiting
- useful new evidence → keep waiting
- slow but active → keep waiting
- repeated identical state → investigate loop
- no evidence + repeated action → steer/retry conditionally
- verified failure → diagnose and route

There is no arbitrary short request timeout in the HTTP invocation action. Provider/model output is requested up to the currently observed capability rather than a fixed 4096-token ceiling; actual `finish_reason`, output tokens, and provider constraints remain separate observations.

## Live provider/quota evidence

Catalog polling is dynamic and provenance-bearing. It records model IDs, context, published pricing/access classifications, documented trial evidence, discovery timestamps, and safe provider response metadata.

For Felo, the current official OX Alpha documentation identifies model `ox-alpha` as a free-trial route with 1M context and 128K maximum output. The public Felo Harness documentation also documents 200 daily free credits for Free Standard accounts for Search API; **account-level remaining balance is not assumed from that public entitlement**. Account/quota state must be treated as observed only when the authenticated provider API or response headers actually exposes it.

Every invocation records safe operational metadata such as request ID, rate-limit/quota/credit response headers when present, HTTP status, tokens, completion state, and error class. Credentials are never persisted.

If an authoritative Felo account/balance endpoint becomes documented or discoverable, the catalog/manager should add it as an explicit account-observation source rather than guessing a dashboard endpoint.

## Agent attribution

GitHub commits/comments may be authored through the repository owner's PAT and therefore appear under `timerloggedout-spec`. Git identity alone is insufficient attribution.

Build a provenance layer that correlates:

- workflow run/job/step
- event and issue/PR number
- head SHA
- commit SHA and parent
- comment timestamp/body markers
- workflow actor and triggering actor
- provider/model invocation telemetry
- session/export provenance when available

The provenance layer must expose an **attribution confidence** value rather than pretending uncertain identity is known.

Chat/session export harvesting, fragment matching, and provenance reconstruction can be used as a conceptual template for backfilling historical agent attribution. Historical attribution must remain explicitly inferred.

## Performance index

The performance index has two populations:

1. **execution observations** — what actually ran
2. **interaction observations** — what each agent contributed to the integrated result

Do not score an agent merely because a workflow claims it selected that agent.

Minimum observation identity:

`manager + task + role + provider + model + workflow_run + head_sha`

Recommended experiment identity:

`manager + policy_version + cohort + task_family + task_instance`

This permits multivariate testing of manager policies, model mixes, prompt budgets, concurrency, and sequencing.

## Task outcome and evidence quality

`PASS/FAIL` is the task-level outcome and must carry notes/evidence. It is not interchangeable with route execution status.

An observation should distinguish, where relevant:

- task outcome: PASS / FAIL / UNKNOWN
- correctness / working state
- tests and verification
- warnings/errors and severity
- integration status
- relevant Big-O / compute characteristics
- requests/tokens/quota consumption
- context/prompt efficiency
- human intervention
- latency
- provider/dispatch/manager failure class

Latency never upgrades a wrong result. A slow verified result can outrank a fast incorrect result.

## Promotion / culling

Managers should be promoted only after sufficient observations and should be compared on confidence intervals or equivalent uncertainty-aware statistics. Do not crown a model after one successful run.

Cherry-pick useful policies into the next experiment generation. Cull policies that repeatedly waste requests, create conflicts, require excessive human intervention, or fail to integrate results.

## OpenRouter / Felo promotional capacity

Promotional/free capacity is an experiment opportunity, not a hardcoded route. The catalog must record promotion metadata when available:

- provider
- model
- pricing classification
- promotion identifier
- start/end time if published
- discovery timestamp
- source URL
- eligibility/terms

The scheduler should exploit a verified promotional window while it is open, but must degrade gracefully when it expires. No workflow should require a promotional model by name.

`FELO_AI_API` is treated as an available provider credential when a workflow explicitly supports that provider; secrets are never written to source, logs, artifacts, or telemetry.

## Human UX and agent sovereignty

Agents should have clear bounded authority, observable decisions, and durable handoff state. Humans should be able to inspect why an agent was selected, what it consumed, what it produced, and why another agent was or was not invoked.

The goal is an environment where agent autonomy and human UX reinforce each other rather than competing.


## BIUDL execution and author provenance implementation

The cross-lane implementation/acceptance contract is indexed in
[`docs/ops/BIUDL-EXECUTION-AND-PROVENANCE.md`](BIUDL-EXECUTION-AND-PROVENANCE.md).
The event-level author contract is
[`docs/ops/AGENT-THROUGHPUT-EVENT.schema.json`](AGENT-THROUGHPUT-EVENT.schema.json).

For PAT-mediated activity, keep `github_actor` and `triggering_actor` separate
from the `author` attribution object. A workflow-name mapping can identify a
known provider/role at workflow level, but it cannot prove which model generated
a particular line of code. `model`, settings fingerprint, and context fingerprint
remain null unless trusted invocation/task-boundary evidence supplies them.
Settings/context values are SHA-256 fingerprints only; never persist raw prompts,
completions, credentials, or session context.

The existing read-only ATES observer now includes the known manager, scout, and
orchestrator workflow cohort plus selected Gemini, DeepSeek, and Jules execution/review
lanes. Bridge/tunnel health (including Pinggy) remains a separate infrastructure receipt
and is deliberately excluded from agent-throughput task counts. The observer retains
run/attempt/SHA linkage, records attribution confidence and evidence references, and
does not infer a model from the PAT owner. The citation curator and index are documented
in `docs/briefing/SOURCE-CITATION-INDEX.md`.

## Agentic-Agile work contracts and waves

The orchestration layer now adopts a thin Agentic-Agile process contract. A dispatchable unit should have an observable objective, bounded scope, explicit ownership, dependencies, acceptance evidence, negative constraints, authority tier, and runtime policy before wave admission.

Independent units may execute in parallel only after ownership and dependency checks pass. Dependent work waits for an explicit review/evidence gate. A successful workflow termination is not itself a wave-completion proof.

The canonical lifecycle is:

`INTAKE → SPECIFY → DECOMPOSE → OWNERSHIP/DEPENDENCY CHECK → WAVE ADMISSION → PARALLEL EXECUTION → REVIEW GATE → EVIDENCE VALIDATION → INTEGRATION → RETROSPECTIVE → NEXT WAVE`

The existing runtime observer remains nested inside execution:

`ACT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD`

Retrospectives should classify process gaps separately from task outcomes (specification, decomposition, execution, verification, integration, governance, and environment). Repeated findings should become durable skills, templates, tests, or workflow changes.

See `docs/ops/AGENTIC-AGILE-PROCESS-INTEGRATION.md` for the adopted contract and gate rules.


## Canonical phase-engine integration

Agentic-Agile waves are implemented as a process layer over the existing dependency-phase control plane, not as a second scheduler. The canonical lifecycle state remains in `docs/agentic/dependency-phases.json`, `phase-approvals.json`, the deterministic phase engine, and current GitHub evidence.

Accordingly, a future manager should ask the phase evaluator for readiness before dispatch, use its `ready/running/awaiting_review/blocked/complete` state as the lifecycle boundary, and derive wave membership from the existing dependency graph. Generated views and agent prose remain advisory.

Do not create a competing `agentic-agile.yaml` or duplicate claim/idempotency protocol. Extend the phase engine when additional Agentic-Agile metadata is needed.
