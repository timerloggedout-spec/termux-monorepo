---
id: leaderboard-protocol
title: "Bounded public leaderboard protocol (reporting-only, zero-weight)"
author: devin
posted_at: 2026-08-10
status: posted
priority: P2
reviewers:
  - id: devin
    role: author
    status: posted
  - id: claude
    role: registrar
    status: posted
related_prs: [123]
gates_required: [repo-gate]
---

# MANIFEST — leaderboard-protocol

## Summary

Registers a bounded, reporting-only public-benchmark leaderboard protocol in
response to the PR #123 review thread. Replaces the originally requested
undocumented/inferred endpoints (HF `leaderboards` API, Space scraping,
`hle_leaderboard.json`, PapersWithCode, raw HTML scraping) with the documented
Hugging Face dataset-leaderboard API contract, defers every benchmark without
a documented+pinned export, and keeps every `benchmark_weights` entry at
`0.0`. This proposal makes **no changes** to `scripts/model_router.py` or
`docs/schemas/model-success-matrix.yaml` — public leaderboard data is a
reporting feature only, never routing authority (see
`docs/schemas/llm-leaderboard-matrix.yaml` for the existing "features, not
authority" policy this proposal extends to benchmark scores).

## Approved collection contracts

Documented Hugging Face endpoints only:

```text
GET https://huggingface.co/api/datasets?filter=benchmark:official
GET https://huggingface.co/api/datasets/{dataset_id}/leaderboard
```

`HLE` uses `GET /api/datasets/cais/hle/leaderboard` — not the previously
proposed `hle_leaderboard.json` static download.

Full per-benchmark classification (eligible / deferred / conditional) lives
in `./SOURCES.md`.

## Ranking policy

All benchmark weights stay at `0.0` until a benchmark is promoted through its
own accepted item. No unweighted baseline is computed when the positive-weight
total is zero.

```yaml
benchmark_weights:
  mmlu: 0.0
  mmlu-pro: 0.0
  gpqa: 0.0
  hle: 0.0
  math: 0.0
  aime: 0.0
  arc: 0.0
  big-bench: 0.0
  swe-bench: 0.0
  humaneval: 0.0
  livecodebench: 0.0
  aa-coding-index: 0.0

ranking:
  normalization: min-max
  aggregation: weighted-mean
  zero_positive_weight_behavior: coverage-only
```

When `zero_positive_weight_behavior: coverage-only` applies, the collector
publishes `composite_score: null` and `composite_rank: null`, plus coverage
and per-source diagnostics only.

## Non-goals / boundaries

- No changes to `scripts/model_router.py` or `docs/schemas/model-success-matrix.yaml`.
- No browser scraping of Hugging Face Spaces, PapersWithCode, or leaderboard HTML.
- No inferred/undocumented endpoints (e.g. `/api/leaderboards?benchmark=...`).
- No raw daily data commits — JSONL observations + diagnostics only, once LBA-03/LBA-04 are accepted.
- DeepSeek "highest priority" routing and any roundtable MoE method are **out of scope** here.
  Public benchmark results from this protocol must never become routing labels or routing
  authority. That work is tracked as its own routing-policy item — see
  `../rate-limit-rotation/ITEMS.md` (`RL-18`) and
  `../rate-limit-rotation/DEEPSEEK-MOE-POLICY.md`.

## Review log

### 2026-08-10 — devin (via PR #123 review thread)

- Disposition: **commented** (source contracts corrected, weights held at zero)
- Notes: Rejected the originally requested HF `leaderboards` API, Space scraping,
  static `hle_leaderboard.json`, PapersWithCode, and raw HTML scraping endpoints.
  Approved only the documented HF dataset-leaderboard API for `HLE` and
  `SWE-bench Verified`; everything else deferred or conditional pending a
  documented+pinned export contract.

### 2026-08-10 — claude (registrar)

- Disposition: **posted** (registered, not yet accepted)
- Notes: Registered proposal + itemized `LBA-01`..`LBA-05`; source registry
  and zero-weight ranking contract recorded. `LBA-03`/`LBA-04` (aggregator
  package + fixture-only tests) stay `todo` until this proposal reaches
  `accepted` — acceptance before implementation, per the finalized plan.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [ ] At least one non-author review recorded
- [ ] Status → accepted before execution merges
- [ ] PRs cite `Implements: LBA-xx`
- [ ] Gates green on merge
- [ ] Closed + moved to `closed/` when terminal

## Links

- ITEMS: ./ITEMS.md
- Source registry: ./SOURCES.md
- Routing-policy split-out: ../rate-limit-rotation/ITEMS.md (RL-18), ../rate-limit-rotation/DEEPSEEK-MOE-POLICY.md