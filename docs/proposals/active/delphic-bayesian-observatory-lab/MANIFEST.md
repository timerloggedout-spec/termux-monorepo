---
id: delphic-bayesian-observatory-lab
title: "Delphic Bayesian Oracle × Observatory control-plane design/evaluation"
author: ChatGPT
posted_at: 2026-10-01
status: executing
priority: P1
related_issues: [968]
related_prs: [5216]
related_branches:
  - experiment/delphic-observatory-scoped-merge
gates_required: [repo-gate, hosted-delphic-ci]
---

# MANIFEST

## Mathematical substrate
- `docs/schemas/delphic-math-contract.yaml` — exact Bayesian, information-value, Markov, DAG, reconciliation, provenance, and numerical invariants.
- Wolfram-verified BetaDistribution[2,2] regression fixture; Wolfram is not a CI runtime dependency.

## Intent

Create a separate design/evaluation proposal that ingests existing control-plane evidence and renders three complementary analytical planes:

- **LEFT / NOW:** tensor, graph, matrix, constellation layers.
- **CENTER / windows:** cadence, Agile, Gantt/dependencies, integration, complexity, compute, quality, uncertainty, provenance.
- **RIGHT / interthreading:** DAG, trellis, Markov state transitions, dependency paths.

The Bayesian/Delphic layer sits between evidence and decision explanation. It does not replace the evidence ledger.

## Computational substrate

- `docs/schemas/graph-algorithm-registry.yaml` — registered algorithm semantics and complexity.
- `scripts/delphic_graph_lab.py` — deterministic reference implementations.
- `scripts/delphic_math.py` — local stable formulas for prediction, entropy, KL, information gain, EVSI, and expected path cost.
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
- [x] Mathematical substrate expanded
- [x] Predictive / information / EVSI / expected-cost fixtures added
- [x] Graph algorithm registry added
- [x] Graph Lab reference engine added
- [x] Graph Lab visual sandbox added
- [x] Legacy Gemini review request archived as historical context
- [x] Gemini Dispatch retired; no longer a review dependency
- [ ] repo-gate + hosted-delphic-ci (Termux Origin offline; device smoke deferred)
- [ ] QUE/autonomous adapter contract and integration tests
- [ ] graduation evaluation


## Public showcase and integration

- `site/delphic-observatory/index.html` — versioned, dependency-free research showcase.
- `site/delphic-observatory/VERSION.json` — machine-readable artifact/version contract.
- `site/delphic-observatory/CHANGELOG.md` — release history.
- `site/delphic-observatory/README.md` — hosting and versioning policy.
- `.github/workflows/delphic-observatory-pages.yml` — validates version metadata and publishes to GitHub Pages on master updates (Pages must be enabled for the repository).
- `docs/ops/DELPHIC-QUE-INTEGRATION.md` — staged QUE/AutonomousOpsStuff integration and cross-context authority contract.

Version: 0.1.0. Public site is a research projection, not a live operations dashboard. Termux Origin is offline as of operator report 2026-11-12; native Termux validation remains pending.
