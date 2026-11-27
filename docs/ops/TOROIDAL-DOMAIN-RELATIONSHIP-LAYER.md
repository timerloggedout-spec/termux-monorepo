# Toroidal Domain Relationship Layer

**Status:** proposed optional SHE interaction layer  
**Authority:** GitHub artifacts, Historical Corpus, versioned SHE snapshots, and their evidence contracts remain authoritative.  
**Surface:** additive visualization and navigation projection; no new source-of-truth database.

## 1. Purpose

Add a toroidal topology as an optional way to explore cross-domain relationships. The topology is inspired by cyclic and mirrored structures: users can traverse forward and reverse relationships, inspect complementary perspectives, and follow evidence across domains.

The torus is a **visual and navigational projection**, not a claim that the repository's domains form a mathematically complete torus. Domain count, ordering, grouping, and placement remain data-driven. A twelve-position preset may be offered as a visual arrangement, but twelve is not a canonical domain count.

## 2. Architectural placement

```text
GitHub truth + Historical Corpus + Actions evidence
                         |
                         v
              deterministic SHE reducers
                         |
                         v
              versioned SHE snapshot
                         |
              relationship projection
                         |
            +------------+-------------+
            |                          |
     conventional graph         toroidal explorer
            |                          |
            +------------+-------------+
                         |
              evidence / provenance drawer
```

The explorer consumes the same versioned snapshot and relationship records as the conventional Relationships surface. It adds a projection and interaction mode; it does not fork ingestion, scoring, or persistence.

## 3. Relationship contract

Each node identifies a domain artifact or capability using a stable ID and a canonical source reference. Each edge identifies a typed relationship between two node IDs.

Required edge properties:

- stable `id`, `source`, and `target`;
- explicit `relation_type`;
- `status`: `verified`, `candidate`, `inferred`, or `unknown`;
- `directionality`: `directed`, `bidirectional`, or `symmetric`;
- evidence references, including source SHA or snapshot identity where available.

Confidence is optional and bounded to [0, 1]. Missing confidence remains missing; it is never synthesized. `mirror_of` is a typed relationship, not an assumption inferred from visual proximity. Mirror pairs carry an explicit `pair_id`.

The JSON Schema at `docs/ops/TOROIDAL-DOMAIN-RELATIONSHIP.schema.json` is the machine contract.

## 4. Projection semantics

The torus maps each node to a pair of angular coordinates:

- major angle: position around the primary domain cycle;
- minor angle: position around the tube/cross-section.

These coordinates control rendering only. They do not change node identity, edge semantics, source order, or evidence authority.

Projection modes:

1. **Domain cycle:** group domains around the major ring.
2. **Mirror view:** place explicitly paired nodes on opposing or reflected positions.
3. **Dependency flow:** emphasize directed producer/consumer paths.
4. **Temporal view:** animate or scrub only when the selected immutable snapshot supplies temporal evidence.

A twelve-slot layout is a preset. Unassigned and additional domains remain discoverable through search, filters, and an overflow group.

## 5. Interaction model

- Pan, zoom, rotate, and reset view.
- Search nodes by stable ID, name, domain, or artifact type.
- Filter by relationship type, evidence status, confidence availability/range, domain, and time window.
- Select a node to open its details and immediate neighborhood.
- Select an edge to inspect direction, relationship semantics, evidence, and provenance.
- Toggle forward/reverse traversal and mirror-pair highlighting.
- Expand/collapse neighborhoods without changing the underlying graph.
- Switch between conventional graph and toroidal projection while preserving the selected node and filters.
- Deep-link to a node/edge using stable IDs and snapshot identity.

Keyboard navigation and an equivalent accessible list/table view are mandatory. Status must be conveyed by text and accessible labels, not color alone. Reduced-motion preferences disable animated rotation and transitions.

## 6. Evidence and authority

Every visible relationship exposes its evidence state:

- **verified:** supported by the declared evidence contract;
- **candidate:** collected but awaiting verification;
- **inferred:** derived by a documented inference process;
- **unknown:** insufficient evidence.

The inspector exposes source snapshot, source SHA, evidence IDs, timestamps, and canonical GitHub links when present. Historical queries use immutable temporal/L2 snapshots; the current graph alone cannot stand in for past state.

The UI must distinguish observed, derived, inferred, and unavailable values. Partial corpus coverage remains visible. Missing evidence is not zero.

## 7. Security and operational boundaries

- Read-only projection by default.
- No credentials in snapshots, browser state, or graph payloads.
- UI commands that initiate mutations route through existing authorized workflows and display the resulting action/effect receipt.
- The explorer does not execute workflow definitions, agents, or arbitrary code.
- External analytics and visual-editor products remain optional adapters.
- Graph layout and rendering failures do not affect collection, reducers, or canonical evidence.

## 8. Implementation sequence

1. Validate the schema and fixture data.
2. Build a deterministic projection adapter from a versioned SHE snapshot.
3. Add a static toroidal diagram/source asset and conventional graph fallback.
4. Implement accessible node/edge selection and evidence inspection.
5. Add filters, mirror traversal, and temporal snapshot selection.
6. Integrate the explorer as an optional mode under SHE Relationships.
7. Add browser tests for partial data, missing confidence, keyboard access, reduced motion, and provenance links.

## 9. Acceptance gates

- [ ] Canonical node and edge IDs remain stable across projection modes.
- [ ] Projection preserves source snapshot ID and SHA.
- [ ] Twelve-position preset remains optional and configurable.
- [ ] Every edge exposes type, directionality, status, and evidence references.
- [ ] Mirror relationships require explicit `mirror_of` records and `pair_id`.
- [ ] Missing confidence and evidence remain unavailable.
- [ ] Partial coverage is visible in all views.
- [ ] Graph and toroidal views share filters and selection state.
- [ ] Keyboard-accessible list/table provides equivalent navigation.
- [ ] Reduced-motion mode removes animated transitions.
- [ ] Read-only operation requires no provider credentials.
- [ ] No new persistence authority or mandatory third-party dependency is introduced.
- [ ] Tests prove projection determinism and provenance preservation.

## 10. Relationship to existing SHE contracts

This document extends, rather than replaces:

- `SHE-DASHBOARD-PRD.md`
- `SHE-DASHBOARD-SNAPSHOT-CONTRACT.md`
- `SHE-DASHBOARD-UI-UX-CONTROL-PLANE.md`
- `SHE-DASHBOARD-ARCHITECTURE.mmd`

The conventional relationship graph remains available as the simpler baseline and fallback.
