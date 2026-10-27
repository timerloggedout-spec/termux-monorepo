# Quota Readings — Gap Fill (2026-10-27)

Fills the readings-side gaps in the quota surface (registry:
`ops/quota/registry.json`, 64 records; readings:
`docs/ops/generated/quota-status.json` == `apps/help-wanted-dashboard/data/quota.json`;
text lane: `apps/help-wanted-dashboard/quota.txt`). Companion to the
2026-10-21 web assessment P0-1/P0-1b and the coordination ask on PR #1504
(comment 6335746305). Registry records themselves are unchanged.

## What was wrong (verified firsthand against master, 2026-10-27)

1. **Evidence shape.** The published readings file was the 2026-10-20 seed:
   `generated_at` 2026-10-20T23:05:00Z, 3 readings for 64 registry records,
   and 2 of the 3 rows carried no `observed_at` at all. `quota-evidence.js`
   and `quota_tui.py` both classify a reading with a missing/invalid
   `observed_at` as unknown forever, so "Needs attention" was dead by
   construction regardless of freshness.
2. **Source shape.** `scripts/quota_poll.py` `record()` stamped
   `observed_at = <poll time>` on every record, including services it never
   observed (H1 registry projections). Snapshot generation is not an
   observation; any projection of those records into the readings contract
   would have inherited a fabricated observation time.
3. **Text-lane drift.** `quota.txt` still carried the 2026-10-20 snapshot
   stamp and reported 3 readings.

## Fixes landed in this change

- `scripts/quota_poll.py`: `record()` now sets `observed_at` to the read
  time for live reads only; unobserved records carry `observed_at: null`
  (horizon H1). The public projection (`--public`, uploaded by
  `vercel-quota-probe.yml`) already had this shape and is unchanged.
- Readings file regenerated through the generated-file path: the two
  unobserved seed rows now carry explicit `observed_at: null`; the
  attributed Vercel seed (Hark, 2026-10-20T21:15Z) is retained unchanged as
  evidence of record and now renders `stale`, as designed.
- Two fresh H0/confirmed readings promoted from real reads of the exact
  endpoints the poller polls, executed at 2026-10-27T12:33:41Z:
  `github.api.user_token` (GET /rate_limit, fleet PAT — the record the read
  actually measured) and `github.actions.cache` (GET
  /repos/{repo}/actions/cache/usage).
- `quota.txt` regenerated with the repo's own renderer
  (`scripts/quota_tui.py`) from the regenerated readings + registry.

## Freshness mechanics (standing)

A committed snapshot ages out of the 15-minute H0 window by design; the
gate is fail-closed and was not loosened. The durable loop is: the
dispatch-only probe workflow (`vercel-quota-probe.yml`, secrets
GITHUB_TOKEN / VERCEL_TOKEN / RENDER_API_KEY / NEON_API_KEY /
OPENROUTER_API_KEY) produces the status-only public projection as an
artifact — poller output is never a commit — and confirmed readings are
promoted into the readings file through the generated-file path, as here.
Fully converging the probe projection with the dashboard readings contract
(the #1504 ask) remains open.

**Follow-up (2026-10-27):** that convergence has landed — see
`QUOTA-PROJECTION-CONVERGENCE-2026-10-27.md`. The projection now carries
the contract's evidence fields and a `--from-public` converter produces
the readings snapshot from a probe artifact; no hand-seeded file is
needed.

## Per-service gap table (all 64 registry records)

| Service | Provider | Read path | State after this fill |
|---|---|---|---|
| `partners.credits` | CellCog/Polsia/Manus | no live source | Entitlement only — no live source exists; nothing to fill |
| `aws.account_credits` | aws | no live source | Entitlement only — no live source exists; nothing to fill |
| `aws.dynamodb_storage` | aws | no live source | Entitlement only — no live source exists; nothing to fill |
| `aws.lambda_compute` | aws | no live source | Entitlement only — no live source exists; nothing to fill |
| `aws.lambda_requests` | aws | no live source | Entitlement only — no live source exists; nothing to fill |
| `azure.account_credit` | azure | no live source | Entitlement only — no live source exists; nothing to fill |
| `azure.functions_executions` | azure | no live source | Entitlement only — no live source exists; nothing to fill |
| `cloudflare.d1_rows_read` | cloudflare | no live source | Entitlement only — no live source exists; nothing to fill |
| `cloudflare.d1_rows_written` | cloudflare | no live source | Entitlement only — no live source exists; nothing to fill |
| `cloudflare.d1_storage` | cloudflare | no live source | Entitlement only — no live source exists; nothing to fill |
| `cloudflare.kv_writes` | cloudflare | no live source | Entitlement only — no live source exists; nothing to fill |
| `cloudflare.queues_ops` | cloudflare | no live source | Entitlement only — no live source exists; nothing to fill |
| `cloudflare.r2_storage` | cloudflare | no live source | Entitlement only — no live source exists; nothing to fill |
| `cloudflare.workers_requests` | cloudflare | no live source | Entitlement only — no live source exists; nothing to fill |
| `deno.deploy_requests` | deno | no live source | Entitlement only — no live source exists; nothing to fill |
| `digitalocean.app_platform_static` | digitalocean | no live source | Entitlement only — no live source exists; nothing to fill |
| `digitalocean.trial_credit` | digitalocean | no live source | Entitlement only — no live source exists; nothing to fill |
| `fly.free_tier` | fly | no live source | Entitlement only — no live source exists; nothing to fill |
| `gcp.cloud_functions_invocations` | gcp | no live source | Entitlement only — no live source exists; nothing to fill |
| `gcp.cloud_run_requests` | gcp | no live source | Entitlement only — no live source exists; nothing to fill |
| `gcp.compute_e2micro` | gcp | no live source | Entitlement only — no live source exists; nothing to fill |
| `github.actions.cache` | github | poller reader `gh_cache` (GITHUB_TOKEN) | FILLED — H0 confirmed reading promoted in this change |
| `github.actions.minutes` | github | none needed | Attributed note retained, shape completed with explicit `observed_at: null`; no reading needed (free for public repos) |
| `github.api.github_token` | github | poller reader `gh_rate` (GITHUB_TOKEN) | Still gapped — see read path |
| `github.api.user_token` | github | Hark connector read (GET /rate_limit) | FILLED — H0 confirmed reading promoted in this change |
| `github.artifacts.retention` | github | no live source | Entitlement only — no live source exists; nothing to fill |
| `github.codespaces.core_hours` | github | provider dashboard only (no usage API) | Still gapped — dashboard is the only source |
| `github.codespaces.storage` | github | provider dashboard only (no usage API) | Still gapped — dashboard is the only source |
| `github.copilot.free` | github | no usage API; indirect signals only | Entitlement only — no usage API |
| `gemini.api_free` | google | no usage API; indirect signals only | Entitlement only — no usage API |
| `g4f.vendors` | gpt4free/CLIProxyAPI/Chapito/ai-manus | no usage API; indirect signals only | Entitlement only — no usage API |
| `grafana.cloud_free` | grafana | no live source | Entitlement only — no live source exists; nothing to fill |
| `koyeb.free_instance` | koyeb | no live source | Entitlement only — no live source exists; nothing to fill |
| `neon.compute` | neon | poller reader `neon_reader` (NEON_API_KEY) | Poller-readable in CI only; no credential in the fill sandbox — still gapped here |
| `neon.egress` | neon | no live source | Entitlement only — no live source exists; nothing to fill |
| `neon.realtime` | neon | no live source | Entitlement only — no live source exists; nothing to fill |
| `neon.storage` | neon | poller reader `neon_reader` (NEON_API_KEY) | Poller-readable in CI only; no credential in the fill sandbox — still gapped here |
| `netlify.credits` | netlify | no live source | Entitlement only — no live source exists; nothing to fill |
| `ollama.balance` | ollama | provider-quota-service opt-in (`--observe`, private) | Still gapped — see read path |
| `openrouter.free_models` | openrouter | poller reader `openrouter_reader` (OPENROUTER_API_KEY) | Contract-pinned unknown row (tests pin status unknown, used null, reset null); renders private (model lane) |
| `openrouter.key` | openrouter | provider-quota-service opt-in (`--observe`, private) | Still gapped — see read path |
| `oracle.ampere_gb_hours` | oracle | no live source | Entitlement only — no live source exists; nothing to fill |
| `oracle.ampere_ocpu_hours` | oracle | no live source | Entitlement only — no live source exists; nothing to fill |
| `oracle.block_storage` | oracle | no live source | Entitlement only — no live source exists; nothing to fill |
| `render.bandwidth` | render | poller reader `render_reader` (RENDER_API_KEY) | Poller-readable in CI only; no credential in the fill sandbox — still gapped here |
| `render.instance_hours` | render | provider dashboard only (no usage API) | Still gapped — dashboard is the only source |
| `render.keyvalue_free` | render | no live source | Entitlement only — no live source exists; nothing to fill |
| `render.pipeline_minutes` | render | poller reader `render_reader` (RENDER_API_KEY) | Poller-readable in CI only; no credential in the fill sandbox — still gapped here |
| `render.postgres_free` | render | no live source | Entitlement only — no live source exists; nothing to fill |
| `supabase.db_storage` | supabase | no live source | Entitlement only — no live source exists; nothing to fill |
| `supabase.edge_functions` | supabase | no live source | Entitlement only — no live source exists; nothing to fill |
| `supabase.egress` | supabase | no live source | Entitlement only — no live source exists; nothing to fill |
| `supabase.file_storage` | supabase | no live source | Entitlement only — no live source exists; nothing to fill |
| `supabase.projects` | supabase | no live source | Entitlement only — no live source exists; nothing to fill |
| `turso.databases` | turso | no live source | Entitlement only — no live source exists; nothing to fill |
| `turso.rows_read` | turso | no live source | Entitlement only — no live source exists; nothing to fill |
| `turso.rows_written` | turso | no live source | Entitlement only — no live source exists; nothing to fill |
| `turso.storage` | turso | no live source | Entitlement only — no live source exists; nothing to fill |
| `upstash.qstash_messages` | upstash | no live source | Entitlement only — no live source exists; nothing to fill |
| `upstash.redis_bandwidth` | upstash | no live source | Entitlement only — no live source exists; nothing to fill |
| `upstash.redis_commands` | upstash | no live source | Entitlement only — no live source exists; nothing to fill |
| `upstash.redis_storage` | upstash | no live source | Entitlement only — no live source exists; nothing to fill |
| `vercel.build_time` | vercel | no live source | Entitlement only — no live source exists; nothing to fill |
| `vercel.deployments` | vercel | poller reader `vercel_deploys` (VERCEL_TOKEN) | Attributed seed retained (H1, observed 2026-10-20T21:15Z, renders stale); no fresh read at fill time |

## Notes

- Documented limits are entitlements, not balances. No remaining value was
  invented anywhere in this change: every filled number came from the read
  named in its row's note, or the row is labeled entitlement/unknown.
- Vercel: a firsthand connector read was attempted at fill time;
  `list_deployments` answered twice, then failed repeatedly (exit 1, empty
  body), so no deployment count is claimed. The poller's CI read
  (VERCEL_TOKEN) remains the reliable path; its listing undercounts
  enforcement by >=13 (registry observation, 2026-10-19).
- OpenRouter: the dashboard row is pinned by contract test to
  status unknown / used null / reset null (the endpoint returns no
  per-counter reset timestamp; none is inferred). The poller reads the
  documented free-request counter in CI; the row renders private on the
  web panel because the service is model-lane.
- Mortality rule: this change adds no new free-tier dependency. Services
  with no live source stay entitlement-only rather than being wired to a
  fragile scrape.
