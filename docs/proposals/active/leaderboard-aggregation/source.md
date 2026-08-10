# Source — leaderboard-aggregation

This is the source blueprint that was pasted into PR #123
(`@Coderabbitai @google-labs-jules @jules implement these files and
structures into the protocols`) and that this proposal was registered
against. It is recorded here verbatim, for provenance, as background only.
**It is not the accepted scope.** See `MANIFEST.md` → "Scope boundaries" for
what phase 1 actually implements; several elements below (browser scraping,
inferred/undocumented APIs, committed daily Parquet history, auto-commit
third-party actions, using public leaderboard data as a routing input) are
explicitly excluded.

---

> Here is your complete automation blueprint for an AI/ML/LLM leaderboard
> aggregator with a GitHub Actions workflow, covering all requested phases
> (1–3). Step 4 (mapping free tiers/exploits) will be integrated later —
> you'll provide those PRs after this foundation is running.
>
> **1. Aggregate All Endpoints into a Unified Time-Series Dataset** — a table
> of ~20 sources (Chatbot Arena/LMSYS, Open LLM Leaderboard, Artificial
> Analysis, LiveBench, Aider Polyglot, Hallucination Leaderboard, Agent
> Leaderboard, MMLU/MMLU-Pro, GPQA, MATH/AIME, ARC, BIG-Bench, SWE-Bench,
> HumanEval, LiveCodeBench, AA Coding Index, MMBench, text-to-image/video
> spaces, MTEB, TTS Arena, GLUE/SuperGLUE, HELM, Reward Bench), split into
> API-accessible and web-scraped, with a proposed `aggregator/sources.py`
> unified `fetch(source)` using `requests` + `beautifulsoup4`.
>
> **2. Import schema (time-series dataset)** — raw observations stored as
> Parquet under `data/raw/` and `data/processed/` with columns `model`,
> `source`, `benchmark`, `metric`, `value`, `timestamp`, `extra`; plus
> processed tables `model_metadata`, `benchmark_definitions`,
> `rankings_daily`, using DuckDB or pandas+Parquet.
>
> **3. Optimize rankings with weights (start at zero)** — all
> `benchmark_weights` in `weights.yaml` start at `0.0`; composite score is a
> weighted average of normalized [0,1] scores, ranked descending, with a
> plan to raise Code & Dev benchmark weights later.
>
> **GitHub Actions workflow** — `.github/workflows/update_leaderboard.yml`
> on a daily `schedule` and on `push` to `main` touching `aggregator/**` or
> `weights.yaml`; jobs: fetch & normalize → compute rankings → generate
> tables → commit & push via `peaceiris/actions-gh-pages` or
> `stefanzweifel/git-auto-commit-action`.
>
> **Output** — a Markdown matrix table (model × benchmark × avg rank) and an
> optional trend plot via matplotlib.
>
> **Proposed file structure:**
> ```text
> .github/workflows/update_leaderboard.yml
> aggregator/
> ├── __init__.py
> ├── sources.py          # fetch functions
> ├── normalize.py        # mapping to schema
> ├── fetch_all.py        # main orchestration
> ├── compute_rankings.py
> ├── generate_tables.py
> ├── utils.py             # caching, logging
> ├── weights.yaml         # initial weights (all zero)
> data/
> ├── raw/                 # parquet files per date
> ├── processed/           # latest rankings, matrix
> docs/
> ├── leaderboard.md       # generated
> README.md                # includes generated table (updated via action)
> requirements.txt
> ```
>
> **Next steps (for you):** fork/copy the structure, `pip install -r
> requirements.txt`, set up `GITHUB_TOKEN` for auto-commit, then share the
> "step 4" (free-tier/exploit mapping) PRs once steps 1–3 work.

---

## Why this differs from the accepted phase-1 scope

| Blueprint element | Phase-1 disposition |
|---|---|
| Web scraping (Artificial Analysis, Aider, Hallucination/Agent leaderboards, MMLU/GPQA/MATH/ARC/BIG-Bench/SWE-Bench/HumanEval/LiveCodeBench/MMBench/TTS Arena/GLUE/Reward Bench spaces) | Excluded — phase 1 supports documented machine-readable sources only |
| LiveBench "inferred" REST API, HELM "inferred" API | Excluded/limited — only published project + dataset artifacts (pinned revision) and a selected small HELM release summary |
| Daily committed Parquet under `data/raw/`, `data/processed/` | Excluded — Parquet, if produced, is a retention-bounded CI artifact, never committed |
| `peaceiris/actions-gh-pages` / `stefanzweifel/git-auto-commit-action` | Excluded — workflow must use native Git commands for the commit step |
| Ranking uses a synthetic average when all weights are zero | Excluded — zero positive weight ⇒ `composite_score`/`composite_rank: null` + coverage metadata |
| Aggregated data feeds/optimizes routing ("step 4: mapping free tiers/exploits") | Excluded from this proposal's authority — public leaderboard values are reporting features only and never become routing labels; `docs/schemas/model-success-matrix.yaml` (internal ELO++/3L0) remains the sole routing input for `scripts/model_router.py` |