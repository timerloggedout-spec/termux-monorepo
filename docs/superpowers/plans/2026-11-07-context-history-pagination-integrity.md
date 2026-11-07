# Context History Pagination Integrity — Implementation Plan

**Proposal:** `context-relationship-graph`
**Work item:** CRG-16
**Status:** executing
**Base:** canonical `master`; PR #5056
**Scope:** prevent bounded history-page limits from truncating per-PR relationship detail.

## Problem

The collector reused `max_items` (the issue/PR history endpoint page limit) as the limit for each PR's changed-file list, and reused `max_commits` (the repository-wide commit sample limit) as the limit for each PR's commit list. A page-size change could therefore silently omit `TOUCHES` and `HAS_COMMIT` edges for PRs with larger detail collections. Later history pages do not resume these per-PR endpoints.

The history endpoint also returns both issues and pull-request-shaped records. Its raw result count must not be labeled as the count of actual issues.

## Design

Keep four independent controls:

| Control | Purpose | Default |
|---|---|---:|
| `max_items` | issue endpoint and PR endpoint history page size | 50 |
| `max_commits` | repository-wide commit sample | 50 |
| `max_files_per_pr` | changed files fetched for each PR | 3,000 |
| `max_commits_per_pr` | commits fetched for each PR | 250 |

The per-PR defaults respect GitHub's documented endpoint ceilings. Record the effective values in the collector report. Preserve old Python call sites by appending optional parameters with defaults.

## Files

- `archwiz/context_relationships/github_collector.py`: add independent per-PR arguments; use them only for the corresponding PR detail endpoints; report effective limits.
- `archwiz/context_relationships/build_index.py`: thread independent limits through the builder and CLI; validate positive values.
- `.github/workflows/context-relationship-backfill.yml`: pass the independent PR detail caps; retain page-size 50 and repository commit sample 50; include the focused collector regression test in the workflow path filter.
- `tests/test_context_relationship_github_collector.py`: assert a history page size of 1 does not constrain PR file/commit endpoints.
- `docs/ops/HISTORICAL-CORPUS-BACKFILL-STATUS.md`: distinguish issue-endpoint result count from actual issue count and record all four limits.
- `docs/ops/SHE-INTEGRATION-FINDINGS.md`: reconcile the current canonical manifest and accurately classify runtime/deployment evidence.
- `docs/proposals/active/context-relationship-graph/ITEMS.md` and `MANIFEST.md`: register and track CRG-16.
- This plan: durable implementation record.

## Validation

1. RED: add a focused collector test that observes the per-endpoint limits independently of the history page size.
2. GREEN: run `python -m pytest tests/test_context_relationship_github_collector.py -q`.
3. Run `python -m pytest tests/test_context_relationship_*.py -q`.
4. Run `python3 scripts/ci/repo_gate.py` and `python3 scripts/ci/termux_smoke.py`.
5. Run `python3 scripts/proposals/validate_registry.py`.
6. Re-fetch PR head SHA and wait for the same-head context relationship, repo-gate, termux-smoke, proposal registry, and review results. Queued/cancelled checks are not passes.
7. Keep the PR draft until required checks and independent review are terminal. Do not merge or claim a corpus page was executed as part of this code change.

## Acceptance

- History page bounds remain 50 for issues and PRs.
- Repository-wide commit sample remains 50.
- Each PR's changed-file collection is independently bounded at 3,000.
- Each PR's commit collection is independently bounded at 250.
- Collector report records both per-PR caps.
- Regression test proves history page size does not truncate PR detail endpoints.
- Current status docs distinguish endpoint records from actual issues.
- Required dual gates and proposal lifecycle validation pass on the same immutable PR head.
- No generated corpus, manifest, checkpoint, or native Hex artifact is fabricated or modified.
