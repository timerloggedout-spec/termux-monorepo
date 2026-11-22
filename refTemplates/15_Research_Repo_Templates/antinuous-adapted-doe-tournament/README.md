# antinuous-adapted-doe-tournament

**Class:** Research orchestration + reproducible experimentation + manager tournament  
**Disposition:** Metadata-first reference and original adaptation specification  
**Tier:** B — research candidate pending implementation evidence  
**Version:** 0.2.0 · 2026-11-22

## Purpose

Capture publicly observable Antinuous product patterns and adapt useful ideas to the Termux MonoRepo's existing DoE, manager tournament, evolutionary replay, SHE, ATES/WTCV, Moneyball/3L0, Actions and evidence-led systems.

The target is an original **DoE Tournament Operating System** with a **Self-Improvement Engine (SIE)**. The primary competition is between versioned tournament implementations. The 70+ classifier population is a capability pool used to discover individual strengths, complementary combinations and effective routing graphs. SIE converts validated evidence into bounded challenger versions, matched experiments and gated promotion.

This is an architectural reference. It is not an implementation claim, an Antinuous SDK, a vendor integration, or a reproduction of proprietary source code.

## Source material

- SOURCE.txt — primary and comparative sources.
- RESEARCH-RECON.md — claim/evidence ledger and confidence.
- ARCHITECTURE.md — adapted system architecture and dynamic-utility patterns.
- DOE-TOURNAMENT-CONTRACT.md — versioned experiment and tournament contract.
- SCHEMAS.md — canonical data model and runtime registry contracts.
- OPERATING-SYSTEM.md — planes, competition units, lifecycle and promotion.
- SELF-IMPROVEMENT-ENGINE.md — SIE subsystems and bounded improvement loop.
- CLASSIFIER-GRAPH-TOURNAMENT.md — lateral classifier comparison, complementarity and graph composition.

## Existing implementation surfaces discovered

The monorepo already contains meaningful DoE/tournament primitives. This reference extends and connects them rather than creating a parallel tournament system.

| Existing surface | Observed responsibility |
|---|---|
| docs/ops/MANAGER-TOURNAMENT.schema.json | canonical manager.tournament.v1 cohort schema |
| docs/research/MANAGER-TOURNAMENT-CONTRACT.md | same-cohort manager comparison protocol |
| deepcli/deepcli/observatory/doe.py | full factorial, Taguchi L9 and seeded randomized assignment |
| deepcli/deepcli/observatory/trial.py | current local Mev producer, Jev critic, Kev verifier and Laya merger role baseline |
| deepcli/deepcli/observatory/tournament.py | campaign selection and leaderboard integration |
| deepcli/deepcli/observatory/leaderboard.py | persistent role/task/provider/model records |
| config/system_one_catalog.json | heterogeneous external model, adapter, runtime and directory inventory |
| config/classifier_graph_registry.json | versioned local/external candidate identities and graph arms |
| docs/ops/CLASSIFIER-GRAPH-REGISTRY.schema.json | runtime registry schema |
| scripts/ci/classifier_graph_registry_validator.py | catalog, role, source-path and DAG validator |
| scripts/agent_evolution/replay_simulator.py | deterministic replay and incumbent-preserving policy evolution |
| docs/ops/EVOLUTIONARY-REPLAY.md | replay-to-online-validation contract |
| she/evaluation | tournament reducers and policy evaluation |
| she/metrics/agent_throughput.py | ATES/WTCV/TCV/TPV/RPI observations |

The canonical manager cohort schema remains authoritative. Proposed DoE design, classifier graph and SIE manifests are supplemental contracts; they map to manager.tournament.v1 and existing evidence schemas rather than replace them. Mev/Jev/Kev/Laya are functional roles in the current baseline implementation, while the broader classifier system is modeled as a capability graph with parallel fan-out/fan-in and identity-based evidence joins.

## Termux MonoRepo integration

| Existing surface | Integration role |
|---|---|
| refTemplates/00_Index | reference navigation and source map |
| refTemplates/08_Swarm_References | orchestration and swarm patterns |
| refTemplates/11_Evaluation_Quality | DoE, quality gates and evaluation methods |
| refTemplates/12_External_Agents | optional external execution adapters |
| refTemplates/15_Research_Repo_Templates | this research template |
| canonical manager.tournament.v1 | cohort identity and manager comparison |
| canonical JSONL + receipts | evidence authority |
| SHE / 3L0 / Moneyball | downstream reduction and decision support |

The monorepo remains authoritative for task identity, version lineage, evidence, acceptance and promotion. External research/compute systems remain optional adapters.

The initial classifier graph registry registers four local role implementations and five catalog-backed namesake candidates. It preserves the 88-entry System One inventory as heterogeneous catalog layers rather than treating every entry as an interchangeable classifier. The graph validator checks candidate-to-catalog references, role compatibility, local source paths, unique node identity and DAG acyclicity. The typed-decision candidate screen remains design-only pending candidate-specific adapters and matched trials.

## Added operating-system references\n\n- OPERATING-SYSTEM.md — planes, competition units, lifecycle and promotion.\n- SELF-IMPROVEMENT-ENGINE.md — SIE subsystems and bounded improvement loop.\n- CLASSIFIER-GRAPH-TOURNAMENT.md — lateral classifier comparison, complementarity and graph composition.\n\nThe earlier trial implementation had a source-inspection risk: independently filtered artifact/Jev/Kev arrays could misalign after partial failures. The current branch adds stable candidate IDs, preserves per-candidate stage slots, checks identity at reduction, and excludes incomplete evidence triples. Regression tests have been added; CI execution remains pending.\n\n## Architectural decision

Use a **hybrid control plane**:

1. Event-sourced experiment ledger for durable state and replay.
2. Versioned DAG for task dependencies and execution planning.
3. Hierarchical manager/worker roles for bounded delegation.
4. Blackboard/evidence index for shared findings and artifact references.
5. Actor/lease ownership for isolated writers and work claims.
6. Factorial and sequential DoE designs for controlled comparison.
7. Pareto-frontier and constrained utility selection for multi-objective promotion.
8. Adapter ports for Termux, GitHub Actions, containers, MCP/A2A peers and optional cloud compute.

No external product owns canonical state. No single scalar score overrides correctness, security, reproducibility or explicit acceptance.

## Operating principles

- Version task, cohort, manager policy, prompt/template, evaluator, environment and experiment design independently.
- Preserve immutable run manifests and append-only observations.
- Use matched cohorts and randomized assignment where feasible.
- Keep failed, cancelled, timed-out and incomplete runs distinct.
- Treat missing measurements as unknown/null, never synthetic zero.
- Attribute provider, model, agent, manager, adapter and GitHub actor separately.
- Use ATES/WTCV as throughput observations, never standalone quality or merge gates.
- Promote only from reproducible evidence and explicit dual-gate/task-outcome policy.
- Keep secrets out of source, prompts, traces, receipts and artifacts.
- Support offline-first operation and bounded compute on Android/Termux.

## Status and next evidence

Reference research, operating-system contracts and the first versioned classifier registry are captured. The candidate-alignment repair and registry validator have regression tests committed; execution remains pending CI. Jules lifecycle is time-sensitive: official documentation says Jules became read-only after 2026-11-11 and is scheduled to wind down on 2026-12-31, so the operating system treats it as a historical/limited read-only collaborator for this snapshot rather than an assumed active write executor. Next steps: extend the registry across the complete classifier capability pool, implement candidate-specific typed-decision adapters, then run a small matched-cohort screen and graph-composition experiment.

## Provenance

Upstream product: https://antinuous.com/  
Upstream public GitHub organization: https://github.com/antinuous  
Repository owner: timerloggedout-spec/termux-monorepo  
Research snapshot: 2026-11-22


The canonical classifier inventory is `config/system_one_catalog.json`, documented in `docs/ops/SYSTEM-ONE-CATALOG.md`. Keep role contract, local implementation, external candidate and protocol adapter as distinct identities. The System One adapter supports typed decisions; it is not a generic text-generation adapter.
