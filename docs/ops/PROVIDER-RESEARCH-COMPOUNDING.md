# Provider research that compounds into tested changes

Agent **Q** extends the existing model-selection-market package, not a second orchestrator. The first slice turns the two requested upstreams into pinned, testable research data and an automatically proposed refresh. It also supplies a working offline advisory planner. It does **not** autonomously write arbitrary software, activate every free provider, or guarantee continuous improvement.

## What runs

```text
Existing daily OpenRouter catalog workflow completes on master
  → provider-recon-compound.yml validates local contracts
  → Scout fetches fixed upstream GitHub sources at full commit SHAs
  → deterministic research snapshot + Cadence plan become run-attempt artifacts
  → publisher changes exactly one research-data path on a new branch
  → refresh PR opens; repo-gate + termux-smoke are explicitly dispatched
  → established promotion lane evaluates current-head checks and outcome
```

There is no additional cron. A manual dispatch starts one cycle. A PR event runs tests only: it cannot enter the collection/publication jobs. A privileged `workflow_run` job checks out the trusted default branch, never its triggering revision or artifacts. Publication downloads only the normalized artifact generated in the same run. Its token exists only during publication.

The existing `openrouter-free-catalog-sync.yml` remains read-only and never creates PRs. The separately named research workflow owns the narrowly authorized write. It does not change the catalog workflow's contract.

## What is implemented

**MSM-006 — discovery and refresh.** `provider_recon.py` resolves full GitHub commit IDs, downloads fixed raw files at those commits, records file SHA-256 hashes and pinned URLs, and extracts directory metadata and static provider references. It follows no redirects and never queries an imported endpoint. Malformed inputs fail the entire refresh; atomic writes preserve the previous snapshot. Stable JSON has no changing observation timestamp, so an unchanged source snapshot does not generate daily churn. The Actions run ID/attempt supplies observation time and provenance outside the content.

All imported candidates are `THIRD_PARTY_CLAIM`, `runtime_eligible: false`, and `quota_remaining: null`. The importer records upstream license designation as unverified, even where research identifies a likely license. Provider class references are not verified model endpoints. Aggregated directory entries are labeled synthetic aggregate IDs, not individually invocable models. Disappeared entries remain recoverable from previous Git commits and immutable run artifacts.

`publish_recon.py` permits only `data/model-selection-market/provider-recon.json` to change. Content-derived branches make retry publication idempotent. Existing branch contents must match; there is no overwrite, force push, arbitrary patch, approval, or merge API. An unchanged snapshot performs no write. A previously closed proposal whose snapshot is absent from master explicitly blocks publication rather than silently succeeding or reopening a rejected proposal. The publisher explicitly dispatches the two existing gate workflows, because PRs created using `GITHUB_TOKEN` do not trigger ordinary PR workflows ([GitHub event behavior](https://docs.github.com/en/actions/how-tos/writing-workflows/choosing-when-your-workflow-runs/triggering-a-workflow)). Repository policy can still prevent token-created PRs; such a failure is a real blocker, not a successful refresh. No permissions or secrets are silently changed.

**MSM-007 — offline advisory analytics.** `cadence.py` accepts tasks and attributed observations. Verified boolean task outcomes update Beta(1,1) summaries by role/provider/model/task type. Unknown, skipped, and unverified attempts do not become successes. Signed reviewer scores are equal-weight Delphi-style summaries; duplicate votes are rejected, disagreement remains visible, and neither authentication nor consensus is inferred from a `signed` flag. Observed state transitions produce empirical Markov frequencies, not proven predictive performance. Task dependencies and exclusive role lanes produce deterministic start/finish minute offsets, with independent roles running in parallel. The generated Gantt is a plan, not live telemetry.

The checked-in seed has **no observations**. Its durations are planning assumptions, not measured completion-time forecasts. The prior is not an agent ranking, and no fabricated historical observations are supplied. DSPy remains the existing consideration/demo lane; its synthetic outputs must never enter verified performance evidence. This slice does not claim DSPy optimization, causal DOE results, or improvements to actual SWE success rates.

## Roles and handoffs

| Role / moniker | Responsibility | Cannot authorize |
|---|---|---|
| Scout | Discover and attribute candidate data | Provider activation or account entitlement |
| Manager | Review task suitability, policy, and uncertainty | Free status from a directory label alone |
| ChronoMancer | Dependency plan, state transitions, freshness and quota-window semantics | Predictive certainty from sparse history |
| SWE | Implement a scoped item and regression tests | Change the acceptance criteria to make a test pass |
| Reviewer | Independent findings and attributed advisory scores | Treat a declared identity as authenticated |
| Orchestrator / Q | Integrate scoped work, collect evidence, request gates | Bypass required checks, secrets permissions, or production policy |

Use the existing [BIUDL control plane](../architecture/AGENT-TEAM-CONTROL-PLANE.md), [Moneyball contract](HEX-MONEYBALL-INTEGRATION.md), and [model-selection proposal](../proposals/active/model-selection-market/MANIFEST.md). The new advisory report is **not** a `3l0.moneyball.v1` export: use the existing [sanitizer/exporter](../../scripts/hex_moneyball_export.py) for that contract rather than relabeling an incompatible report. Production routing weights remain unchanged; existing observe-cycle and promotion requirements still apply.

## Reproduce on Termux or CI

The runtime uses Python standard library only. Tests additionally use pytest.

```bash
python3 -m scripts.model_selection_market.provider_recon --output /tmp/provider-recon.json
python3 -m scripts.model_selection_market.cadence \
  --input data/model-selection-market/cadence-seed.json --output /tmp/cadence-plan.json
python3 -m pytest -q tests/test_provider_recon.py tests/test_market_cadence.py tests/test_publish_provider_recon.py
python3 -m unittest scripts.model_selection_market.test_msm
python3 scripts/ci/repo_gate.py
python3 scripts/ci/termux_smoke.py
```

Publication uses `GH_TOKEN` from the Actions job, never a committed token. A local planner run is not deployment evidence. The first remote run and subsequent refresh PR are the operational proof points.

## Integrations: enabled is not verified

The session configuration exposed GitHub, Google Workspace, Gmail, OpenAI, Google Gemini, Grok, OpenRouter API, Hugging Face, Hex, Linear, Atlassian, Notion, Airtable, monday.com, Taskade, Todoist, Make, Sentry, LaunchDarkly, Vercel, Cloudflare, Cloudflare Worker Bindings, Neon, Supabase, MotherDuck, Dropbox, GitBook, GitHits, Falconer, Otter.ai, Consensus, Dice, Canva, Lucid, Mermaid Chart, Miro, Mobbin, Webflow, Anchor Browser, Playwright, Tailscale, QuiverAI, Picsart, Higgsfield, Wireflow, Synthesize Bio, and Serena as enabled. This is an inventory, **not** proof that each tool/account is callable, deployed, or appropriate for this task.

| Surface | Actual use or disposition |
|---|---|
| GitHub | Authenticated repository/PR/run inspection; code publication, checks and promotion evidence are recorded in the resulting PR/run |
| Public web / GitHub source fetch | Read the two prioritized repositories and cited provider documentation; public pinned-source discovery exercised without inference |
| Hex | Read-only search for existing `3L0` projects attempted; tool access rejected in this session. No analytics project was modified and no live feed was established |
| Local parallel collaborators | Separate Scout research, implementation and test-review lanes with disjoint file ownership; these are current-task workers, not persistent configured agents |
| Remaining integrations | Not invoked: no task-specific need or verified destination. No unrelated accounts, boards, databases, paid inference, or deployments were changed |

## Research and next validated slices

The [cited provider brief](FREE-LLM-PROVIDER-RECON.md) distinguishes the [CC0 directory](https://github.com/mnfst/awesome-free-llm-apis), [MIT FreeLLMAPI proxy](https://github.com/tashfeenahmed/freellmapi), and [GPL-3.0 gpt4free](https://github.com/xtekky/gpt4free). No upstream code was vendored or executed. Public model counts and quota totals are publisher claims, not our verified account capacity.

Next scoped implementations need their own item and evidence: official provider/account capability admission; source-to-native-provider identity mapping; task-outcome ingestion with real run/attempt IDs and authenticated reviewer provenance; controlled baseline/candidate DOE; quota-aware recovery tests; then a reviewed adapter using the existing runtime contracts. Do not turn research refresh into provider activation, multi-account quota evasion, self-modifying unreviewed executable code, or an unbounded retry loop.
