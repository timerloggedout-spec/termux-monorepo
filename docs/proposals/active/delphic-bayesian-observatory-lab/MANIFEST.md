---
id: delphic-bayesian-observatory-lab
title: "Delphic Bayesian Oracle × Observatory control-plane design/evaluation"
author: ChatGPT
posted_at: 2026-10-01
status: executing
priority: P1
related_issues: [968]
related_prs: [969]
related_branches:
  - experiment/delphic-bayesian-observatory-lab
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST

## Mathematical substrate
- `docs/schemas/delphic-math-contract.yaml` — exact Bayesian, information-value, Markov, DAG, reconciliation, provenance, and numerical invariants.
- Wolfram-verified BetaDistribution[2,2] regression fixture; Wolfram is not a CI runtime dependency.

## Intent

Create a separate Gemini design/style proposal that ingests existing control-plane evidence and renders three complementary analytical planes:

- **LEFT / NOW:** tensor, graph, matrix, constellation layers.
- **CENTER / windows:** cadence, Agile, Gantt/dependencies, integration, complexity, compute, quality, uncertainty, provenance.
- **RIGHT / interthreading:** DAG, trellis, Markov state transitions, dependency paths.

The Bayesian/Delphic layer sits between evidence and decision explanation. It does not replace the evidence ledger.

## Computational substrate

- `docs/schemas/graph-algorithm-registry.yaml` — registered algorithm semantics and complexity.
- `scripts/delphic_graph_lab.py` — deterministic reference implementations.
- `experiments/delphic-observatory-lab/graph-lab.html` — executable visual explanation surface.

The Graph Lab deliberately distinguishes Git history, decision/evidence DAGs, dependency DAGs, state reconciliation, and Markov trellises.

## Existing architecture bindings

- Bayesian uncertainty: `docs/ops/BAYESIAN-ROUTING.md`
- Bayesian schema: `docs/schemas/bayesian-routing.yaml`
- Oracle evaluator: `scripts/ci/oracle_watch.sh`
- Evidence substrate: `docs/ops/AGENT-EVIDENCE-SUBSTRATE.md`
- SHE snapshot: `docs/ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md`
- Research-lane separation: `docs/research/LANE-ARCHITECTURE.md`

## Data rule

The Observatory projection consumes canonical evidence. It must not manufacture events, convert missingness to zero, or silently promote inferred relationships to verified facts.

## Adversarial review rule

Adversarial review admission is dynamic. Candidate admission signals are uncertainty width, benchmark regression, anomaly/retry density, provenance incompleteness, change-point evidence, and decision impact. These signals select *when to seek review*; they do not score a reviewer or declare a winner.

## Checklist

- [x] Issue registered
- [x] Isolated branch created
- [x] Control-plane schema added
- [x] Deterministic engine added
- [x] Observatory projection contract added
- [x] Design sandbox added
- [x] Focused tests added
- [x] Graph algorithm registry added
- [x] Graph Lab reference engine added
- [x] Graph Lab visual sandbox added
- [x] Gemini review request prepared
- [ ] Gemini findings received/dispositioned
- [ ] repo-gate + termux-smoke
- [ ] graduation evaluation
