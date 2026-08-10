# ITEMS — leaderboard-protocol

| ID | Work | Priority | Owner | Status | Evidence |
|----|------|----------|-------|--------|----------|
| LBA-01 | Register proposal + source registry (12 benchmarks classified eligible/deferred/conditional) | P2 | claude | done | ./SOURCES.md |
| LBA-02 | Ranking policy: all `benchmark_weights` at `0.0`, coverage-only output, `composite_score`/`composite_rank` null when no positive weight | P2 | claude | done | ./MANIFEST.md#ranking-policy |
| LBA-03 | Standard-library JSONL collector: Hugging Face dataset discovery (`GET /api/datasets?filter=benchmark:official`) + per-dataset leaderboard retrieval (`GET /api/datasets/{dataset_id}/leaderboard`) for `HLE` and `SWE-bench Verified` only | P2 | | todo — blocked on proposal `accepted` | none yet |
| LBA-04 | Per-source diagnostics: `429`/`Retry-After` handling, per-source error isolation, explicit metric direction + model alias mappings, exact-observation dedup, fixture-only tests, no browser scraping, no raw daily data commits | P2 | | todo — blocked on proposal `accepted` | none yet |
| LBA-05 | Confirm zero diff footprint on `scripts/model_router.py` and `docs/schemas/model-success-matrix.yaml` (reporting-only boundary held) | P2 | claude | done | this PR's diff touches only `docs/proposals/` |