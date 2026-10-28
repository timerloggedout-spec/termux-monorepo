# ML PR lane classify — production run of the vocab-v2 PR classifier

Contract for `.github/workflows/ml-pr-lane-classify.yml` +
`ml/pipelines/production_classify.py`. Closes gap 1 of
docs/ops/TIER1-CLASSIFIER-RECON-2026-10-28.md: `classify_pr`
(ml/pipelines/lanes) had no production trigger — the keep-alive
workflow only unit-tests the package when ml/** paths change (last
fired 2026-10-21), so the fleet's own PR-disposition vocabulary
classified nothing live.

## What runs

Daily 05:37 UTC + workflow_dispatch. The collector is invoked as a
module from the repo root (`python3 -m ml.pipelines.production_classify`) —
script-path invocation puts ml/pipelines/ at sys.path[0], where its
operator/ subpackage shadows the stdlib operator module. It lists every open PR,
maps each to the classifier's input dict, runs `classify_pr`, and
writes the feed to `ops/ml/pr-lane-feed.json` (schema `pr-lane-feed/v1`:
generated_at, open_prs, per-lane counts, per-PR rows with lane, gates,
age, size). The workflow commits the feed only when it changed.

## Input mapping (honest, by design)

From the pulls API directly: title, draft, mergeable_state, base ref,
author, changed_files, age from created_at. Gates come from the head
sha's check runs: `repo-gate` = a completed "hygiene + portability
gate" run with conclusion success; `termux-smoke` = same for "agentic
termux smoke". A PR whose checks have not run classifies
NEED_EVIDENCE — that is the classifier's verdict on missing evidence.

Session-era signals with no live source (wholesale, keep_alive,
product, why) are fixed False/"" and documented here rather than
silently implied; the minesweeper number set and title tokens apply
verbatim from ml/pipelines/lanes rules.

## Failure record

If a run fails, the collector writes the feed with an `error` field
(exception type + message, no payload data) and the workflow commits
it under `if: always()` — an error feed on master is more honest than
a stale one, and the committed file is the diagnostic surface the
fleet's API route can actually read (job logs are not API-readable).

## Boundaries

Descriptive only: the run labels nothing, comments nowhere, and gates
nothing. Consumers read the committed feed. If a lane vocabulary or
rule changes, this contract and the recon doc's section B update in
the same PR.
