# Connector Management System

Centralized configuration for API integrations, webhooks, and external services.

## Schema (runtime)

The manager reads **environment variable names**, not secret values:

| Field | Purpose |
|-------|---------|
| `api_key_env` | Name of env var holding the API key |
| `api_secret_env` | Name of env var holding the secret |
| `passphrase_env` | Name of env var holding passphrase (KuCoin) |
| `token_env` | Name of env var holding a token (GitHub) |
| `secret_env` | Name of env var holding a webhook secret |

Env names must be on the allowlist in `ConnectorManager._ALLOWED_ENV_NAMES`.

## LLM providers example

```yaml
# .github/connectors/llm_providers.yaml
llm_providers:
  deepseek:
    enabled: true
    api_key_env: "DEEPSEEK_API_KEY"
    base_url: "https://api.deepseek.com"
    auth_method: "bearer"
    rate_limit: 100
    timeout: 60
    retry_attempts: 3
    models:
      - id: "deepseek-chat"
        name: "DeepSeek Chat"
  mistral:
    enabled: true
    api_key_env: "MISTRAL_API_KEY"
    base_url: "https://api.mistral.ai"
    auth_method: "bearer"
    models:
      - id: "mistral-small"
        name: "Mistral Small"
```

## GitHub example

```yaml
# .github/connectors/github.yaml
github:
  repository:
    owner: "timerloggedout-spec"
    name: "termux-monorepo"
  api:
    base_url: "https://api.github.com"
    token_env: "GITHUB_TOKEN"
    rate_limit: 5000
    timeout: 30
  webhooks:
    enabled: true
    secret_env: "GITHUB_WEBHOOK_SECRET"
  agents:
    jules:
      enabled: true
      api_key_env: "JULES_API_KEY"
    coderabbit:
      enabled: true
      api_key_env: "CODERABBIT_API_KEY"
```

## Webhooks (scaffold)

```yaml
# .github/connectors/webhooks.yaml
webhooks:
  github:
    base_url: "${WEBHOOK_RECEIVER_BASE_URL:-}"
    secret_env: "GITHUB_WEBHOOK_SECRET"
    endpoints:
      - name: "agent-review-auto-jules"
        path: "/github/webhook/agent-review-auto-jules"
        events: ["pull_request_review", "issue_comment"]
        active: false  # inactive until receiver deployed
  security:
    validate_signature: true
    scaffold: true
    note: "Enforced only when a receiver calls ConnectorManager.verify_webhook_signature"
```

## Exchanges

**Moved to PR #74** (`feature/exchange-connectors`). Not part of the project-management refresh.

## Python API

```bash
export PYTHONPATH=.github/connectors
python3 -c "from connector_manager import ConnectorManager; m = ConnectorManager(); print(m.list_connectors())"
bash .github/connectors/health_check.sh
```

```python
from connector_manager import ConnectorManager
manager = ConnectorManager()
if manager._load_failed:
    raise SystemExit(manager._load_errors)
print(manager.is_enabled("github", "api"))
```

## Security

1. Never commit secrets — only env var *names* in YAML
2. GitHub Actions → repository Secrets
3. Cross-origin absolute endpoints are **rejected** before credentials are attached
4. Env var names outside the allowlist raise `ValueError`
5. Webhook HMAC-SHA256 verification is implemented; wire it in the receiver

## Agent roster

See [`docs/schemas/agent-roster.yaml`](../docs/schemas/agent-roster.yaml) for collaborating agents, nested integrations (e.g. Tembo → Linear / MCP / sub-agents), and **triggerable comment commands** including CodeRabbit cooldown:

```text
@coderabbitai rate limit
```

Fallback: parse PR comments for `Next review available in: N minutes`.

---

*Last updated: 2026-08-07 · Maintainer: @timerloggedout-spec*
