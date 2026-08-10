# Connector Catalog (AUTHORIZED)

Centralized, non-secret configuration for external integrations.
Runtime code and Actions read **environment variable names** only — never secret values.

## Authorized secrets (GitHub Actions / repo secrets)

| Secret name | Purpose | Used by |
|-------------|---------|--------|
| `OPERATOR_GITHUB_TOKEN` | Write/admin PAT for CodeRabbit autofix, privileged comments, continuous-ops | peer-review-orchestrator, continuous-ops, auto-jules |
| `GITHUB_TOKEN` | Default Actions token (contents/PRs/issues scoped) | all workflows |
| `OMNI_API_KEY` / `OMNIROUTE_API_KEY` | OmniRoute free-tier peer | model-router, http-llm-invoke |
| `OMNI_BASE_URL` | Optional override (must be https allow-listed host) | http-llm-invoke |
| `OPENROUTER_API_KEY` | OpenRouter free-tier peer (`:free` models only) | model-router, http-llm-invoke |
| `GEMINI_API_KEY` | Gemini residual path | gemini-* workflows |
| Linear / Vercel / other | Connected via Grok Connectors or separate secrets as needed | agent-feedback-linear-sync, deploy |

## Provider allow-list (http-llm-invoke)

- `cloud.omniroute.online`
- `openrouter.ai` / `api.openrouter.ai`

HTTPS only. Non-allow-listed hosts are rejected.

## Soft-budget policy (exceed prior capacity)

See `scripts/model_router.py` and `docs/schemas/model-success-matrix.yaml`.
Omni `auto/best-free` and OpenRouter free models have elevated daily soft limits
so peer capacity is preferred over Gemini residual. Limits are best-effort
(Actions cache per Pacific day).

## Files in this directory

- `github.yaml` — repo identity + API surface
- `llm-peers.yaml` — Omni / OpenRouter / Gemini routing preferences
- `integrations.yaml` — Linear, Vercel, Jules, CodeRabbit, Devin markers

Exchange connectors (Yobit/KuCoin/Binance) were **intentionally removed** from
the active surface (PR #74 closed). Do not reintroduce without OPERATOR sign-off.
