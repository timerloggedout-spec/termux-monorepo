# antinuous-adapted-doe-tournament

**Class:** Research orchestration + reproducible experimentation + manager tournament  
**Disposition:** Metadata-first reference and original adaptation specification  
**Tier:** B — research candidate pending implementation evidence  
**Version:** 0.1.1 · 2026-11-22

## Purpose

Capture publicly observable Antinuous product patterns and adapt useful ideas to the Termux MonoRepo's existing DoE, manager tournament, evolutionary replay, SHE, ATES/WTCV, Moneyball/3L0, Actions and evidence-led systems.

The target is an original **Design-of-Experiments Tournament (DoE Tournament)** control plane. It versions experimental plans and manager policies, assigns comparable cohorts, executes isolated treatments, captures immutable evidence, evaluates quality and utility, and promotes validated variants through explicit gates.

This is an architectural reference. It is not an implementation claim, an Antinuous SDK, a vendor integration, or a reproduction of proprietary source code.

## Source material

- SOURCE.txt — primary and comparative sources.
- RESEARCH-RECON.md — claim/evidence ledger and confidence.
- ARCHITECTURE.md — adapted system architecture and dynamic-utility patterns.
- DOE-TOURNAMENT-CONTRACT.md — versioned experiment and tournament contract.
- SCHEMAS.md — canonical data model and illustrative YAML/JSON structures.

## Existing implementation surfaces discovered

The monorepo already contains meaningful DoE/tournament primitives. This reference extends and connects them rather than creating a parallel tournament system.

| Existing surface | Observed responsibility |
|---|---|
| docs/ops/MANAGER-TOURNAMENT.schema.json | canonical manager.tournament.v1 cohort schema |
| docs/research/MANAGER-TOURNAMENT-CONTRACT.md | same-cohort manager comparison protocol |
| deepcli/deepcli/observatory/doe.py | full factorial, Taguchi L9 and seeded randomized assignment |
| deepcli/deepcli/observatory/trial.py | Mev → Jev → Kev → Laya trial orchestration |
| deepcli/deepcli/observatory/tournament.py | campaign selection and leaderboard integration |
| deepcli/deepcli/observatory/leaderboard.py | persistent role/task/provider/model records |
| scripts/agent_evolution/replay_simulator.py | deterministic replay and incumbent-preserving policy evolution |
| docs/ops/EVOLUTIONARY-REPLAY.md | replay-to-online-validation contract |
| she/evaluation | tournament reducers and policy evaluation |
| she/metrics/agent_throughput.py | ATES/WTCV/TCV/TPV/RPI observations |

The canonical manager cohort schema remains authoritative. The proposed DoE design/treatment manifests in this slot are supplemental contracts; they must map to manager.tournament.v1 and existing evidence schemas rather than replace them.

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

## Architectural decision

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

Reference research is captured. Existing DoE and tournament code has been located by source inspection; this PR has not executed its test suite. Next steps: map the proposed design/treatment manifest to manager.tournament.v1, add validators only for genuine gaps, then run a small matched-cohort tournament before expanding adapters or UI.

## Provenance

Upstream product: https://antinuous.com/  
Upstream public GitHub organization: https://github.com/antinuous  
Repository owner: timerloggedout-spec/termux-monorepo  
Research snapshot: 2026-11-22
