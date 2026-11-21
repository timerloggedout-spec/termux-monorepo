# Research Astute — Platform Architecture

## 1. System boundary

The platform hosts many thought experiments under one research operating model. It shares identifiers, schemas, evidence conventions, validation, and visualization. It preserves independent project state and attribution.

A thought experiment is a research object, not an implementation commitment. A dependency map describes a proposed logical route; it does not establish physical feasibility, engineering readiness, or practical utility.

## 2. Canonical objects

| Object | Responsibility | Identity |
|---|---|---|
| Experiment | Question, scope, owners, lifecycle, and project-specific policy | `experiment_id` |
| Concept | Mathematical, scientific, technical, or domain entity | `concept_id` |
| Claim | Testable proposition with assumptions and evidence | `claim_id` |
| Source | Paper, dataset, video, repository, observation, or other reference | `source_id` |
| Evidence record | Source passage/result, interpretation, date, and quality | `evidence_id` |
| Graph | Typed graph instance and graph semantics | `graph_id` |
| Node | A concept, claim, artifact, capability, or milestone in a graph | `node_id` |
| Edge | A typed, directed relation with provenance | `edge_id` |
| Path set | One or more alternate routes through a graph | `path_set_id` |
| Path | Ordered nodes/edges plus assumptions and status | `path_id` |
| Snapshot | Immutable, reproducible version of experiment state | `snapshot_id` |
| Research run | Bounded observe/choose/act/verify/record cycle | `run_id` |

IDs are globally unique or namespace-qualified by experiment. Display names remain editable and localized.

## 3. Graph semantics

The platform uses a graph envelope with a required `graph_type`. Each graph type has its own validation and mathematical rules.

| Graph type | Edge meaning | Allowed structure | Reused implementation |
|---|---|---|---|
| `prerequisite_dag` | prerequisite → dependent | directed acyclic graph | `she/orchestration/dag.py`; `scripts/agentic/dependency_phase_engine.py` |
| `markov_transition` | state → possible next state with transition probability | directed weighted state graph; cycles allowed | `experiments/archwiz-markov-lane/src/markov-engine.mjs` |
| `bayesian_evidence` | evidence/model/claim dependency or inference relation | probabilistic model with explicit priors and likelihoods | `scripts/bayesian_routing.py` as an adapter pattern |
| `lineage` | derived-from, supersedes, or records | versioned provenance graph | platform provenance layer |
| `concept_map` | typed conceptual relation | cycles allowed where relation semantics permit | shared graph core |

**Semantic firewall:** graph instances retain their type. A prerequisite edge is not a transition probability; a Bayesian dependency is not a prerequisite; a historical lineage relation does not imply causation. Shared node IDs and provenance references connect these models without conflating them.

## 4. Alternate paths

Each experiment may register multiple named path hypotheses against one or more graphs. Paths can branch, merge, overlap, compete, or remain unresolved.

A path record carries:
- ordered node and edge references;
- hypothesis and rationale;
- prerequisite assumptions;
- supporting and contradicting evidence references;
- evidence class and confidence representation;
- status: `candidate`, `active`, `supported`, `challenged`, `blocked`, `superseded`, or `retired`;
- snapshot and revision provenance.

Path ranking remains an explicit, configurable projection. The platform does not collapse uncertainty into a single default winner.

## 5. Shared algebraic mapping layer

The mapping layer provides reusable relation vocabularies and typed transforms, rather than forcing every domain into one universal algebra.

Initial relation families:
- identity and equivalence;
- prerequisite and derivation;
- composition and decomposition;
- containment and membership;
- transformation and representation;
- state transition;
- evidence support, contradiction, and qualification;
- version lineage and supersession.

Each mapping declares domain, codomain, relation type, assumptions, validity interval, source, and transform version. Mathematical structures such as groups, rings, fields, vector spaces, Hilbert spaces, manifolds, and probability spaces are represented as typed concepts with source-backed relations. Domain adapters define their specialized operators.

## 6. Existing module adapters

### DAG and phase engine

Use the DAG module for prerequisite ordering and the phase engine for dependency waves and phase validation. Map platform IDs to adapter-local IDs, preserve edge direction, and return validation receipts with source graph and snapshot IDs.

### Markov engine

Use the Markov lane for state-transition models, including strict trees and recombining trellises. Preserve transition weights, normalization rules, absorbing states, and model assumptions. Do not route a Markov graph through DAG cycle validation.

### Bayesian evidence

Use the Bayesian routing module as a structural reference for posterior/provenance updates. Define domain-specific priors, likelihoods, evidence dependence, and calibration before interpreting posterior values as research confidence. Keep model output distinct from observed evidence.

## 7. Interactive visualization surface

One shared viewer renders graph instances through type-specific adapters.

Primary interaction regions:
1. **Experiment navigator** — select experiment, version, and snapshot.
2. **Path navigator** — select, overlay, isolate, and compare alternate paths.
3. **Graph canvas** — pan, zoom, focus, expand, collapse, and follow relationships.
4. **Evidence inspector** — inspect claims, sources, assumptions, provenance, confidence, and unresolved questions.
5. **Phase rail** — view dependency waves, research phases, blocked prerequisites, and progress.
6. **Comparison view** — compare paths or snapshots by nodes, edges, evidence, assumptions, and state changes.

Interactions update a shareable view state. They do not mutate canonical research data. Edits create a proposed revision or issue/PR through the governed workflow.

## 8. Versioning and reproducibility

Every snapshot records schema version, experiment revision, graph revision, path-set revision, source manifest digest, adapter versions, and generation timestamp. Derived visual layouts may be regenerated; canonical graph and evidence records remain source-controlled.

## 9. Quality gates

- Schema validation and referential integrity.
- Unique IDs and valid graph-type semantics.
- DAG acyclicity only for `prerequisite_dag`.
- Markov transition normalization where the model requires it.
- Bayesian model declaration of priors, likelihoods, and dependence assumptions.
- Evidence references resolve to registered sources.
- Path references resolve to nodes and edges in the declared graph.
- Snapshot generation is deterministic for identical inputs and adapter versions.
- UI path selection and comparison preserve the underlying model semantics.
