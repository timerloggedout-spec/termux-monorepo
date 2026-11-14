---
name: context-relationship-graph
description: Build, query, validate, or operate a repository-native context relationship graph that connects files and AST symbols with GitHub commits, pull requests, issues, labels, native timeline events, comments, reviews, direct comment/review permalinks, and optional Linear freshness metadata. Use when asked to reconstruct context before a change, identify related PRs/issues/file touches, find missed connections, audit stale linked work, create a file-review or relationship timeline, prepare an evidence-backed Mermaid graph, or maintain a GitHub Actions–published relationship index.
---

# Context Relationship Graph

Use a **metadata-only, evidence-backed graph** before nontrivial repository changes when related files, GitHub history, review threads, or prior decisions could affect the work. Apply [the repository DO-statement mandate](../../../docs/ops/DO-STATEMENT-MANDATE.md) to new instructions, comments, receipts, and reports.

## Architectural position

The relationship graph supplies historical evidence for model comparisons and multi-PR analysis.

`GitHub/Actions/provider provenance → relationship corpus → observations/cohorts → DOE/MVT → Moneyball/3L0 → learning/manager evolution`

The canonical repository surface is:

`workspace/llm_map/context_relationships/`

Its `manifest.json`, `nodes.jsonl`, `edges.jsonl`, `matrix.json`, reports, and checkpoint describe collection coverage. A complete corpus is a sequence of bounded historical pages. Report each page as bounded coverage with explicit continuation state.

## Operating sequence

1. Read the repository’s agent instructions, proposal registry, and scope registry before collection. Use the existing canonical index only when its manifest/ref is current.
2. Query a narrow root first. Prefer `file:relative/path.py`, `symbol:relative/path.py:Qualname:line`, `pr:123`, `issue:123`, `label:name`, `scope:id`, or an exact GitHub issue/comment/review permalink. Use plain terms only when an exact root is unavailable.
3. Treat GitHub `cross-referenced` timeline events as **verified** `MENTIONS` relationships from the referencing issue or PR to the timeline target. Store event metadata and evidence URLs; exclude event, issue, review, and comment body text.
4. Treat exact local GitHub permalinks for `#issuecomment-`, `#pullrequestreview-`, and `#discussion_r` as verified references. Resolve the target node and its parent issue/PR when it exists; report a missing target precisely rather than guessing.
5. Use `--file-review-timeline relative/path.py` for a bounded chronology of touching PRs, reviews, review comments, direct comment links, and related verified context. Keep candidates separate.
6. Report **verified** relationships separately from **candidate** relationships. Label candidate links as hypotheses and keep them separate from verified facts.
7. Cite evidence URLs or source locations for every material verified connection. State collection bounds, omissions, parser failures, unresolved references, and historical coverage when they matter.
8. Update the central index only through the trusted publisher, the manual bounded reconciler, or the manual history-page backfill. Keep graph queries read-only and route GitHub or Linear writes through separately authorized workflows.

## Polyglot acceleration

The canonical graph remains Python/schema-owned. An optional Rust accelerator may be used for CPU-dense fragment fingerprinting and cost analysis:

- `archwiz/context_relationships/rust_accel/` owns the Rust hot path.
- `archwiz/context_relationships/rust_accel.py` is the safe Python adapter.
- `CRG_RUST_ACCEL=auto` degrades cleanly when the compiled binary is absent.
- `CRG_RUST_ACCEL=required` fails closed if the configured binary is unavailable or returns an invalid contract.
- Full BLAKE3-256 remains canonical; treat compact 128-bit refs as probabilistic identifiers.
- Zipf alpha is observational evidence only. Pointer selection uses frequency + explicit byte-cost savings.
- Language-specific providers may feed normalized fragment records through the same JSONL boundary; graph-write authority remains with the canonical publisher.

Preserve the existing graph datastore and compiler/schema/privacy checks while using the accelerator.

## Historical corpus contract

The historical backfill is explicit and resumable. Start from page `1`; inspect `history_window.next_start_page`; continue only while it is non-null.

A backfill page is **complete for its declared window**. Report the corpus coverage window and continuation state with every page. The corpus must retain:

- collection timestamp and source/ref;
- page/window bounds and continuation state;
- PR/issue/commit/review/comment metadata;
- exact evidence URLs and stable IDs;
- parser/API failure counts;
- excluded/sensitive path counts;
- verified vs candidate relationship classification.

Persist relationship metadata and evidence links; keep discussion bodies, session stores, browser profiles, credentials, tokens, and key material in their authorized source systems.

Every PR/issue is an observation candidate. Create Markdown receipts for notable measurements or promotions; keep all observations in the graph.

## Temporal evidence layer

The historical backfill now produces a second, append-only evidence layer under:

`workspace/llm_map/context_relationships/temporal/`

Each observation receives a deterministic `snapshot_id` bound to repository/ref, source SHA, observation time, and page bounds. Snapshot manifests retain:

- source SHA/ref and observation timestamp;
- history start/continuation pages;
- explicit coverage state;
- node/edge counts and content hashes;
- previous snapshot identity;
- structural delta counts.

Snapshots are immutable. Re-running the same observation may reuse the existing snapshot; preserve the original contents.

The temporal layer distinguishes:

`source → relationship → observation → snapshot → lineage`

A later observation may add, remove, change, or reclassify a relationship. Preserve prior evidence as an immutable snapshot and record later observations as deltas.

Use `temporal-current.json` for the latest materialized observation and `temporal/lineage.jsonl` for the append-only observation chain. The current graph remains the L1 relationship view; temporal snapshots are the L2 evidence/history layer consumed by SHE, longitudinal analysis, and future context reconstruction.

Declare historical coverage complete only when `history_coverage.status == "COMPLETE"` and `history_window.next_start_page == null`. Node/edge growth remains a progress measure, never the completeness verdict.

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

Use **context relationship Linear freshness** as a manual, read-only comparison. It resolves explicit repository GitHub URLs in bounded Linear metadata and emits `current`, `stale`, `missing`, or `ambiguous`. Route Linear changes through separately authorized workflows.

Run the deterministic contract before changing graph code:

```bash
python -m pytest tests/test_context_relationship_*.py -q
```

## DOE/MVT / Moneyball handoff

The graph supplies provenance and relationship evidence to experiment cohorts; decision selection remains in the experiment and evaluation lanes.

A valid experiment record binds:

`experiment_id + baseline_sha + candidate_sha + treatment/policy + suite + observation + outcome + provenance + confidence`

Moneyball/3L0 consumes these observations and compares integrated orchestration outcomes. Ground causal claims in measured treatments and outcomes; use comment volume, actor identity, and graph edge count as context only.

## Safety and interpretation

| Relationship class | Meaning | Permitted claim |
|---|---|---|
| `verified` | Direct AST, GitHub API, native timeline event, exact permalink, scope-registry, or explicit-reference evidence exists. | State the connection and cite its evidence. |
| `candidate` | A bounded heuristic such as file co-change or lexical similarity suggests a connection. | Recommend review and ground causality, ownership, and intent in direct evidence. |

When exact-root lookup for a typed selector or direct permalink returns empty, report an explicit empty match. Keep fuzzy results separate from exact roots. When a query reaches the node limit, disclose the bound and request an explicit wider query.

## Closeout standard

Summarize the chosen root, verified timeline, relevant candidate links, evidence locations, index/history bounds, and any required follow-up. When the graph returns an empty match, report the exact selector and coverage bounds.
