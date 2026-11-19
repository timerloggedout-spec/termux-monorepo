# Source — Research Astute Platform

## User direction

The platform hosts many thought experiments of the same kind. Each experiment owns its research question and evolving content. The platform shares algebraic mappings, graph/data contracts, and an interactive visualization UX that allows alternate path structures to be selected and compared.

## Repository evidence

- Existing research issue intake: `.github/workflows/research-intake.yml` and `scripts/research/research_intake.py`.
- Existing research registry validation: `.github/workflows/research-registry.yml`.
- Research-repository scaffolds: `refTemplates/15_Research_Repo_Templates/`, with the Jogyo research-lab pattern as the primary exemplar.
- Reusable graph/model modules: `she/orchestration/dag.py`, `scripts/agentic/dependency_phase_engine.py`, `scripts/bayesian_routing.py`, and `experiments/archwiz-markov-lane/`.
- Existing research integration contract: `docs/ops/RESEARCH-INTEGRATION-LANE.md` and `docs/ops/RESEARCH-TRIGGERS.md`.
- Standard fleet repository creation route: GitHub API `POST /user/repos` followed by Contents-API seeding, recorded in `docs/proposals/active/master-splinter/EVALUATION.md` and `ops/github-apps/PROCESS.json`.

## Design decision

Use a platform envelope with independent experiment manifests and versioned graph/path sets. Keep prerequisite DAG, Markov transition, Bayesian evidence, concept mapping, and lineage semantics distinct. Use adapter boundaries to reuse existing implementations. Treat the viewer as a read projection; canonical changes flow through versioned repository updates and review.
