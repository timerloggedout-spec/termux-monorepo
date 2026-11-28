# Neuro-Inspired Engineering Research Lane

This document separates biological inspiration from repository fact. These are hypotheses for software architecture, not statements that an artificial system has biological structures or mental states.

## Established functional analogies in the SYNAPSE registry

- **Executive control:** prefrontal/frontoparietal systems inspire explicit goal, constraint, and resource management.
- **Attention:** salience and dorsal/ventral attention networks inspire prioritization and interrupt handling.
- **Memory:** hippocampal and temporal systems inspire episodic relationship storage and semantic registries.
- **Action selection:** thalamic/basal-ganglia loops inspire typed routing, eligibility, and suppression of unsafe or redundant actions.
- **Feedback:** cerebellar learning inspires comparison of intended and observed effects.
- **Homeostasis:** interoceptive and brainstem functions inspire health, liveness, and resource envelopes.
- **Reward learning:** reinforcement circuitry inspires outcome-based policy evaluation, constrained by correctness and safety.

## Expansion hypotheses

### 1. Corpus callosum → inter-agent integration fabric

A multi-agent system needs a dependable bridge between specialized workers. The engineering interpretation is not “agents think like hemispheres”; it is a shared, typed protocol for task claims, handoffs, acknowledgements, artifacts, and disagreement.

Test:
- schema compatibility;
- handoff completion rate;
- duplicate work;
- lost context;
- conflict resolution latency.

### 2. Sleep and glymphatic clearance → context consolidation

A mature system should periodically reconcile duplicate observations, create source-linked summaries, mark stale facts, and reduce retrieval noise. The analogy is consolidation and clearance, not literal sleep.

Safety:
- never delete canonical evidence;
- preserve source references and hashes;
- make summaries reversible;
- expire only under explicit retention policy.

### 3. Social cognition / mirror-system analogy → collaborator modeling

The ADE contains managers, agents, providers, tools, and human operators with different capabilities and authority. Model each role's actual capabilities and uncertainty. Do not infer an agent's identity from GitHub actor identity or treat a provider credential as an agent.

Test:
- role attribution accuracy;
- capability-route correctness;
- handoff quality;
- disagreement diversity without redundant review.

### 4. Novelty detection → weak-signal research

An anomaly/novelty lane could detect unusual co-occurrences across failures, provider changes, dependency shifts, and code paths. It should emit ranked hypotheses for review, not automatically interrupt or mutate production.

Test:
- precision/recall on historical incidents;
- false-positive burden;
- lead time;
- reproducibility of candidate evidence.

### 5. Metaplasticity → controlled learning-rate governance

The system needs a way to decide not only which policy performs best, but how much evidence is sufficient to change a policy. Small samples should not cause large routing changes. Drift, confidence intervals, cohort comparability, and rollback should govern adaptation.

Test:
- policy stability;
- time to detect genuine improvement;
- regression rate;
- rollback success;
- resistance to metric gaming.

### 6. Visual and language perception → structured input/output normalization

Dashboards, Mermaid diagrams, issue text, review comments, and tool responses are different observation surfaces. Normalize their provenance and uncertainty before allowing them into planning.

Test:
- source attribution;
- stale-data detection;
- partial-coverage visibility;
- instruction/data separation for untrusted input.

## New candidate names

| Candidate | Proposed role | Status |
|---|---|---|
| **Synaptic Bus** | Typed event and handoff fabric across subsystems | Proposed |
| **Dreamforge** | Offline research, scenario simulation, and hypothesis generation | Proposed |
| **Glymphatic Sweep** | Reversible context deduplication and stale-memory marking | Research |
| **Salience Gate** | Prioritized interruption and attention-budget controller | Proposed |
| **Plasticity Governor** | Evidence threshold and adaptation-rate controller | Proposed |
| **Noetic Cartographer** | Cross-domain concept and dependency mapping | Research |
| **Homeostat** | Unified runtime/resource health vector | Proposed |

These names are optional labels, not established repository components.

## Research guardrails

1. Prefer falsifiable engineering hypotheses over metaphor expansion for its own sake.
2. Run against historical or synthetic fixtures before live routing.
3. Compare against the simplest existing baseline.
4. Report confidence, sample size, and false-positive cost.
5. Keep candidate links and hypotheses separate from verified facts.
6. Do not use biological terminology to imply sentience or authority.
