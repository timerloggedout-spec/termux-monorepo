# IIE Engineering Status — WP1 through WP9

**Updated:** 2026-11-15  
**Branch:** `feat/incremental-intelligence-rfp-2026-11`  
**Review:** [Draft PR #5455](https://github.com/timerloggedout-spec/termux-monorepo/pull/5455)

This status records what is implemented, what is merely instrumented, and what remains gated. A code commit is not a passing test, and a CI workflow definition is not a CI result.

## Work package status

| WP | State | Evidence / next action |
|---|---|---|
| WP0 — architecture reconciliation | **Implemented (docs)** | RFP maps CEEL, ATES, L1/L2 graph, Rust accelerator, historical backfill, queue v2 and admission owner. |
| WP1 — baseline instrumentation | **Instrumented; baseline pending** | Graph build receipt now records collection/compile/publish/wall/CPU/peak-RSS metrics plus SHA-256 fingerprints of canonical nodes and edges. `scripts/ops/iie_benchmark.py` compares two receipts and rejects exact artifact, count, source and coverage parity drift. Run repeated same-SHA baseline/treatment cohorts before claims. |
| WP2 — incremental ingestion | **Existing path confirmed; enhancement gated** | Builder already uses checkpoint `since`, retained history, bounded page continuation and checkpoint eligibility. This slice does not add a new event broker or persistent raw-response cache. Next: baseline actual request counts, then optimize only demonstrated duplicate/unchanged reads. |
| WP3 — queue dependency admission | **Targeted hardening implemented; CI pending** | Existing queue v2 evaluator retained. ISO-8601 offset/fractional timestamps now parse; future-dated feeds fail freshness; malformed active-run timestamps remain conservatively blocking. New regression tests added. |
| WP4 — semantic retrieval | **Research design only** | No approved, sanitized, frozen embedding corpus or measured recall labels was available in this implementation pass. Next: build evaluation corpus and exact lexical/vector baselines before FAISS ANN. |
| WP5 — online clustering | **Research design only** | e-means/MiniBatchKMeans comparison not executed. Requires the same frozen vectors and labels as WP4; no production graph writes. |
| WP6 — analytical projections | **Deferred** | No evidence yet that JSONL/SQLite scanning is the limiting factor. DuckDB/Parquet remain derived-projection candidates only. |
| WP7 — observability | **Initial instrumentation implemented** | Build summaries carry phase timings, process CPU and best-effort peak RSS. Full ATES correlation and queue histograms remain to be added through schema owners after baseline review. |
| WP8 — Termux portability | **Not yet validated on device** | Runtime path remains stdlib/SQLite/JSONL-friendly; no new native dependencies. ARM64/Termux proof and offline interruption tests still required. |
| WP9 — promotion | **Draft PR open; no promotion** | PR #5455 is open as draft. CI status has not yet been observed. No merge, default-branch update or production routing change. |

## Implemented engineering details

### Queue admission
- ISO-8601 parsing uses `datetime.fromisoformat`, normalizes offsets to UTC, and supports fractional seconds.
- Malformed timestamps retain conservative behavior: an active run with unknown age is not silently excluded as ancient.
- A collector feed with a future `generated_at` is not accepted as fresh.
- Future clock skew is named explicitly in stale-feed diagnostics.

### Graph build receipts
The canonical graph and temporal evidence formats are unchanged. `build-summary.json` now includes:
- `collection_seconds`
- `compile_seconds`
- `publish_seconds`
- `wall_seconds`
- `process_cpu_seconds`
- `peak_rss_bytes` (best effort; null if unavailable)\n- `nodes_sha256` and `edges_sha256` (SHA-256 of the published canonical JSONL bytes)

The final summary is written through a temporary file and atomic replacement.

### Benchmark comparator
`scripts/ops/iie_benchmark.py` compares baseline and treatment receipts. It first checks repository, ref, source SHA, graph counts and coverage. Any mismatch yields `PARITY_FAILED`; efficiency ratios are reported only as descriptive metrics. A zero/missing denominator produces an unavailable ratio, not an invented infinite speedup.

Example:

```bash
# SEED must be a frozen copy of a valid prior corpus, including manifest,
# nodes.jsonl, edges.jsonl, temporal-current.json and checkpoint.json.
cp -a "$IIE_SEED" /tmp/iie-baseline
cp -a "$IIE_SEED" /tmp/iie-treatment

python3 archwiz/context_relationships/build_index.py \
  --owner "$GITHUB_REPOSITORY_OWNER" --repo "$GITHUB_REPOSITORY_NAME" \
  --ref "$GITHUB_REF_NAME" --full-refresh --output /tmp/iie-baseline

python3 archwiz/context_relationships/build_index.py \
  --owner "$GITHUB_REPOSITORY_OWNER" --repo "$GITHUB_REPOSITORY_NAME" \
  --ref "$GITHUB_REF_NAME" --output /tmp/iie-treatment

python3 scripts/ops/iie_benchmark.py \
  --baseline /tmp/iie-baseline/build-summary.json \
  --treatment /tmp/iie-treatment/build-summary.json \
  --output /tmp/iie-comparison.json
```

For a valid controlled experiment, both runs must start from byte-identical frozen seed directories, use the same commit/source SHA, config, limits and source snapshot, and run in isolated output directories. The seed must include a valid prior checkpoint; otherwise the treatment bootstraps and is not an incremental treatment. Repeat the cohort and report medians and spread. Do not run both treatments against a moving live source and call the result a controlled benchmark.

## Validation added to CI

The context relationship validation workflow now includes a dedicated job for:
- `scripts/ops/test_swarm_admission.py`
- `tests/test_iie_benchmark.py`
- `tests/test_context_relationship_build_index.py`

The existing graph-validation job remains in place. Workflow execution results must be checked on PR #5455 before the slice is called validated.

## Explicitly not done

- No FAISS/e-means package or model dependency was installed.
- No vector index, embedding corpus or semantic candidate writer was added.
- No new broker, scheduler, database, cache service or queue was introduced.
- No full refresh was run against production GitHub data from this session.
- No Termux/ARM64 device test was run.
- No PR merge or production promotion occurred.

## Promotion gate

Do not promote until:
1. CI checks pass on the exact head SHA.
2. Queue and graph tests pass.
3. Full-refresh/incremental parity is demonstrated on a frozen cohort.
4. Repeated benchmark runs show an improvement with no coverage loss.
5. Termux target-device tests pass for the core path.
6. Semantic research is evaluated separately and candidate-only.
7. Existing proposal and operator gates approve any production behavior change.
