---
type: process
universe: live
status: verified
consumes:
  - ../objects/knowledge/context-relationship-index.md
  - ../../../AGENTS.md
  - ../../../docs/proposals/registry.yaml
produces:
  - bounded context query
  - verified relationship evidence
  - separately labeled candidate links
verified_at: 2026-08-18
---

# Context Relationship Reconnaissance

Before a nontrivial code, workflow, consolidation, or documentation change, an agent can use the **Context Relationship Index** to reconstruct the smallest relevant history and source neighborhood. The process is a planning aid; it does not replace source review, proposal governance, or human authorization.

## Input → Movement → Output

A scoped work item and a precise root—file, symbol, pull request, issue, label, scope, or exact GitHub permalink—are the input. The agent queries the canonical index within explicit depth/node bounds, reviews the verified timeline and any separately ranked candidates, then cites material evidence in its plan or closeout. The output is a narrow contextual record that exposes connections and uncertainty without making speculative claims.

## Why this shape

Broad repository crawling produces noisy, stale, and potentially sensitive context. A schema-bound, **metadata-only** index with evidence URLs and path exclusions offers a repeatable middle layer between a task request and deep source inspection.

## Steps

1. Read `AGENTS.md`, the active proposal item, and `objects/knowledge/context-relationship-index.md`. Confirm that the intended work is registered and that the index manifest/ref is appropriate for the task.
2. Start with an exact query root such as `file:archwiz/context_graph_builder.py`, `pr:232`, `issue:86`, `label:P1`, `scope:context-relationships`, or a direct GitHub `#issuecomment-`, `#pullrequestreview-`, or `#discussion_r` permalink. Use `--file-review-timeline` for a review chronology tied to one exact file. Use fuzzy text only when no exact root exists, and retain the score and overlap reason.
3. Keep traversal bounded. State the chosen depth and node limit; if the result is truncated, refine the root rather than silently widening collection.
4. Treat AST, scope-registry, GitHub API, commit, native GitHub `cross-referenced` timeline events, exact permalinks, and explicit-reference edges as **verified** only when their evidence is present. Treat lexical similarity and co-change links as **candidates** only.
5. Cite relevant evidence URLs/source locations in the work plan or closeout. Review candidate links manually before expanding scope; do not perform autonomous comment, label, merge, or configuration writes from graph results.
6. If the canonical index is stale or unavailable, use the trusted publisher or an explicitly authorized bounded operator build. For archive coverage, use manual history-page backfill and record the reported `next_start_page`; do not claim full history until it is null. Use the optional Linear freshness comparison only read-only and only for explicit GitHub mappings; its `stale`, `missing`, and `ambiguous` states require review, not an automatic Linear write. Do not hand-edit generated JSONL, matrix, manifest, reports, or checkpoint files.

## If you change this

- **Hits:** agent planning behavior, query/closeout expectations, index freshness handling, and the line between verified context and investigation candidates.
- **Does not hit:** proposal approval, protected GitHub writes, or the source-of-truth status of files and repository governance documents.

## Surfaces

| Surface | Role |
|---|---|
| Agent | Selects a narrow root, records bounds, and distinguishes fact from lead. |
| Canonical index | Supplies normalized records and evidence-backed relationships. |
| Source and GitHub evidence | Remain the authoritative evidence behind a graph edge. |
| Candidate link | Directs manual investigation only. |
| Operator | Authorizes full refreshes, historical page backfill, or any downstream GitHub/Linear write. |

## See

- Object: [`../objects/knowledge/context-relationship-index.md`](../objects/knowledge/context-relationship-index.md)
- Process: [`change-and-validate.md`](change-and-validate.md)
- Source: [`AGENTS.md`](../../../AGENTS.md)
