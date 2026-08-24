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

## Timeline, Permalink, Backfill, and Freshness Extension

The supplied GitHub mobile timeline case was verified against the native issue timeline API: issue `#236` carries GitHub’s `cross-referenced` event from issue `#243` (**Game Teams**). The collector normalizes this as a verified `MENTIONS` edge from `issue:243` to `issue:236`, separately from the explicit body-derived `REFERENCES` edge. The event is source-URL-backed and does not retain timeline, issue, or comment body text.

Exact local GitHub `#issuecomment-`, `#pullrequestreview-`, and `#discussion_r` URLs now resolve to their typed nodes, parent issue/PR, and verified reference edges. Review comments with a safe path now emit an explicit verified file-touch relation, which powers the bounded `--file-review-timeline` projection without broad PR-wide review noise.

The operator-controlled historical backfill now reports `history_window` coverage. A live first-page run collected 100 issue and 100 pull-request records and correctly reported `next_start_page: 2`; this is an explicit partial-history state, not a claim of complete archive coverage. Successive manual page windows retain canonical history and continue until the reported next page is null.

The enabled Linear integration was tested read-only against a bounded export of repository-linked records. The metadata-only comparator produced 1 `stale`, 60 `missing`, and 15 `ambiguous` mappings in the partial GitHub history window; it retained only Linear identifiers, titles, URLs, status/timestamps, explicit GitHub targets, comparison timestamps, and status. It neither writes to Linear nor emits descriptions/comment bodies. Missing and ambiguous states are expected during a partial GitHub backfill and remain review prompts rather than assertions.

## Extension Validation Record

The focused contract suite passes with **30 tests**, covering schema/compilation, source and GitHub collectors, nested native timeline events, exact comment/review permalinks, file-review projections, historical-window reporting, metadata-only Linear freshness comparison, workflow trust boundaries, and AGENTS/ICM/skill integration. Focused `ruff`, bytecode compilation, and `git diff --check` also pass.

A live metadata-only build of the first 100 updated issues and pull requests produced 4,870 nodes, 7,206 verified edges, and 311 candidates. An exact `issue:236` query contains the verified `MENTIONS` relationship from **Game Teams** `#243` to `.APK Investigation List` `#236`, matching the supplied GitHub timeline event. The temporary live artifacts are not canonical repository content.

## PR #244 Review-Finding Disposition

The current PR #244 head was checked against the submitted review findings before any additional implementation was attempted. The publisher already pins its checkout and build ref to `master-staging`; the publisher, reconciler, and backfill workflows share the `context-relationship-writer-master-staging` writer lock; and the source collector rejects symlinks plus records recursion failures without aborting collection. The GitHub collector classifies repeated closing and ordinary references by match span, rejects mismatched checkpoint repository/ref identity, and marks truncated collection windows checkpoint-ineligible. The query enforces positive `fuzzy_limit` values and truncates roots before traversal. The saved focused contract command, `PYTHONPATH=. pytest tests/test_context_relationship_*.py -q`, passed **39 tests** on the current head. This closes CRG-14 as a verified no-new-code review disposition; routine full-gate/review workflow results remain the PR promotion evidence.
