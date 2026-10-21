# Historical Backfill Promotion Gate

## Purpose

This document records the safety contract for the Historical Corpus backfill. It supersedes the earlier `master-staging` instructions below, which describe an obsolete branch topology and must not be used to authorize promotion.

## Current authoritative evidence

The canonical source is `workspace/llm_map/context_relationships/manifest.json` on `master`.

At the latest inspected snapshot (`2026-10-15T19:16:02.945529Z`):

- `default_branch = master`
- history window starts at page 13 and `next_start_page = null`
- issue and pull-request history-window completion flags are true
- nodes: 30,978; edges: 52,624; verified edges: 47,845; candidate edges: 4,779
- `github_report.checkpoint_eligible = false`
- one unresolved internal reference remains
- 14 source parser failures remain

**Important:** exhausted pagination is not equivalent to a promotable/validated checkpoint. The manifest itself marks checkpoint eligibility false. Do not promote or label the corpus fully validated based only on `next_start_page = null`.

Canonical artifacts:
- Manifest: `workspace/llm_map/context_relationships/manifest.json`
- Bounded collector: `.github/workflows/context-relationship-backfill.yml`
- Runtime watcher: `.github/workflows/context-relationship-backfill-watcher.yml`
- Tracking issue: [#522](https://github.com/timerloggedout-spec/termux-monorepo/issues/522)

## Current workflow behavior

The collector checks out `master`, resumes from the manifest's `next_start_page`, builds one bounded history window, validates the delta and hashes, and writes only the bounded corpus change back to `master`. It is triggered by relevant corpus pushes, an hourly schedule, or explicit dispatch.

The watcher records run/attempt/SHA, job and step states, artifact names, and a structured observer-only receipt. A watcher receipt is runtime evidence, not a corpus-promotion decision.

The earlier `historical-backfill-promotion-gate.yml` referenced by the legacy staging design is **not present on current master**. Do not claim that a dedicated promotion workflow currently enforces the final checkpoint gate.

## Required promotion conditions

Promotion requires all of the following, evidenced against the current master SHA:

1. Record source SHA/ref, start page, next page, input/schema/manifest hashes, and the bounded diff.
2. Confirm history-window pagination is exhausted for the intended scope.
3. Resolve or explicitly disposition all parser failures and unresolved internal references; any accepted exclusions must be documented and test-covered.
4. Run the canonical corpus validators and record their actual result.
5. Verify node/edge counts, verified/candidate classification, and reference integrity without interpreting missing data as zero.
6. Inspect the Actions run, jobs, steps, artifacts, and receipt for the exact run/attempt and SHA.
7. Confirm the diff contains only the intended corpus delta and required metadata.
8. Record an explicit promotion decision. If any gate is absent or fails, keep `checkpoint_eligible = false`.

A successful workflow conclusion, elapsed time, branch mergeability, or `next_start_page = null` alone is not evidence that these conditions passed.

## Historical note

The previous version described `master-staging` as the continuation target and cited 2026-08/09 manifest snapshots. That record is retained in repository history, but its branch-specific directions are obsolete after the collector was re-anchored to current `master`.
