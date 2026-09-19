---
name: context-relationship-graph
description: Build, query, validate, or operate a repository-native context relationship graph that connects files and AST symbols with GitHub commits, pull requests, issues, labels, native timeline events, comments, reviews, direct comment/review permalinks, and optional Linear freshness metadata. Use when asked to reconstruct context before a change, identify related PRs/issues/file touches, find missed connections, audit stale linked work, create a file-review or relationship timeline, prepare an evidence-backed Mermaid graph, or maintain a GitHub Actions–published relationship index.
---

# Context Relationship Graph

Use a **metadata-only, evidence-backed graph** before nontrivial repository changes when related files, GitHub history, review threads, or prior decisions could affect the work.

## Architectural position

The relationship graph is the **historical evidence substrate**, not a model leaderboard and not a single PR receipt.

`GitHub/Actions/provider provenance → relationship corpus → observations/cohorts → DOE/MVT → Moneyball/3L0 → learning/manager evolution`

The canonical repository surface is:

`workspace/llm_map/context_relationships/`

Its `manifest.json`, `nodes.jsonl`, `edges.jsonl`, `matrix.json`, reports, and checkpoint describe collection coverage. A complete corpus is a sequence of bounded historical pages; a single page is never silently treated as full history.

## Operating sequence

1. Read the repository’s agent instructions, proposal registry, and scope registry before collection. Use the existing canonical index only when its manifest/ref is current.
2. Query a narrow root first. Prefer `file:relative/path.py`, `symbol:relative/path.py:Qualname:line`, `pr:123`, `issue:123`, `label:name`, `scope:id`, or an exact GitHub issue/comment/review permalink. Use plain terms only when an exact root is unavailable.
3. Treat GitHub `cross-referenced` timeline events as **verified** `MENTIONS` relationships from the referencing issue or PR to the timeline target. Retain event metadata and evidence URL; never retain event, issue, review, or comment body text.
4. Treat exact local GitHub permalinks for `#issuecomment-`, `#pullrequestreview-`, and `#discussion_r` as verified references. Resolve the target node and its parent issue/PR when it exists; report a missing target precisely rather than guessing.
5. Use `--file-review-timeline relative/path.py` for a bounded chronology of touching PRs, reviews, review comments, direct comment links, and related verified context. Keep candidates separate.
6. Report **verified** relationships separately from **candidate** relationships. A candidate can direct investigation but must never be described as fact.
7. Cite evidence URLs or source locations for every material verified connection. State collection bounds, omissions, parser failures, unresolved references, and historical coverage when they matter.
8. Update the central index only through the trusted publisher, the manual bounded reconciler, or the manual history-page backfill. Never write GitHub or Linear content merely because a graph query found a relationship.

## Historical corpus contract

The historical backfill is explicit and resumable. Start from page `1`; inspect `history_window.next_start_page`; continue only while it is non-null.

A backfill page is **complete for its declared window**, not globally complete. The corpus must retain:

- collection timestamp and source/ref;
- page/window bounds and continuation state;
- PR/issue/commit/review/comment metadata;
- exact evidence URLs and stable IDs;
- parser/API failure counts;
- excluded/sensitive path counts;
- verified vs candidate relationship classification.

Do not persist discussion bodies, session stores, browser profiles, credentials, tokens, or key material.

Every PR/issue is an observation candidate. Not every PR needs a Markdown receipt. Receipts are human-readable projections of notable measurements or promotions.

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

Use the normal publisher for incremental updates. Use the manual reconciliation only for a bounded refresh. Use **context relationship historical backfill** for complete history in explicit pages.

Use **context relationship Linear freshness** only as a manual, read-only comparison. It resolves explicit repository GitHub URLs in bounded Linear metadata, emits `current`, `stale`, `missing`, or `ambiguous`, and must never update Linear or publish Linear descriptions.

Run the deterministic contract before changing graph code:

```bash
python -m pytest tests/test_context_relationship_*.py -q
```

## DOE/MVT / Moneyball handoff

The graph does not decide which provider/model/manager wins. It supplies provenance and relationship evidence to experiment cohorts.

A valid experiment record binds:

`experiment_id + baseline_sha + candidate_sha + treatment/policy + suite + observation + outcome + provenance + confidence`

Moneyball/3L0 consumes these observations and compares integrated orchestration outcomes. It must not infer causality from comment volume, actor identity, or graph edge count.

## Safety and interpretation

| Relationship class | Meaning | Permitted claim |
|---|---|---|
| `verified` | Direct AST, GitHub API, native timeline event, exact permalink, scope-registry, or explicit-reference evidence exists. | State the connection and cite its evidence. |
| `candidate` | A bounded heuristic such as file co-change or lexical similarity suggests a connection. | Recommend review; do not assert causality, ownership, or intent. |

If a typed selector or direct permalink has no exact root, return no match; do not fall back to unrelated fuzzy results. If a query reaches the node limit, disclose the bound instead of silently widening the graph.

## Closeout standard

Summarize the chosen root, verified timeline, relevant candidate links, evidence locations, index/history bounds, and any required follow-up. If no relationship is found, say so precisely rather than inferring one from naming similarity.
