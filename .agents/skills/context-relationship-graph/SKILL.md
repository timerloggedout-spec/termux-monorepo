---
name: context-relationship-graph
description: Build, query, validate, or operate a repository-native context relationship graph that connects files and AST symbols with GitHub commits, pull requests, issues, labels, native timeline events, comments, reviews, direct comment/review permalinks, and optional Linear freshness metadata. Use when asked to reconstruct context before a change, identify related PRs/issues/file touches, find missed connections, audit stale linked work, create a file-review or relationship timeline, prepare an evidence-backed Mermaid graph, or maintain a GitHub Actions–published relationship index.
---

# Context Relationship Graph

Use a **metadata-only, evidence-backed graph** before nontrivial repository changes when related files, GitHub history, review threads, or prior decisions could affect the work.

## Operating sequence

1. Read the repository’s agent instructions, proposal registry, and scope registry before collection. Use the existing canonical index only when its manifest/ref is current.
2. Query a narrow root first. Prefer `file:relative/path.py`, `symbol:relative/path.py:Qualname:line`, `pr:123`, `issue:123`, `label:name`, `scope:id`, or an exact GitHub issue/comment/review permalink. Use plain terms only when an exact root is unavailable.
3. Treat GitHub `cross-referenced` timeline events as **verified** `MENTIONS` relationships from the referencing issue or PR to the timeline target. Retain event metadata and evidence URL; never retain event, issue, review, or comment body text.
4. Treat exact local GitHub permalinks for `#issuecomment-`, `#pullrequestreview-`, and `#discussion_r` as verified references. Resolve the target node and its parent issue/PR when it exists; report a missing target precisely rather than guessing.
5. Use `--file-review-timeline relative/path.py` for a bounded chronology of touching PRs, reviews, review comments, direct comment links, and related verified context. Keep candidates separate.
6. Report **verified** relationships separately from **candidate** relationships. A candidate can direct investigation but must never be described as fact.
7. Cite evidence URLs or source locations for every material verified connection. State collection bounds, omissions, parser failures, unresolved references, and historical coverage when they matter.
8. Update the central index only through the trusted publisher, the manual bounded reconciler, or the manual history-page backfill. Never write GitHub or Linear content merely because a graph query found a relationship.

## Repository commands

Run from the repository root. Query an exact issue, a specific permalink, or a bounded file-review timeline:

```bash
python -m archwiz.context_relationships.query \
  --index workspace/llm_map/context_relationships \
  --query issue:86 --depth 2 --format markdown

python -m archwiz.context_relationships.query \
  --index workspace/llm_map/context_relationships \
  --query https://github.com/OWNER/REPO/pull/123#discussion_r456 \
  --depth 2 --format markdown

python -m archwiz.context_relationships.query \
  --index workspace/llm_map/context_relationships \
  --file-review-timeline archwiz/example.py --max-nodes 50 --format markdown
```

Produce a bounded Mermaid diagram only when a person has requested visual output:

```bash
python -m archwiz.context_relationships.query \
  --query file:archwiz/context_graph_builder.py \
  --depth 2 --max-nodes 25 --format mermaid --output /tmp/context.mmd
```

Use the normal publisher for incremental updates. Use the manual reconciliation only for a bounded refresh. Use **context relationship historical backfill** for complete history in explicit pages: start from page `1`, inspect `history_window.next_start_page` in the summary, then manually resume only while it is non-null.

Use **context relationship Linear freshness** only as a manual, read-only comparison. It resolves explicit repository GitHub URLs in bounded Linear metadata, emits `current`, `stale`, `missing`, or `ambiguous`, and must never update Linear or publish Linear descriptions.

Run the deterministic contract before changing graph code:

```bash
python -m pytest tests/test_context_relationship_*.py -q
```

## Safety and interpretation

Do not persist PR, issue, timeline-event, review, comment, or Linear description bodies. Extract explicit internal reference tokens only in memory. Exclude session stores, browser profiles, credentials, tokens, key material, generated artifacts, oversized files, and any path in `config/context_relationships/scope_registry.json`. Keep API collection read-only; keep pull-request validation read-only and secret-free.

| Relationship class | Meaning | Permitted claim |
|---|---|---|
| `verified` | Direct AST, GitHub API, native timeline event, exact permalink, scope-registry, or explicit-reference evidence exists. | State the connection and cite its evidence. |
| `candidate` | A bounded heuristic such as file co-change or lexical similarity suggests a connection. | Recommend review; do not assert causality, ownership, or intent. |

If a typed selector or direct permalink has no exact root, return no match; do not fall back to unrelated fuzzy results. If a query reaches the node limit, disclose the bound instead of silently widening the graph.

## Current bounded record

For AR-11 provider command library review on 2026-08-20, the exact root `pr:278` was queried at depth `2` with a maximum of `30` nodes. The canonical index returned no matching root, verified timeline, or candidates because the newly opened PR was not yet in published index coverage. The result is recorded in the proposal manifest and process card; no generated index file was edited, and no relationship was inferred.

## Closeout standard

Summarize the chosen root, verified timeline, relevant candidate links, evidence locations, index/history bounds, and any required follow-up. If no relationship is found, say so precisely rather than inferring one from naming similarity.
