# antinuous-adapted-doe-tournament

**Class:** Research orchestration + reproducible experimentation + manager tournament  
**Disposition:** Metadata-first reference and original adaptation specification  
**Tier:** B — research candidate pending implementation evidence  
**Version:** 0.1.0 · 2026-11-22

## Purpose

Capture publicly observable Antinuous product patterns and adapt useful ideas to the Termux MonoRepo's existing DoE, SHE, ATES/WTCV, Moneyball/3L0, Actions and evidence-led systems.

The target is an original **Design-of-Experiments Tournament (DoE Tournament)** control plane. It versions experimental plans and manager policies, assigns comparable cohorts, executes isolated treatments, captures immutable evidence, evaluates quality and utility, and promotes validated variants through explicit gates.

This is an architectural reference. It is not an implementation claim, an Antinuous SDK, a vendor integration, or a reproduction of proprietary source code.

## Source material

- SOURCE.txt — primary and comparative sources.
- RESEARCH-RECON.md — claim/evidence ledger and confidence.
- ARCHITECTURE.md — adapted system architecture and dynamic-utility patterns.
- DOE-TOURNAMENT-CONTRACT.md — versioned experiment and tournament contract.
- SCHEMAS.md — canonical data model and illustrative YAML/JSON structures.

## Termux MonoRepo integration

| Existing surface | Integration role |
|---|---|
| refTemplates/00_Index | reference navigation and source map |
| refTemplates/08_Swarm_References | orchestration and swarm patterns |
| refTemplates/11_Evaluation_Quality | DoE, quality gates and evaluation methods |
| refTemplates/12_External_Agents | optional external execution adapters |
| refTemplates/15_Research_Repo_Templates | this research template |
| she/evaluation | tournament reducers and policy evaluation |
| she/metrics/agent_throughput.py | ATES/WTCV/TCV/TPV/RPI observations |
| docs/ops/AGENT-EVALUATION-LANE-REGISTRY.md | evaluator and adapter admission |
| docs/ops/AGENT-TEAM-ORCHESTRATION.md | manager/worker responsibilities |
| canonical JSONL + receipts | evidence authority |

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

Reference research is captured. Implementation fitness remains untested. Next steps: map this contract against current DoE/tournament modules, add schema validators and deterministic fixtures, then run a small matched-cohort tournament before expanding adapters or UI.

## Provenance

Upstream product: https://antinuous.com/  
Upstream public GitHub organization: https://github.com/antinuous  
Repository owner: timerloggedout-spec/termux-monorepo  
Research snapshot: 2026-11-22
