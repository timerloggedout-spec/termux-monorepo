---
type: object
cluster: knowledge
universe: live
status: verified
entity: workspace/llm_map/context_relationships/
verified_at: 2026-08-18
---

# Context Relationship Index

The **Context Relationship Index** is the repository’s generated, metadata-only evidence graph. It connects repository files and bounded Python AST symbols with GitHub commits, pull requests, issues, labels, native GitHub `cross-referenced` timeline events, comments, reviews, exact comment/review permalinks, changed-file touches, and explicit internal references.

## Why this shape

A conventional file map cannot reliably surface the historical and discussion connections that explain a change. The index makes those relationships queryable without treating full conversation content, session data, browser data, secrets, or heuristic suggestions as shared facts.

## Shape

- `config/context_relationships/schema.json` owns the canonical node, edge, evidence, and relationship vocabulary.
- `config/context_relationships/scope_registry.json` owns scopes, path exclusions, and collection size bounds.
- `archwiz/context_relationships/` owns source collection, GitHub metadata collection, deterministic merge/compile, query, and the builder.
- `workspace/llm_map/context_relationships/` holds only canonical generated records, manifest, reports, and a checkpoint; it is not hand-edited.
- `.github/workflows/context-relationship-*.yml` own read-only pull-request validation, trusted staging publication, bounded reconciliation, manual history-page backfill, and manual read-only Linear freshness comparison.

Citations: `config/context_relationships/schema.json`, `config/context_relationships/scope_registry.json`, `archwiz/context_relationships/`, `.github/workflows/context-relationship-*.yml`.

## Connected to

- **owns:** the normalized relationship and evidence representation used for contextual reconnaissance.
- **owned-by:** the schema, scope registry, compiler, and trusted index builder.
- **joins:** an agent’s proposed change to exact file/symbol/history roots, verified evidence, and clearly marked candidate links.
- **looks-like-but-is-not:** a full-text discussion archive, a substitute for source review, proof of causal intent from candidates, or authority to post GitHub/Linear comments, labels, or merges.

## If you change this

- **Hits:** schema compatibility, collector redaction/exclusion behavior, query semantics, generated-artifact manifests, and all three dedicated workflows.
- **Does not hit:** unrelated mapper outputs, browser/session state, protected GitHub operations, or causal claims derived only from candidate edges.

## Surfaces

| Surface | Role |
|---|---|
| Schema and compiler | Enforce stable IDs, valid relationships, evidence, and verified/candidate separation. |
| Scope registry | Bounds source collection and excludes sensitive or generated paths. |
| GitHub collector | Reads bounded metadata, native cross-reference events, exact permalink targets, and explicit references only in memory. |
| Canonical index | Offers queryable JSONL, sparse matrix, manifest, reports, and checkpoint. |
| Query/Mermaid renderer | Produces bounded relationship timelines, direct permalink lookups, file-review projections, and optional diagrams with candidate styling. |
| Publisher, reconciliation, and backfill workflows | Build and commit canonical artifacts only from trusted staging contexts; page backfill reports coverage explicitly. |
| Linear freshness workflow | Compares explicit GitHub mappings against bounded Linear metadata read-only and emits `current`, `stale`, `missing`, or `ambiguous` for review. |

## See

- Process: [`../../processes/context-relationship-reconnaissance.md`](../../processes/context-relationship-reconnaissance.md)
- Process: [`../../processes/change-and-validate.md`](../../processes/change-and-validate.md)
- Source: [`AGENTS.md`](../../../../AGENTS.md)
