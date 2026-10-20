# Quota registry and poller

Plan every free allowance so it gets fully used without going over. Everything here is additive and read-only toward vendors.

- **Registry:** `ops/quota/registry.json` has one entry per service the repo uses: GitHub Actions, cache, API and Copilot; Vercel; Render; Neon; OpenRouter; Gemini; the g4f, CLIProxyAPI and Chapito vendors; Grafana; the Platform201 data candidates; and the partner credits. Each entry carries the documented limit and its **source URL**, the window, the reset and its zone, the live endpoint, and a `planned_use` safety factor. `limit: null` means no fetched page states a number, and the poller never invents one (FREE-QUOTA-WINDOWS.md).
- **Poller:** `scripts/quota_poll.py`, stdlib only. It reads a live source only when that source's credential env var is set, and never prints a secret.
- **Runner:** the existing `vercel-quota-probe.yml` (workflow_dispatch only) does a sparse checkout of 3 paths and uploads the artifact `quota-readings` with 7-day retention. Nothing is committed, so polling never triggers Vercel or Render builds. The scheduled one-shots dispatch it; there is no cron and no second monitor.
- **Outputs:**
  - `quota-records.jsonl`: Foresight Evidence Spine v2 records (`resource_id`, `item_id`, `lane_id`, `canonical_source == source.url`, horizon H0 for a live reading and H1 for a documented one, `evidence_status`, `evidence_hash`).
  - `hindsight-retain.jsonl`: `retain(bank_id="deepagent::termux-monorepo", content)` payloads.
  - `routing-weights.json` (`3l0.quota-weights.v1`): a per-provider multiplier.
- **3L0 / MoneyBall:** `ml/pipelines/moneyball/quota_weights.quota_multiplier(provider)` multiplies the 3L0/ELO × role score. The multiplier is the remaining-budget fraction (after safety) divided by the remaining-time fraction, capped at 2. It's 0 when a quota is exhausted, and 1.0 when there's no evidence or no file, so routing stays unchanged by default.
- **Secrets the poller can use (names only):** VERCEL_TOKEN and VERCEL_ORG_ID (set), RENDER_API_KEY, NEON_API_KEY and OPENROUTER_API_KEY (each is optional and skipped when absent).

Corrections to Render figures, 2026-10-19: 500 Starter pipeline minutes on Hobby comes from https://render.com/docs/build-pipeline. 750 free instance hours, the 15-minute spin-down, builds disabled with artifacts kept, and free Postgres/Key Value come from https://render.com/docs/free. 5 GB of bandwidth on Hobby comes from https://render.com/pricing. The "$5/mo build credit needs a card" claim was unsourced and has been removed. The Render API exposes no included-usage endpoint (that's on the dashboard billing page only), so pipeline minutes are estimated from the deploys API's wall-clock time.
