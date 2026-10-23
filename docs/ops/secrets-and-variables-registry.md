# Secrets & Variables Registry — Operational Reference

Status: source of truth for repository configuration names. Ledger issue: #184.
Scope: `timerloggedout-spec/termux-monorepo`. Derived from static inventory of
`.github/workflows/**` (86 files reference `secrets.*` / `vars.*`).

## 1. Classes

- Secret (`gh secret set`): credentials. Never in variables, never in code.
- Variable (`gh variable set`): non-secret configuration and identifiers.
- App credentials (`APP_CLIENT_ID` + `APP_PRIVATE_KEY` style pairs): GitHub App
  JWT pairs, always secrets, always created together.

## 2. Existing names (inventory-derived, not exhaustive of values)

Secrets in current use include: AION_API_KEY, APP_CLIENT_ID, APP_PRIVATE_KEY,
ARCHWIZ_GITHUB_TOKEN, CEREBRAS_API_KEY, CODESPACE_CREATE_TOKEN,
CROSS_REPO_PAT, DEEPSEEK_AGENT_TOKEN, DEEPSEEK_AGENT_URL, DEEPSEEK_API_KEY,
DEEPSEEK_AUTH_TOKEN, DEEPSEEK_TOKEN, DEEPSEEK_TOKEN_ACCOUNT_1,
DEEPSEEK_TOKEN_PRIMARY, DEEPWIKI_LLM_API_KEY,
DEVICE_QUEUE_PRODUCER_TOKEN_ACTIONS, DEVICE_QUEUE_URL, FELO_AI_API,
GAMUT_JUDGE_API_KEY, GEMINI_API_KEY, GH_ACTIONS, GH_AW_GITHUB_MCP_SERVER_TOKEN,
GH_AW_GITHUB_TOKEN, GITLAB_CICD_W_ORG_VIEW, GITLAB_TOKEN, GOOGLE_API_KEY,
GOVERNED_AUTOMERGE_APP_CLIENT_ID, GOVERNED_AUTOMERGE_APP_PRIVATE_KEY,
GRAFANA_API_KEY, GRAFANA_SERVICE_ACCOUNT_TOKEN, GRAFANA_TOKEN, GRAFANA_URL,
HUGGINGFACE_TOKEN, JULES_API_KEY, KOYEB_API_TOKEN,
LANE_EVENTS_DATABASE_URL, LINEAR_API_KEY, LLM7_API_TOKEN, MANUS_SSH_HOST,
MANUS_SSH_KEY, MANUS_SSH_PORT, N8N_SHE_WEBHOOK_URL, NEON_API_KEY,
NEXUSCLI_TOKEN, NVIDIA_API_KEY, NVIDIA_NIM_API_KEY, OMNIROUTE_API_KEY,
OMNI_API_KEY, OPENROUTER_API_KEY, OPERATOR_GITHUB_TOKEN,
OPERATOR_GITLAB_TOKEN, OPERATOR_MATRIX_PROJECT_URL, OPERATOR_TOKEN,
PEER_STATE_PUBLISHER_LOGINS, RECON_INTEL_GITLAB_READ_TOKEN, RENDER_API_KEY,
REPOSITORY_OBSERVATORY_TOKEN, SWE_EVALUATION_API_KEY,
TERMUX_MCP_KNOWN_HOSTS, TERMUX_MCP_SSH_PRIVATE_KEY, TRIBUTE_VERCEL_PROJECTS,
VANTAGE_PAT_GH_SECRETS, VERCEL_ORG_ID, VERCEL_TOKEN. GITHUB_TOKEN is the built-in per-run token.

Variables in current use include: AUTOMATION_MARKER_PUBLISHER_LOGINS,
CELLCOG_API_KEY, CELLCOG_CHAT_TIER, CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN,
CURRENT_EXPERIMENT_ID, DEEPWIKI_LLM_API_BASE_URL, DEEPWIKI_MODEL,
GEMINI_HEALTH_MODEL, GH_AW_MODEL_AGENT_COPILOT, GH_AW_RUNTIME_FEATURES,
GOVERNED_REVIEW_TEAM, JULES_AUTO_INVOKE, OLLAMA_API_KEY,
OPENROUTER_HEALTH_MODEL, OPERATOR_COMMAND_ACTIONS, OPERATOR_EXECUTOR_LOGINS,
PEER_ENFORCE_PROVIDER_COMPLETION, PEER_REQUIRED_PROVIDERS,
RECON_SWEEP_MAX_TARGETS, RECON_SWEEP_WINDOW_HOURS,
SWE_REFERENCE_EVALUATION_ENABLED, plus QUOTA_EVAL_WATERMARK (created by the
quota dispatch tree).


## 3. New names required by the quota program

| Name | Class | Value / source | Consumer |
|---|---|---|---|
| SUPABASE_URL | variable | `https://rtcthvahpdrykjlghnhe.supabase.co` (project termux-monorepo-lane-state, us-west-1, ref rtcthvahpdrykjlghnhe) | quota-dispatch-tree: verdict persistence to dispatch_verdicts |
| SUPABASE_SERVICE_ROLE_KEY | secret | Supabase dashboard -> Project Settings -> API -> service_role key | quota-dispatch-tree: service-role writes (RLS enabled; no anon policies) |
| QUOTA_EVAL_WATERMARK | variable | created/advanced automatically | quota-dispatch-tree: Node E watermark |
| BIGQUERY_PROJECT_ID | variable | TBD when BigQuery project is chosen | future quota telemetry lane |
| GCP_BIGQUERY_SA_KEY | secret | GCP service-account JSON key | future quota telemetry lane |
| BUILDKITE_ORG_SLUG | variable | `founders-are-found-to-implement` | future cross-platform dispatch lane |
| BUILDKITE_PIPELINE_SLUG | variable | `termux-monorepo` | future cross-platform dispatch lane |
| BUILDKITE_API_TOKEN | secret | Buildkite API token (read/write builds) | future cross-platform dispatch lane |
| VANTAGE_PAT_GH_SECRETS | secret | Vantage access token, read scope (console.vantage.sh -> Settings -> API Access Tokens); provisioned 2026-10-23 via repo Settings -> Secrets and variables -> Actions | vantage-cost-report lane: cost telemetry probe (woken 2x/day by dispatcher Node H) |

Provision with the CLI:

```
gh variable set SUPABASE_URL        --body 'https://rtcthvahpdrykjlghnhe.supabase.co' -R timerloggedout-spec/termux-monorepo
gh secret   set SUPABASE_SERVICE_ROLE_KEY -R timerloggedout-spec/termux-monorepo   # paste service_role key
gh variable set BUILDKITE_ORG_SLUG  --body 'founders-are-found-to-implement' -R timerloggedout-spec/termux-monorepo
gh variable set BUILDKITE_PIPELINE_SLUG --body 'termux-monorepo' -R timerloggedout-spec/termux-monorepo
```

Variables can also be upserted without the CLI via the
`operator-variable-provision` workflow (workflow_dispatch; allowlisted,
non-secret names only). Secret values can only be set via `gh secret set` or
repo Settings -> Secrets and variables -> Actions.

## 4. Naming conventions (binding)

- UPPER_SNAKE_CASE. System prefix first (SUPABASE_, VERCEL_, GITLAB_,
  BUILDKITE_, BIGQUERY_/GCP_), then role (URL, API_TOKEN, SERVICE_ROLE_KEY,
  ORG_ID). Read-only credentials end `_READ_TOKEN` (see
  RECON_INTEL_GITLAB_READ_TOKEN); write credentials end `_TOKEN` or `_API_KEY`.
- URLs and slugs are variables, never secrets. Keys are secrets, never
  variables.
- One name, one meaning: no alias families (DEEPSEEK_TOKEN vs
  DEEPSEEK_TOKEN_PRIMARY already exist — new work must not add more aliases;
  consolidate in #184 instead).
- Optional integrations must degrade: consumers read
  `secrets.X || ''` / `vars.Y || ''` and skip cleanly when absent
  (pattern proven in quota-dispatch-tree Supabase persistence).

## 5. Extensions to additional systems

- Supabase: live (lane-state schema). Wire-up needs SUPABASE_URL variable +
  SUPABASE_SERVICE_ROLE_KEY secret; persistence is dormant until both exist.
- BigQuery: define BIGQUERY_PROJECT_ID variable + GCP_BIGQUERY_SA_KEY secret
  when the telemetry dataset from the RFP (#1576) is chosen.
- Buildkite: cross-platform dispatch per RFP; needs the three BUILDKITE_*
  names above.
- Vantage: GitHub-side lane delivered — vantage-cost-report.yml
  (workflow_dispatch-only; woken 2x/day by dispatcher Node H, hour % 12 == 1).
  VANTAGE_PAT_GH_SECRETS was provisioned 2026-10-23 via repo Settings -> Secrets
  and variables -> Actions, and the lane reads it as its Bearer token; it
  degrades cleanly if the secret is removed. MCP connector token invalid —
  re-provision the connector before MCP-side provisioning (workspaces,
  dashboards, budgets, alerts).


## 6. Snapshot validation (2026-10-23, Settings -> Secrets and variables -> Actions)

Validated against the repository settings snapshot (issue #184) and the
public-code scan:

- Security model confirmed: secrets are encrypted by GitHub, readable only to
  workflows run by collaborators, and never passed to workflows triggered by
  pull requests from forks. Variables are plain text by design — non-secret
  configuration only. Use (read) availability in Actions runs is therefore the
  default for every listed name; fork PRs get none of them.
- Secrets present in settings but not in the earlier code-scan inventory
  (reserved or consumed by non-workflow surfaces): CODECOV_TOKEN,
  DEEPSEEK_AWS_WEB... (DEEPSEEK_AWS_* family), DEVICE_QUEUE_DATABASE_URL,
  FLY_IO_ORG_TOKEN, GITLAB_ADMIN_TOKEN, HEX_ALSO_USEDB...,
  HINDSIGHT_API_KEY / HINDSIGHT_BANK... / HINDSIGHT_BASE... /
  HINDSIGHT_TENANT... (HINDSIGHT_* family), LIKECLAW_A2A_G...,
  TMX_VAULT_AGE_..., VANTAGE_PAT_GH... (added recently; exact full name to be
  confirmed against settings), VERCEL_GITHUB_..., TERMUX_MCP_SSH...
  (TERMUX_MCP_* family), ARCHWIZ_GITHUB_TOKEN, CELLCOG_API_KEY,
  CLOUDFLARE_ACC... / CLOUDFLARE_API... (CLOUDFLARE_* family).
- Repository variables confirmed present: only three at snapshot time
  (DEVICE_QUEUE_* / TERMUX_* family values). SUPABASE_URL was absent at
  snapshot time and is the first variable to provision through the
  operator-variable-provision lane (workflow_dispatch or the gated
  issue-comment request on #184).
- Quota program status: QUOTA_EVAL_WATERMARK is created automatically by the
  quota-dispatch-tree on first advance; SUPABASE_URL provisioning is pending;
  SUPABASE_SERVICE_ROLE_KEY (secret) remains a manual Settings/gh-CLI action —
  no lane or agent can place secret values, by design.
