# Context Retrieval + goal-to-workflow — refTemplates entry (pattern from Box Architect)

- **Pattern source:** Box Architect (2026-11-08) — plain-language goal compiled into a workflow {stages + decisions} under existing permissions; its Context Retrieval engine (Nvidia Nemotron Retriever) cut tokens sent to downstream models by up to 90% in internal testing.
- **Status (owner order 2026-11-18):** IMPLEMENT the pattern, fleet form, DoE-scored.

## Fleet form
1. **Context retrieval in front of every dispatch** — the pool/dispatch path sends each executor only the context slice its task needs, retrieved and ranked per task, instead of the whole filing + history. The staging index is the substrate (materialized working set); the retriever is the missing scoring piece on top of it.
   - Metric of record: tokens per dispatch, before/after, per task class — DoE-scored; the 90% figure is the vendor's claim, the fleet number comes from its own receipts.
   - Directly serves the standing token-optimization priority (chat budget + arm context windows alike).
2. **Goal-to-workflow compilation** — plain-language goal to a staged workflow with decision points, under the fleet's existing permission gates {QUE template - claim classes - approval cards}. ArchWiz lane; the QUE filing is the current manual form of this compile.

## Bounds
- Retrieval never widens access: slices respect the same discretion rules as the source (a slice carries only what its task needs).
- Vendor internals (Box/Nemotron) are pattern only — no dependency; the retriever is built from fleet parts or scored as a pool participant like any other surface.
