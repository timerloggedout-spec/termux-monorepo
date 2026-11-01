# ITEMS — orbital-syntax-topology-lab

## ORB-001 — Independent orbital syntax layout contract

Specify a reusable radial information architecture for hierarchical, multi-level data. Keep this parallel to SHE's existing grid/list/graph surfaces; do not replace the evidence model, graph query contract, or canonical navigation.

Acceptance:
- Define ring/depth semantics, angular ordering, focal-anchor rules, label placement, and overflow behavior.
- Separate semantic hierarchy from geometric layout.
- Preserve stable node IDs and source provenance.
- Mark the visual encoding as an exploratory presentation, not a validated claim of faster reading.

## ORB-002 — Accessible SVG proof of concept

Build a dependency-free, read-only SVG prototype with:
- concentric depth bands and a central focal anchor;
- selectable nodes and a persistent detail panel;
- keyboard-operable node selection;
- visible focus and reduced-motion support;
- a synchronized semantic list for screen readers and non-SVG fallback;
- responsive behavior and no external runtime/network dependency.

Acceptance:
- No source data is invented as live telemetry; all demo content is explicitly illustrative.
- Every node has a stable ID, label, depth, and description.
- No text is clipped by tight arcs; labels use radial bands or external callouts when space is insufficient.

## ORB-003 — D3/SVG interoperability evaluation

Evaluate D3 hierarchy/radial-tree primitives against a small custom polar-layout adapter. Use D3 for hierarchy/layout only if it adds measurable value; do not make a CDN or network fetch a runtime dependency.

Acceptance:
- Document coordinate convention, angular separation, depth-to-radius mapping, deterministic ordering, and layout complexity.
- Compare output against SVG 2 path/textPath behavior and browser accessibility constraints.
- Preserve an implementation path that can consume the existing context-relationship graph's verified/candidate edge classes without conflating them.

## ORB-004 — Human-factors evaluation plan

Define a falsifiable comparison against conventional list/grid and node-link views.

Acceptance:
- Measure task completion time, error rate, recall/accuracy, eye-movement proxy only where valid, viewport size, device class, and participant familiarity.
- Include dense technical labels, long identifiers, nested hierarchies, partial data, and low-vision/keyboard/screen-reader tasks.
- Do not claim "without moving your eyes" or faster reading without controlled evidence.
- Treat radial layout as an optional view and preserve a conventional alternative.

## ORB-005 — SHE integration decision gate

Recommend integration only after ORB-002/003 and a human-factors pilot.

Acceptance:
- Keep this prototype isolated until reviewed.
- Any future SHE adapter is read-only and consumes existing snapshot/graph contracts.
- Verified, candidate, inferred, unknown, and unavailable states remain distinct.
- No dashboard writes, collection changes, or schema migrations are included in this proposal.
