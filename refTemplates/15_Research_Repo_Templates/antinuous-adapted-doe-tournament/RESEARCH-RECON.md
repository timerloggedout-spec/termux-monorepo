# Antinuous RECON — evidence ledger

**Snapshot:** 2026-11-22  
**Research target:** https://antinuous.com/  
**Disposition:** reference architecture candidate; this recon uses public sources and repository materials. Live account execution remains a separate validation gate.

## Evidence classes

| Class | Meaning | Use |
|---|---|---|
| P — primary | Official website, legal terms, pricing, official repository | Establish what the source says |
| R — repository | Public GitHub repository, code or issue | Establish publicly visible code and project activity |
| I — independent | Independent reproduction, third-party evidence | Validate claims outside source owner |
| A — analysis | Architectural inference or proposed adaptation | Guide our design; label architectural inference separately from upstream fact |

## Product capability claims

The public Antinuous product describes an autonomous research and compute environment combining research planning and agent delegation; parallel agent swarms; isolated computers and compute workers; scientific/engineering simulation and data-source access; research artifacts and source-linked results; iterative candidate evaluation; external agent access through MCP and A2A; and optional GPU execution/external compute account integration.

**Evidence status:** P — company-published capability descriptions.  
**Independent status:** this recon contains no independent validation evidence.  
**Adaptation:** build equivalent capability contracts as modular providers; qualify vendor APIs through explicit adapter evidence.

## Commercial and performance claims

The website advertises a throughput/cost proposition and reports swarm/compute speedups and research completion statistics. Pricing is organized into subscription tiers with AI usage allowances and compute capabilities.

**Evidence status:** P — company-reported marketing and pricing.  
**Independent status:** equal-budget, equal-quality reproduction evidence remains unestablished.  
**Tournament treatment:** retain claim text, capture date, workload definition, baseline, worker count, hardware, model, quality score, total cost and repetitions before comparison.

Report productivity after equal-quality acceptance and full resource accounting.

## Security and trust

Official privacy and terms materials describe collection and processing of account data, prompts, files, research records and connected-account context; third-party processors; user ownership/license provisions; generated-output limitations; retention and liability provisions.

Independent audit evidence for SOC 2, penetration testing, tenant-isolation verification, encryption design, customer-managed keys and enterprise SLA remains an open verification gate in this recon.

**Evidence status:** P — published policy/terms statements.  
**Independent status:** I — technical controls remain unverified.  
**Adaptation:** require explicit data classification, adapter permission scopes, redaction, environment isolation, retention, secret boundaries and provenance receipts.

## Public GitHub recon

The user-provided GitHub repository search was reviewed. The public Antinuous organization includes Mojo-oriented repositories such as antinuous/mojo-flare, antinuous/mojo-json, antinuous/protomojo, antinuous/grpc-mojo, antinuous/mojo-http2, antinuous/mojo-net, antinuous/mojo-tls and antinuous/mojo-mozz.

These repositories demonstrate a public Mojo software footprint. These repositories demonstrate a public Mojo software footprint; hosted-platform implementation evidence remains a separate verification item.

The exact-name issue search surfaced unrelated issue text containing “Antinuous”; identity and relevance checks are required before attributing an issue to the company or product.

## Comparative architecture patterns

### Agentic Swarm Research

Public repository describes config-packaged swarm topology, orchestrator/researcher/synthesizer/critic roles, structured tool-call communication, worker pools, tournament synthesis, token budgets and shared SQLite context.

**Adaptation:** versioned topology packages, explicit bridge contracts, bounded workers, critic pass and tournament synthesis.

### Autonomous Agentic Research Swarm

Public repository describes Operator/Planner/Worker/Judge roles, per-task Git worktrees, declared file ownership, deterministic quality gates and run manifests.

**Adaptation:** isolated workspaces, declared write sets, judge independence, manifest-first provenance and acceptance gates.

### SwarmResearch

Public repository describes explorer/optimizer populations, branch isolation, parent selection, diversity steering and iterative search.

**Adaptation:** evolutionary manager-policy populations, lineage and controlled variation; retain independent task cohorts and avoid score leakage.

## Termux MonoRepo implementation recon

The branch was inspected against the existing repository contracts and code:

| Surface | Source-derived finding | Adaptation boundary |
|---|---|---|
| Manager cohort | docs/ops/MANAGER-TOURNAMENT.schema.json defines strict manager.tournament.v1 with cohort, policy, task contract, environment, managers, evaluation contract and provenance | Keep this as canonical cohort envelope |
| Tournament protocol | docs/research/MANAGER-TOURNAMENT-CONTRACT.md requires same cohort/tool inventory/environment/budget/acceptance and deterministic verification before LLM judges | Preserve this protocol |
| DoE helpers | deepcli/deepcli/observatory/doe.py implements full factorial, Taguchi L9 and seeded random assignment | Reuse; test balance, design assumptions and factor limits |
| Trial orchestration | deepcli/deepcli/observatory/trial.py runs producer, critic, verifier and synthesis roles | Treat as an existing experiment path; test independent judge and source-grounded evaluation |
| Tournament campaign | deepcli/deepcli/observatory/tournament.py records trial outcomes and selects winners/losers | Extend carefully; inspect ranking semantics before using as promotion utility |
| Leaderboard | deepcli/deepcli/observatory/leaderboard.py stores role/task/provider/model run aggregates | Preserve raw records and avoid treating its composite as universal utility |
| Evolutionary replay | docs/ops/EVOLUTIONARY-REPLAY.md describes deterministic history replay and incumbent-preserving policy screening | Prefer offline replay before expensive live exploration |

Code inspection observations requiring targeted tests:

- Full factorial has exponential combination growth.
- Taguchi L9 is bounded to at most four factors with exactly three levels each.
- mvt_shuffle samples with replacement; balanced assignment requires an explicit balancing method.
- The current campaign/leaderboard path uses defaults for absent score, cost, latency and success fields. New adapters should preserve unknown values as null and validate evidence rather than silently treating absence as a successful zero-cost run.
- Existing leaderboard aggregation is a baseline ranking mechanism; complete multi-objective Pareto and uncertainty-aware decision logic belongs in a separate layer.

These are source inspections. Repository test execution is tracked by PR CI.

## Claims requiring validation before adoption

| Claim or capability | Validation experiment |
|---|---|
| Parallel swarm speedup | Matched sequential vs parallel task cohort |
| Compute worker speedup | Same job, resource accounting and repeated runs |
| Lower cost | Total inference + compute + orchestration + human cost |
| Better research quality | Blind rubric + factual/source verification |
| Reproducibility | Re-run pinned manifest in clean environment |
| Artifact provenance | Verify input, code, environment and output hashes |
| MCP interoperability | Authenticated tool discovery and bounded read-only call |
| A2A interoperability | Agent-card identity and task lifecycle conformance |
| Isolation | Cross-workspace negative tests in an authorized lab |
| Failure recovery | Worker kill, timeout, retry and partial-result tests |

## Decision

**Adopt as architecture inspiration; defer vendor dependency.**

Antinuous is relevant as a reference for integrated research, orchestration, compute and artifacts. The monorepo already has a manager tournament schema, DoE helpers, trial/tournament orchestration and evolutionary replay. The adaptation should compose these existing systems and add only missing versioned design, treatment, allocation and evidence-linkage contracts.

The useful product idea is adapted into an original architecture whose canonical contracts remain repository-owned.


## Additional references — classifier routing and bounded improvement

### Loop Library / Loopy

The user-supplied Loopy skill export describes discover, find, audit, adapt, craft, run, debrief, save/reuse and publish workflows. Its core loop is observe → choose → act → verify → record → repeat or stop, with explicit terminal states and run receipts. The current public Forward Future repository describes the library and skill as separate surfaces: the catalog publishes reusable loops, while the optional skill guides discovery, execution and debrief.

**Adaptation:** SIE adopts bounded passes, evidence receipts, named terminal states, explicit approval boundaries and post-run debrief. SIE keeps repository-owned experiment identity, evaluators and promotion authority.

Sources:
- https://github.com/Forward-Future/loopy
- https://signals.forwardfuture.com/loop-library/
- https://github.com/Forward-Future/loopy/tree/main/skills/loopy

### Jules lifecycle correction

The user-supplied Jules workflow material is valuable for agent-team design, attribution, asynchronous task delegation, PR integration and run observation. The official Jules changelog states that Jules winds down on 2026-12-31 and became read-only after 2026-11-11. For this 2026-11-22 snapshot, treat Jules as a historical/limited read-only collaborator for session export, provenance reconstruction and workflow analysis. Record live write-execution eligibility from an observed adapter, not from the historic roster.

**Adaptation:** make every agent's availability and permissions time-bounded registry fields. Historical agent contributions remain measurable; live execution eligibility requires an observed, time-bounded adapter.

Source: https://jules.google/docs/changelog/

### Classifier and router research

- RouteLLM provides multiple router strategies and an evaluation harness across benchmarks. https://github.com/lm-sys/RouteLLM
- RouterBench studies multi-model routing with a large inference-outcome dataset. https://arxiv.org/abs/2403.12031
- LLMRouterBench emphasizes unified comparison, model complementarity, model-pool composition and limitations of simplistic router baselines. https://arxiv.org/abs/2601.07206
- TwinRouterBench evaluates step-level routing in long-horizon agent trajectories, including static router iteration and end-to-end live execution. https://arxiv.org/abs/2605.18859
- Who Routes the Router highlights task diversity, model-pool balance and evaluation methodology as sources of routing-evaluation bias. https://openreview.net/pdf?id=EEPostHMtF

**Adaptation:** compare individual classifier capability, routing policy, graph composition and full tournament implementation as separate units. Test complementarity and conditional error overlap; preserve matched cohorts, held-out evaluation, stable candidate identity and actual end-to-end task outcome.

These references inform architecture and experiment design. Their benchmark results provide comparative context; the repository's 70+ classifier pool requires its own matched trials.


## Classifier inventory authority

The existing `docs/ops/SYSTEM-ONE-CATALOG.md` describes `config/system_one_catalog.json` (schema `system-one-catalog/1`) as the machine-readable catalog and reports 88 entries: 61 models, 16 adapters, 7 runtimes and 4 directories. The documented lifecycle is referenced → catalogued → trial_candidate → evaluated, with firsthand evidence required at each transition. The local Mev/Jev/Kev/Laya classes implement trial roles; same-named external projects are distinct catalog entities. This distinction is carried into the classifier graph contract.

The existing `docs/ops/CLASSIFIER-TRIAL-DISPATCH.md` already records the positional-zip alignment issue in trial.py as a steward backlog item. The proposed graph work elevates stable candidate-ID joins and regression coverage to a prerequisite.
