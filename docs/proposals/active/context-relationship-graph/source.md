# Source — Context Relationship Graph

## Operator Request

The operator requested a fuzzy AST-aware context search that builds a mapped graph matrix and timeline from related pull requests, issues, linked comments, labels, and file-touch history. The purpose is to prevent missed connections at request initiation and improve consolidation before agents implement changes.

## Reconnaissance Findings

The current `master-staging` branch contains a local context graph builder, graph query helper, AST similarity tensors, and a file graph. Those tools are useful precedents but do not satisfy the requested GitHub-native relationship history: the dependency index reports no dependencies, and the builder reads from a home-directory-wide scan plus session stores. Those inputs are neither repository-bounded nor suitable for a durable shared index.

PR #232 was merged into `master` on 2026-08-18 and appears in the current `master-staging` history. Its ICM-07 documentation-only deferral was an implementation boundary for that merged integration work; it does not own this separate, operator-authorized successor proposal.

## Architecture Decision

Use a versioned repository snapshot as the canonical index. The compiler reads metadata-only records and emits deterministic JSON artifacts under `workspace/llm_map/context_relationships/`. It will not require an external graph service in the first version. A local ephemeral cache may be introduced later for query speed, but binary caches are not canonical content.

The initial compiler is intentionally separate from collection. It accepts a normalized seed document, validates schema and relationship endpoints, generates stable IDs, normalizes and deduplicates records, produces a sparse relation matrix, and writes an evidence manifest. This creates a testable contract before GitHub API collection and automated publication are introduced.

## Canonical Sources and Exclusions

| Source class | Initial treatment | Reason |
|---|---|---|
| Repository files and AST metadata | Allowed, path-bounded, parser-annotated | Required for source relationships and fuzzy context roots. |
| GitHub issue/PR/commit/label metadata and explicit references | Allowed, source-URL-backed | Required for verified collaboration history. |
| Comments and reviews | Metadata plus explicit references only by default | Preserves evidence without duplicating full discussion text. |
| Session stores, chat exports, `thinking_content`, browser profiles, cookies, tokens, and `.env` files | Rejected | Sensitive, user-private, non-portable, or prohibited by repository hygiene rules. |
| Generated/vendor/binary/oversized code | Excluded or reported | Prevents noisy or misleading source relations. |

## Initial Relationship Vocabulary

| Relationship | Classification | Meaning |
|---|---|---|
| `DEFINES`, `IMPORTS`, `TOUCHES`, `CHANGED_IN`, `MENTIONS`, `CLOSES`, `REFERENCES`, `LABELED_AS`, `IN_SCOPE` | Verified | Exact parser, GitHub, or configuration evidence is present. |
| `CO_CHANGED_WITH`, `SIMILAR_TO`, `POSSIBLE_CONTEXT` | Candidate | Deterministic score and evidence factors are present; it is not a factual assertion. |

## References

- [Root agent guidance](../../../AGENTS.md)
- [Repository-native ICM integration](../../ICM-ARCHITECT-INTEGRATION.md)
- [Existing local context builder](../../../archwiz/context_graph_builder.py)
- [Existing graph query helper](../../../workspace/llm_map/graph_query.py)
- [GitHub pull request #232](https://github.com/timerloggedout-spec/termux-monorepo/pull/232)

## Validation Record

The focused contract suite passes with **25 tests**, covering schema/compilation, source and GitHub collectors, merge behavior, historical retention, exact/fuzzy query semantics, Mermaid generation, workflow trust boundaries, and AGENTS/ICM/skill integration. Focused `ruff`, bytecode compilation, and `git diff --check` also pass.

A live bounded bootstrap against `timerloggedout-spec/termux-monorepo` produced 4,804 nodes, 7,099 verified edges, and 1,579 separately marked candidate edges. The exact `pr:232` root resolved to the merged ICM integration pull request with evidence-backed commit and file-touch history. A subsequent one-item incremental window retained that PR and its timeline even though the fresh collection could not rediscover it, proving canonical-history retention.

The required repository-wide gates remain blocked by a pre-existing conflict in `scripts/ci/repo_gate.py:139`: `repo_gate.py` raises `IndentationError: unexpected unindent`, and `termux_smoke.py` reports that same required failure while its other checks pass. This proposal does not modify that unrelated gate script.
