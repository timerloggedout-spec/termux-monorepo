# Research Astute

A shared research environment for independent, continuously evolving thought experiments.

## Platform

- `research/astute-platform/ARCHITECTURE.md` — shared experiment, graph, path, evidence, and provenance model.
- `research/astute-platform/EXPERIMENT-LIFECYCLE.md` — lifecycle and bounded research loops.
- `research/astute-platform/visualization/INTERACTION-CONTRACT.md` — shared interactive graph and alternate-path UX.
- `research/astute-platform/schemas/` — experiment and typed graph contracts.
- `research/astute-platform/registry/experiments.yaml` — experiment catalogue.

## Experiments

Each experiment owns its question, hypotheses, sources, evidence, graphs, alternate path sets, and snapshots.

The first registered experiment is [Ultimate Computational Limits](research/astute-computational-limits/README.md). It begins with a 34-node / 46-edge prerequisite graph and two candidate research-path views.

## Graph semantics

Prerequisite DAGs, Markov transition systems, Bayesian evidence models, concept maps, and lineage graphs retain separate typed semantics. Shared IDs and provenance connect the models.

## Continuous work

Use the experiment lifecycle and research-run receipt contract to make bounded, reproducible updates. Validate with:

```bash
python3 scripts/research/validate_astute.py
```

Research maps describe candidate routes and evidence. They preserve assumptions and uncertainty as the project evolves.
