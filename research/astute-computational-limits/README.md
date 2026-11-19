# Research Astute — Computational Limits

**Lane ID:** `ultimate-computation-limits`  
**Status:** PRELIMINARY · research-active · phase-gated  
**Hub:** `timerloggedout-spec/termux-monorepo`  
**Research workspace:** `research/astute-computational-limits/`  
**Intended stewardship:** Research Astute / Termux MonoRepo  
**Source seed:** [Black Hole Computers — Dr. Blitz (14 May 2025)](https://www.youtube.com/watch?v=v-2GGpARN0E)

## Mission

Map the mathematical, scientific, informational, physical and engineering dependencies that define increasingly powerful computation, up to the theoretical limits discussed in Seth Lloyd's *Ultimate physical limits to computation* (Nature, 2000).

The lane is a thought experiment and research practice. It maps established discoveries, known technologies, open theoretical questions and speculative bridges as separate evidence classes.

## Research question

**⌖ What prerequisite discoveries, models, materials, control systems and technologies would be required to approach each successive level of computational capability, and where do known physical limits or unresolved theories constrain the path?**

## Initial source interpretation

The linked video introduces a black-hole-computer thought experiment through:

- the Margolus–Levitin quantum speed limit;
- energy as a constraint on state-transition rate;
- mass-energy equivalence;
- information capacity and black-hole entropy;
- communication distance and signal-propagation time;
- Hawking radiation as a proposed output channel;
- the unresolved engineering of black-hole formation and precise quantum-state preparation.

The video is an explanatory entry point. Primary papers and current reviews govern scientific claims. Numerical claims in the video remain candidates for independent derivation and unit checking.

## Platform registration

This thought experiment is the first registered project in the shared [Research Astute platform](../astute-platform/README.md). Its manifest, normalized typed graph, source registry, and alternate path set provide the initial platform integration:

- [Experiment manifest](experiment.json)
- [Normalized prerequisite graph](graphs/ucl-prerequisite-v1.json)
- [Source registry](sources.json)
- [Alternate path hypotheses](paths/ucl-alternate-paths-v1.json)
- [Shared graph and path interaction contract](../astute-platform/visualization/INTERACTION-CONTRACT.md)

## Research files

| File | Purpose |
|---|---|
| [RESEARCH-PLAN.md](RESEARCH-PLAN.md) | Phased work and evidence gates |
| [DEPENDENCY-MAP.md](DEPENDENCY-MAP.md) | Cross-domain prerequisites, technology paths and algebra example |
| [DEPENDENCY-GRAPH.mmd](DEPENDENCY-GRAPH.mmd) | Visual prerequisite DAG |
| [dependency-graph.json](dependency-graph.json) | Machine-readable concept and dependency seed |
| [SOURCES.md](SOURCES.md) | Primary papers and current review anchors |

## Existing monorepo components to reuse

The lane reuses existing planning and uncertainty components by adapter:

- `she/orchestration/dag.py` — deterministic prerequisite DAG; edge direction is prerequisite → dependent.
- `scripts/agentic/dependency_phase_engine.py` — phase validation, topological ordering, dependency waves and evidence-aware lifecycle evaluation.
- `scripts/bayesian_routing.py` — Beta-Bernoulli posterior and uncertainty-aware decision primitives; use as a pattern for research confidence updates, with a domain-specific evidence model.
- `docs/ops/BAYESIAN-ROUTING.md` and `docs/schemas/bayesian-routing.yaml` — priors, likelihoods, partial pooling, evidence identity and decision separation.
- `experiments/archwiz-markov-lane/src/markov-engine.mjs` — Markov chain, strict-tree and recombining-trellis reference implementation.

The Markov transition model, Bayesian posterior model and prerequisite DAG have distinct semantics. Their data can be linked through stable concept/evidence identifiers; their mathematics and state transitions remain separately typed.

## Evidence labels

- `ESTABLISHED` — supported by accepted theory or repeatable observation within its stated assumptions.
- `SUPPORTED_MODEL` — supported theoretical framework with active research questions.
- `ACTIVE_RESEARCH` — current research with competing interpretations or incomplete resolution.
- `SPECULATIVE` — proposed conceptual path without a demonstrated implementation.
- `ENGINEERING_GAP` — required capability lacks a known engineering route at the proposed scale.
- `UNASSESSED` — source collection or analysis remains pending.

## Scope boundaries

- Map dependencies and evidence; do not present the map as a build plan for a black hole.
- Keep physical possibility, mathematical consistency, engineering feasibility and practical utility as separate assessments.
- Preserve source date, version, assumptions, evidence class and confidence for every consequential claim.
- Treat probabilities as evidence-conditioned estimates; keep qualitative unknowns qualitative.
- Keep the initial lane lightweight, reproducible and Termux-portable.

## First checkpoint

Establish the concept vocabulary, validate the prerequisite direction, reconcile the video against Lloyd's paper, and register the first cross-domain dependency paths. Subsequent concepts enter as new nodes and source-backed edges.
