# Research Astute — Shared Visualization Interaction Contract

## Goal

Provide one interactive surface for many independent thought experiments and their alternate path structures. The viewer is a projection of canonical, versioned research data.

## User flow

1. Select an experiment.
2. Select a snapshot or compare two snapshots.
3. Select a graph type and graph instance.
4. Select one or more path hypotheses.
5. Inspect the shared graph canvas and phase rail.
6. Select nodes or edges to inspect assumptions, evidence, source provenance, and open questions.
7. Compare alternate paths or revisions.
8. Export a stable deep link to the selected view state.

## Core controls

| Control | Behavior |
|---|---|
| Experiment selector | Switches experiment context and resets invalid graph/path selections |
| Snapshot selector | Loads a fixed, reproducible experiment snapshot |
| Graph-type filter | Selects prerequisite, transition, evidence, lineage, or concept views |
| Path selector | Isolates or overlays a chosen path |
| Path comparison | Highlights shared, divergent, added, removed, and unresolved segments |
| Phase rail | Shows dependency waves and phase status for prerequisite graphs |
| Node/edge inspector | Shows definitions, relation semantics, assumptions, evidence, and provenance |
| Evidence filter | Filters by evidence class, source, date, and confidence representation |
| Layout controls | Pan, zoom, fit, focus, expand, collapse, and reset |
| View permalink | Encodes experiment, snapshot, graph, paths, filters, and focus state |

## Graph-type renderers

- **Prerequisite DAG:** topological layers, dependency waves, blocked prerequisites, and alternate valid routes.
- **Markov transition graph:** states, weighted transitions, probability labels, reachable states, and selected trajectories.
- **Bayesian evidence graph:** claims, observations, priors, likelihood relationships, and posterior summaries with model assumptions visible.
- **Lineage graph:** versions, derivations, supersession, and source ancestry.
- **Concept map:** typed relations and domain groupings.

Each renderer declares its graph semantics and supported interactions. The viewer may share layout primitives while retaining type-specific legends, validation, and analytical controls.

## Comparison modes

- **Path vs path:** shared prefix, divergence points, unique nodes/edges, distinct assumptions, and evidence balance.
- **Snapshot vs snapshot:** added/removed/changed objects, source freshness, status transitions, and schema/adapter versions.
- **Experiment vs experiment:** compare shared concepts and relation mappings while preserving each experiment's local graph and evidence context.

## State and persistence

View state is non-canonical and shareable. Research edits create versioned data changes through the normal repository workflow. A browser selection, layout adjustment, or filter never changes a claim, edge, probability, or evidence record.

## Accessibility and portability

- Keyboard navigation for all graph actions.
- Text/table representation for every visual graph.
- Screen-reader labels for node and edge semantics.
- Color-independent status encoding.
- Mobile-friendly pan/zoom and compact inspector.
- Static SVG/PNG and Markdown/Mermaid fallbacks.
- Local-first data loading with no mandatory external runtime service.

## Acceptance tests

1. Switch between two experiment manifests without cross-contaminating graph state.
2. Toggle alternate paths and accurately highlight shared/divergent segments.
3. Render cycles in Markov graphs while DAG validation remains acyclic-only.
4. Inspect a node and resolve its source/evidence references.
5. Deep-link to a view and restore the same snapshot and selections.
6. Compare snapshots and show exact object-level changes.
7. Operate the complete flow by keyboard and through the text/table fallback.
