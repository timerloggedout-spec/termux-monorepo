# Quota registry and poller

- Registry: `data/quota/registry.json`. One entry per service: the documented limit with its source URL, the window, the reset and its zone, and the live source. `limit: null` means no fetched page states it; the poller never invents one.
- Poller: `scripts/quota_poll.py` (stdlib). Runs inside the existing `vercel-quota-probe.yml` (workflow_dispatch only, so no second monitor), after a sparse checkout of just these two paths.
- Outputs (artifact `quota-evidence`, 7-day retention, never committed, so no deploy triggers):
  - `evidence.jsonl`: Foresight evidence v2 records (`resource_id`, `item_id`, `lane_id=ops-quota`, `canonical_source`, `horizon`, `evidence_status`, `evidence_hash`).
  - `hindsight-retain.jsonl`: `retain(bank_id, content)` payloads for bank `deepagent::termux-monorepo`.
  - `routing-weights.json`: the per-provider pace-to-limit multiplier consumed by `ml/pipelines/moneyball/quota_weights.py` (`adjusted_score = 3L0 score x multiplier`).
- Planned use: `limit x safety x elapsed fraction of the window` (safety 0.95, or 0.90 for Vercel deploys because the probe undercounts). The weight is above 1 when under-spent (use it), 1 when on plan, and 0 at the margin or when exhausted (explicit skip).
- Live readers: GitHub rate limit and cache, Vercel deploys in the last 24h, Render bandwidth plus a pipeline-exhaustion check from the build log, OpenRouter `free_model_daily_requests`, and Neon compute. A reader whose secret is absent reports `no_credential`. Render minutes and instance hours aren't exposed by the Render API (dashboard Billing only).
- Secrets are read from the environment only. Nothing prints or stores their values.
