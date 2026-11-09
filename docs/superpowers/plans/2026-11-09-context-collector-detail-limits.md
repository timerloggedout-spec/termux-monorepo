# CRG-16 — Independent GitHub detail endpoint bounds

**Status:** implementation in review  
**Branch:** `fix/context-collector-detail-limits-2026-11-09`  
**Base:** current canonical `master` at branch creation  
**Scope:** collector correctness only; no corpus generation or checkpoint promotion.

## Problem

The historical collector uses `max_items` to bound the issue and pull-request history pages. It also incorrectly reuses that page limit for per-PR changed-file enumeration and per-item issue/PR timeline enumeration. The repository-wide commit sample and per-PR commit enumeration also need distinct limits. A small history window must not silently truncate the supporting evidence for each selected PR or issue.

## Contract

| Argument | Scope | Default |
|---|---|---:|
| `max_items` | issues and pull requests in each history page | existing workflow setting |
| `max_commits` | repository-wide commit sample | existing workflow setting |
| `max_files_per_pr` | changed files for each PR | 3,000 |
| `max_commits_per_pr` | commits for each PR | 250 |
| `max_timeline_events_per_item` | timeline events for each issue/PR | 1,000 |
| `max_comments_per_item` | comments/reviews/review comments for each item | existing workflow setting |

All limits must be positive integers. The collector report must persist the effective limits so downstream consumers can interpret coverage correctly.

## Implementation

- Add independent per-PR file, per-PR commit, and per-item timeline limits to `collect_github_seed`.
- Keep history pagination and repository commit sample limits independent.
- Expose the limits through the collector CLI and `build_index` API/CLI.
- Pass explicit bounds from `.github/workflows/context-relationship-backfill.yml`.
- Add a regression test proving a small history page does not truncate PR files, PR commits, or timeline events.
- Record the effective values in the GitHub collector report.

## Acceptance

1. Focused collector and builder tests pass.
2. Repository gate and Termux smoke pass on the exact PR head.
3. No generated corpus, manifest, checkpoint, or temporal snapshot is changed by this implementation.
4. Independent review has no unresolved actionable findings.
5. The branch is based on the current canonical master at PR creation; any subsequent drift is reconciled before merge.
