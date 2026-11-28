# ML PR lane classify — production run of the vocab-v2 PR classifier

Contract for `.github/workflows/ml-pr-lane-classify.yml` and
`ml/pipelines/production_classify.py`.

## What runs

Daily 05:37 UTC + `workflow_dispatch`. The collector runs as a module from the repo root:

```bash
python3 -m ml.pipelines.production_classify
```

It lists open PRs, reads each head SHA and check runs, fetches the paginated changed-file list, applies the shared Termux surface predicate, runs `classify_pr`, and writes `ops/ml/pr-lane-feed.json` (`pr-lane-feed/v1`). Each PR row includes lane, gates, `termux_smoke_required`, age, size, base ref, and mergeable state. The workflow commits the feed when its content changes. Successful runs append one counts-only line to `ops/ml/pr-lane-series.jsonl`.

## Input mapping

From the pulls API: title, draft, mergeable state, base ref, author, changed-file count, and age from `created_at`.

From the paginated `pulls/{number}/files` endpoint: changed paths. The shared predicate in `scripts/ci/gate_admission.py` derives `termux_smoke_required`.

- `repo-gate`: completed `hygiene + portability gate` check with conclusion `success`.
- `termux-smoke`: completed `agentic termux smoke` check with conclusion `success`, required only when `termux_smoke_required=true`.
- A complete changed-path list outside the Termux surface allows `CANDIDATE` with repo-gate evidence.
- A Termux-surface change requires both repo-gate and Termux smoke evidence.
- Missing or incomplete changed-path evidence sets `termux_smoke_required=true`, preserving the runtime check.

Session-era signals (wholesale, keep_alive, product, why) retain documented fixed values until live sources are available. The minesweeper number set and title tokens apply from `ml/pipelines/lanes` rules.

## Failure record

A failed collector run leaves the last good feed in place; staleness remains visible in `generated_at`. The run surfaces the failure through a `::error::` stage annotation with exception type and message. The counts series appends only after a successful run.

## Boundaries

The classifier is descriptive. It labels PR lanes and writes the committed feed. Merge, comment, deployment, and provider actions remain with their owning workflows. If a lane vocabulary or rule changes, update this contract and the reconciliation document in the same PR.
