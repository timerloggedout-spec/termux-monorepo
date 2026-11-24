# Master–staging reconciliation

Scope: reconcile the permanent `master-staging` integration spine with canonical `master`, while preserving staging-only work and keeping Termux smoke execution scoped to Termux runtime operations.

## MSR-001 — Reconcile branch ancestry

- **DO:** Integrate the current canonical `master` history into `master-staging` through a reviewable merge.
- **DO:** Preserve all staging-only commits and their provenance.
- **DO:** Keep the promotion direction explicit: `master` → `master-staging` for synchronization; staging → master only through separately reviewed, selective promotion.
- **Acceptance:** the resulting staging history contains the selected master head as an ancestor; staging-only work remains reachable; the merge has no unresolved conflicts; required checks validate the resulting head.

## MSR-002 — Isolate Termux smoke scope

- **DO:** Keep `.github/workflows/termux-smoke.yml` limited to Termux runtime smoke checks and their focused tests.
- **DO:** Move bucket-headroom contract tests into a dedicated workflow with path-scoped triggers.
- **DO:** Keep the bucket-headroom tests and their workflow contract intact.
- **Acceptance:** the Termux workflow invokes only Termux smoke checks; the dedicated bucket-headroom workflow runs both bucket-headroom test modules; focused regression tests prove the separation.

## Execution constraints

- Preserve canonical branch and workflow ownership.
- Use small, evidence-backed commits.
- Validate the exact resulting SHA and workflow runs before promotion.
- Record committed, executed, validated, and promoted as separate states.

## Recon evidence — 2026-11-24

- Canonical `master` head: `1f57496874f090a2c734f8134c24e20881593c01`.
- Merge base: `c3ea1e1c24a03b1b199e6c36521f4be9b367c733`.
- `master-staging` is 56 commits ahead and 31,741 commits behind `master`; GitHub reports the refs as diverged with 191 changed paths.
- `master` `.github/workflows/termux-smoke.yml` runs `tests/test_bucket_headroom.py` and `tests/test_bucket_headroom_workflow.py` in a dedicated step. Those are bucket-headroom contract tests, not Termux runtime smoke operations.
- `master-staging` `.github/workflows/termux-smoke.yml` runs the Termux smoke regression suite and Termux smoke script without the bucket-headroom test step.
- The Gemini quota action also differs: `master` uses a 1,450 daily limit and cache restore; `master-staging` retains a 900 safety-margin limit and lookup-only cache behavior. The canonical version should flow into staging through the ancestry reconciliation.
- The branch comparison supports a master-to-staging synchronization PR. It does not support a wholesale staging-to-master promotion.


## Current execution gate — 2026-11-24

- Proposal and branch are committed.
- Linear TER issue creation is blocked by the workspace free-issue limit.
- Execution remains on hold until an existing authorized TER issue is linked or the workspace issue limit is raised.
- The branch-sync PR and workflow changes remain uncreated; this preserves the review gate and avoids an untracked repository change.
