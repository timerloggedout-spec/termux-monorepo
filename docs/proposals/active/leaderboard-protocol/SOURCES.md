# Source registry — leaderboard-protocol

Classification of every benchmark requested on PR #123, corrected against
published source contracts. `eligible` sources may be implemented once this
proposal is `accepted` (see `LBA-03`/`LBA-04`); `deferred` and `conditional`
sources are recorded here for traceability only and must not be
implemented until they clear their listed blocker.

| Benchmark | Classification | Collection contract | Notes |
|---|---|---|---|
| MMLU | Deferred | Add only when an official benchmark dataset exposes MMLU through the Hugging Face dataset-leaderboard API. | Do not use the undocumented `/api/leaderboards?benchmark=open-llm-leaderboard` endpoint. |
| MMLU-Pro | Deferred | Prefer a documented official dataset leaderboard or a pinned project artifact. | Do not scrape `huggingface.co/spaces/TIGER-Lab/MMLU-Pro`. |
| GPQA | Deferred | Prefer a documented official dataset leaderboard or a pinned project artifact. | Do not scrape `huggingface.co/spaces/Idavidrein/gpqa`. |
| HLE (Humanity's Last Exam) | **Eligible** | `GET /api/datasets/cais/hle/leaderboard` | Hugging Face dataset-leaderboard API. Do not use the proposed `hle_leaderboard.json` static download. |
| MATH | Deferred | Add only through an official dataset-leaderboard contract. | Do not use the undocumented broad leaderboard endpoint. |
| AIME | Deferred | No approved contract yet. | Do not use the inferred `huggingface.co/spaces/open-llm-leaderboard/aime` Space endpoint. |
| ARC | Deferred | Add a documented dataset export or official repository artifact first. | Do not scrape `huggingface.co/spaces/leaderboards/arc`. |
| BIG-Bench | Deferred | Verify `leaderboard_table.json` exists in the official `google/BIG-bench` repository and pin a commit SHA before enabling. | Static JSON download only after the pin is verified. |
| SWE-bench Verified | **Eligible** | `GET /api/datasets/SWE-bench/SWE-bench_Verified/leaderboard` | Hugging Face documents this dataset-leaderboard endpoint. Do not scrape `swe-bench.github.io` or `leaderboard.berkeley.edu`. |
| HumanEval | Deferred | Verify the Papers with Code API contract, licensing, and current endpoint support before enabling. | No PapersWithCode API is approved yet. |
| LiveCodeBench | Deferred | Add a pinned commit and a parser contract once repository leaderboard JSON is confirmed. | Do not scrape `livecodebench.github.io/leaderboard.html`. |
| AA Coding Index | Conditional | Use the documented Artificial Analysis Data API (`https://artificialanalysis.ai/data-api/docs`), not HTML scraping. | Requires `AA_API_KEY`, required attribution, tier validation, `429`/rate-limit-header handling, and confirmed redistribution rights. Published free-tier limit: 100 requests/day (subject to change — verify against current docs before enabling). |

## Sources

- [Hugging Face leaderboard data guide](https://huggingface.co/docs/hub/en/leaderboard-data-guide)
- [Artificial Analysis Data API](https://artificialanalysis.ai/data-api/docs)

## Deduplication / metric-direction / alias contract (for LBA-03/LBA-04)

Once accepted, the collector implementation must:

- record explicit metric direction per benchmark (higher-is-better vs lower-is-better);
- record explicit model alias mappings (a model id on one source may not match another);
- de-duplicate exact-observation rows (same source + dataset + model + timestamp);
- isolate errors per source (one source failing must not abort the run);
- honor `429` responses and `Retry-After` headers as diagnostics, not crashes;
- never log `AA_API_KEY` or any other credential in observation/diagnostic output.