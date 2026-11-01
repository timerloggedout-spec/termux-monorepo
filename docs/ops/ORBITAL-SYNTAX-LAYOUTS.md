# Orbital Syntax Layouts — research and implementation contract

**Status:** exploratory proposal + isolated proof of concept  
**Authority:** proposal `orbital-syntax-topology-lab`  
**Runtime:** browser-native SVG/HTML; no external dependencies

## Purpose

Explore concentric-ring and polar-partition layouts as an optional view for hierarchical information. The layout is a projection of structured data, not a data store, graph authority, or evidence collector.

## Semantic model

Each node has:
- stable `id`;
- `label`;
- `description`;
- `depth` (root = 0);
- optional `parent_id`;
- optional source/evidence references;
- explicit state when used with repository data (verified, candidate, inferred, unknown, unavailable).

The hierarchy is canonical input. Geometry is derived and disposable.

## Geometry contract

- The root/focal anchor occupies the center.
- Depth maps monotonically to radius; depth 1 is the innermost ring.
- Sibling nodes receive deterministic angular intervals in stable input order; intervals are weighted by descendant leaf count so larger subtrees receive proportionally more angular space. Parent nodes sit at the center of their allocated interval.
- Angular span may be weighted by descendant count or explicit value only when that field is present and its semantics are documented.
- Labels are not forced onto arcs when the available arc length is insufficient. Use horizontal callouts or the synchronized semantic list.
- The initial prototype uses a fixed illustrative data set and a deterministic leaf-count-weighted polar layout: each sibling receives angular span proportional to the number of descendant leaves, and its center angle is derived from that interval. No live corpus values are represented.
- The 120 px inner-radius suggestion from the supplied screenshot is a tunable experiment parameter, not a hard-coded universal rule.

## Interaction contract

- Selecting a node updates the detail panel and selected-state affordance.
- The same node is reachable via the semantic list and keyboard.
- SVG marks are not the only way to access information.
- Focus indication, reduced motion, high contrast, and responsive reflow are required.
- No auto-rotation, flashing, forced animation, or destructive controls.
- No write-back to GitHub, SHE, or source systems.

## Evaluation

Compare radial, tree, list, and conventional grid views on the same task/data cohort. Record:
- task completion time;
- correctness/error rate;
- recall where relevant;
- navigation actions;
- viewport/device class;
- accessibility task completion;
- participant familiarity;
- missing/ambiguous evidence handling.

Pre-register task definitions and avoid using eye movement claims unless eye tracking is actually measured. A faster click path is not by itself proof of faster reading or better comprehension.

## Integration boundary

Do not add this view to SHE navigation until the proposal is reviewed and the prototype passes functional/accessibility tests plus a human-factors pilot. If integrated later, consume existing read-only snapshot/graph contracts; preserve source SHA, snapshot ID, coverage/freshness, and provenance links. Never map missing data to zero or collapse verified and candidate edges.
