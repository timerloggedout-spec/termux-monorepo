# Antinuous RECON — evidence ledger

**Snapshot:** 2026-11-22  
**Research target:** https://antinuous.com/  
**Disposition:** reference architecture candidate; no live account execution performed.

## Evidence classes

| Class | Meaning | Use |
|---|---|---|
| P — primary | Official website, legal terms, pricing, official repository | Establish what the source says |
| R — repository | Public GitHub repository, code or issue | Establish publicly visible code and project activity |
| I — independent | Independent reproduction, third-party evidence | Validate claims outside source owner |
| A — analysis | Architectural inference or proposed adaptation | Guide our design; never report as upstream fact |

## Product capability claims

The public Antinuous product describes an autonomous research and compute environment combining research planning and agent delegation; parallel agent swarms; isolated computers and compute workers; scientific/engineering simulation and data-source access; research artifacts and source-linked results; iterative candidate evaluation; external agent access through MCP and A2A; and optional GPU execution/external compute account integration.

**Evidence status:** P — company-published capability descriptions.  
**Independent status:** I — not established by this recon.  
**Adaptation:** build equivalent capability contracts as modular providers; do not assume vendor API compatibility.

## Commercial and performance claims

The website advertises a throughput/cost proposition and reports swarm/compute speedups and research completion statistics. Pricing is organized into subscription tiers with AI usage allowances and compute capabilities.

**Evidence status:** P — company-reported marketing and pricing.  
**Independent status:** I — no independent equal-budget, equal-quality reproduction established.  
**Tournament treatment:** retain claim text, capture date, workload definition, baseline, worker count, hardware, model, quality score, total cost and repetitions before comparison.

A speedup without equal-quality acceptance and full resource accounting is not a productivity result.

## Security and trust

Official privacy and terms materials describe collection and processing of account data, prompts, files, research records and connected-account context; third-party processors; user ownership/license provisions; generated-output limitations; retention and liability provisions.

The public material inspected did not establish independent audit evidence for SOC 2, penetration testing, tenant-isolation verification, encryption design, customer-managed keys or enterprise SLA.

**Evidence status:** P — published policy/terms statements.  
**Independent status:** I — technical controls remain unverified.  
**Adaptation:** require explicit data classification, adapter permission scopes, redaction, environment isolation, retention, secret boundaries and provenance receipts.

## Public GitHub recon

The user-provided GitHub repository search was reviewed. The public Antinuous organization includes Mojo-oriented repositories such as antinuous/mojo-flare, antinuous/mojo-json, antinuous/protomojo, antinuous/grpc-mojo, antinuous/mojo-http2, antinuous/mojo-net, antinuous/mojo-tls and antinuous/mojo-mozz.

These repositories demonstrate a public Mojo software footprint. Their existence does not prove that any repository implements the Antinuous hosted research platform.

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
- mvt_shuffle samples with replacement; it does not guarantee balanced assignments.
- The current campaign/leaderboard path uses defaults for absent score, cost, latency and success fields. New adapters should preserve unknown values as null and validate evidence rather than silently treating absence as a successful zero-cost run.
- Existing leaderboard aggregation is a baseline ranking mechanism, not a complete multi-objective Pareto or uncertainty-aware decision engine.

These are source inspections, not test execution results. The PR has not yet run the repository test suite.

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
