# Research Astute — Shared Research Platform

**Status:** PRELIMINARY · platform architecture seed  
**Repository role:** host a growing collection of independent, continuously evolving thought experiments  
**Current exemplar:** [Computational limits](../astute-computational-limits/README.md)

## Purpose

Research Astute is a multi-experiment research environment. Each thought experiment owns its question, hypotheses, evidence, concepts, dependency structures, alternate paths, and evolving conclusions. Shared platform services provide common identifiers, typed relationship semantics, provenance, validation, reusable analysis adapters, and an interactive visualization surface.

The computational-limits experiment is one tenant of this platform. Its current DAG is an initial project seed, not the platform's canonical graph.

## Platform invariants

1. **Experiment isolation:** each experiment has an independent manifest, evidence set, graph set, lifecycle, and research history.
2. **Shared algebraic mappings:** common mathematical and conceptual entities receive stable identifiers and typed relations; project-specific meanings remain scoped.
3. **Typed graph semantics:** prerequisite DAGs, Markov transition systems, Bayesian evidence models, and historical lineage remain separate models.
4. **Alternate-path first:** an experiment can maintain competing routes and hypotheses simultaneously; the viewer can select and compare them.
5. **Evidence traceability:** every material claim and consequential edge carries source, date, assumptions, evidence class, and confidence or an explicit unknown state.
6. **Continuous evolution:** append and version concepts, edges, paths, sources, and experiment snapshots; preserve historical states.
7. **Reusable execution:** deterministic validation and bounded research loops operate across experiments through adapters.

## Platform layout

- `registry/experiments.json` — machine-readable experiment catalogue used by validation and the viewer.
- `registry/relation-types.json` — central typed relation vocabulary and algebraic mapping semantics.
- `schemas/` — experiment, graph, path-set, and source-registry contracts.
- `viewer/` — shared interactive graph viewer with alternate-path overlay and comparison.

```text
research/
├── astute-platform/
│   ├── README.md
│   ├── ARCHITECTURE.md
│   ├── EXPERIMENT-LIFECYCLE.md
│   ├── schemas/
│   └── visualization/
└── astute-computational-limits/
    ├── README.md
    ├── RESEARCH-PLAN.md
    ├── DEPENDENCY-MAP.md
    ├── DEPENDENCY-GRAPH.mmd
    ├── dependency-graph.json
    └── SOURCES.md
```

New experiments receive their own directory and manifest. Shared platform definitions live outside experiment directories. `registry/experiments.yaml` is the human-readable catalogue; `registry/experiments.json` is the machine-readable registry of record.

## Current repository integration

- Research issue templates and `.github/workflows/research-intake.yml` provide the existing issue-driven intake pattern.
- `.github/workflows/research-registry.yml` validates the current research registry surface.
- `refTemplates/15_Research_Repo_Templates/` contains research-repository scaffolds; the Jogyo pattern is the primary research-lab exemplar.
- `docs/ops/RESEARCH-TRIGGERS.md` and `docs/ops/RESEARCH-INTEGRATION-LANE.md` describe the existing research intake family and template integration.
- The standard fleet repository-creation route is documented in the AppID Registrar evaluation as GitHub API `POST /user/repos` followed by a Contents-API seed. This platform branch records the architecture; repository provisioning remains a separate authenticated operation.

## Initial delivery sequence

1. Establish the shared experiment, graph, path, evidence, and provenance contracts.
2. Register the computational-limits work as the first experiment package.
3. Adapt the existing DAG, dependency-phase, Bayesian, and Markov modules through typed interfaces.
4. Define and implement the shared interactive visualization surface.
5. Add experiment intake and validation to the existing research workflow family.
6. Provision the standalone `timerloggedout-spec/research-astute` repository through the authenticated bootstrap workflow.
7. Add bounded continuous research loops with explicit terminal states and receipts.
