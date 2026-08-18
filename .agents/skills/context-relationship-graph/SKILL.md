---
name: context-relationship-graph
description: Build, query, validate, or operate a repository-native context relationship graph that connects files and AST symbols with GitHub commits, pull requests, issues, labels, comments, reviews, and explicit references. Use when asked to reconstruct context before a change, identify related PRs/issues/file touches, find missed connections, create a relationship timeline, prepare an evidence-backed Mermaid graph, or maintain a GitHub Actions–published relationship index.
---

# Context Relationship Graph

Use a **metadata-only, evidence-backed graph** before nontrivial repository changes when related files, GitHub history, or prior decisions could affect the work.

## Operating sequence

1. Read the repository’s agent instructions, proposal registry, and scope registry before collection. Use the existing canonical index when its manifest/ref is current.
2. Query a narrow root first. Prefer `file:relative/path.py`, `symbol:relative/path.py:Qualname:line`, `pr:123`, `issue:123`, `label:name`, or `scope:id`. Use plain terms only when an exact root is unavailable.
3. Report **verified** relationships separately from **candidate** relationships. A candidate can direct investigation but must never be described as fact.
4. Cite evidence URLs or source locations for every material verified connection. State collection bounds, omissions, parser failures, and unresolved references when they matter.
5. Update the central index only through the trusted publisher or a deliberate operator build. Never write GitHub comments or labels merely because a graph query found a relationship.

## Repository commands

Run from the repository root. Query the current index:

```bash
python -m archwiz.context_relationships.query \
  --index workspace/llm_map/context_relationships \
  --query issue:86 --depth 2 --format markdown
```

Produce a bounded Mermaid diagram only when a person has requested visual output:

```bash
python -m archwiz.context_relationships.query \
  --query file:archwiz/context_graph_builder.py \
  --depth 2 --max-nodes 25 --format mermaid --output /tmp/context.mmd
```

Run the deterministic fixture contract before changing graph code:

```bash
python -m pytest tests/test_context_relationship_*.py -q
```

Use the GitHub Actions publisher for normal updates. Use a manual full refresh only for a bounded reconciliation or recovery; preserve the generated checkpoint and let the builder replace canonical artifacts atomically.

## Safety constraints

Do not persist PR, issue, review, or comment bodies. Extract only explicit internal reference tokens in memory. Exclude session stores, browser profiles, credentials, tokens, key material, generated artifacts, oversized files, and any path in `config/context_relationships/scope_registry.json`. Keep API scope read-only for collection; keep pull-request validation read-only and secret-free.

## Interpretation rules

| Relationship class | Meaning | Permitted claim |
|---|---|---|
| `verified` | Direct AST, GitHub API, scope-registry, or explicit-reference evidence exists. | State the connection and cite its evidence. |
| `candidate` | A bounded heuristic such as file co-change or lexical similarity suggests a connection. | Recommend review; do not assert causality, ownership, or intent. |

If a query has no exact root, return fuzzy matches with score and token-overlap reason. If a query reaches the node limit, disclose the bound instead of silently widening the graph.

## Closeout standard

Summarize the chosen root, verified timeline, relevant candidate links, evidence locations, and any required follow-up. If no relationship is found, say so precisely rather than inferring one from naming similarity.
