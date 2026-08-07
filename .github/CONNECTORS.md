# Connector Management System

This document defines the connector management system for the termux-monorepo, including API integrations, webhook configurations, and external service connections.

## Overview

The termux-monorepo integrates with multiple external services, APIs, and platforms. This document provides a centralized configuration and management system for all connectors.

## Connector Types

### 1. API Connectors
- **LLM Providers**: DeepSeek, Mistral, Claude, Grok, etc.
- **Exchange APIs**: Yobit, Binance, Kucoin, etc.
- **GitHub API**: Repository management, issues, PRs
- **Other APIs**: As needed for specific integrations

### 2. Webhook Connectors
- **GitHub Webhooks**: For CI/CD and automation
- **Agent Webhooks**: For multi-agent coordination
- **Notification Webhooks**: For status updates

### 3. Database Connectors
- **Local SQLite**: For session storage and metadata
- **External Databases**: As needed for specific projects

### 4. File System Connectors
- **Termux Storage**: Android-specific storage access
- **Cloud Storage**: For backups and shared resources

---

## Connector Configuration

### API Connectors Configuration

#### LLM Provider Connectors

```yaml
# .github/connectors/llm_providers.yaml
llm_providers:
  deepseek:
    enabled: true
    api_key_env: "DEEPSEEK_API_KEY"
    auth_method: "bearer"
    base_url: "https://api.deepseek.com"
    rate_limit: 100
    timeout: 60
    retry_attempts: 3
    models:
      - id: "deepseek-chat"
        name: "DeepSeek Chat"
      - id: "deepseek-coder"
        name: "DeepSeek Coder"
    
  mistral:
    enabled: true
    api_key_env: "MISTRAL_API_KEY"
    auth_method: "bearer"
    base_url: "https://api.mistral.ai"
    rate_limit: 100
    timeout: 60
    retry_attempts: 3
    models:
      - id: "mistral-tiny"
        name: "Mistral Tiny"
      - id: "mistral-small"
        name: "Mistral Small"
      - id: "mistral-medium"
        name: "Mistral Medium"
      - id: "mistral-large"
        name: "Mistral Large"
    
  claude:
    enabled: false
    api_key_env: "CLAUDE_API_KEY"
    base_url: "https://api.anthropic.com"
    rate_limit: 100
    timeout: 60
    retry_attempts: 3
    models:
      - id: "claude-3-haiku-20240307"
        name: "Claude 3 Haiku"
      - id: "claude-3-sonnet-20240229"
        name: "Claude 3 Sonnet"
      - id: "claude-3-opus-20240229"
        name: "Claude 3 Opus"
    
  grok:
    enabled: false
    api_key_env: "GROK_API_KEY"
    base_url: "https://api.grok.com"
    rate_limit: 100
    timeout: 60
    retry_attempts: 3
    models:
      - id: "grok-beta"
        name: "Grok Beta"
      - id: "grok-1"
        name: "Grok 1"
```

#### Exchange API Connectors

```yaml
# .github/connectors/exchanges.yaml
exchanges:
  yobit:
    enabled: true
    api_key_env: "YOBIT_API_KEY"
    api_secret_env: "YOBIT_API_SECRET"
    auth_method: "hmac"
    hash_algorithm: "sha512"
    base_url: "https://yobit.net"
    api_version: "3"
    rate_limit: 10
    timeout: 30
    retry_attempts: 3
    pairs:
      - "BTC_USD"
      - "ETH_USD"
      - "LTC_USD"
    
  binance:
    enabled: false
    api_key_env: "BINANCE_API_KEY"
    api_secret_env: "BINANCE_API_SECRET"
    auth_method: "hmac"
    hash_algorithm: "sha256"
    base_url: "https://api.binance.com"
    api_version: "v3"
    rate_limit: 1200
    timeout: 30
    retry_attempts: 3
    
  kucoin:
    enabled: true
    api_key_env: "KUCOIN_API_KEY"
    api_secret_env: "KUCOIN_API_SECRET"
    passphrase_env: "KUCOIN_PASSPHRASE"
    auth_method: "jwt"
    hash_algorithm: "sha256"
    base_url: "https://api.kucoin.com"
    api_version: "v1"
    rate_limit: 100
    timeout: 30
    retry_attempts: 3
    # Public endpoints that do not require authentication
    public_endpoints:
      - symbols
      - ticker
      - order_book
      - trades
      - kline
```

#### GitHub Connectors

```yaml
# .github/connectors/github.yaml
github:
  repository:
    owner: "timerloggedout-spec"
    name: "termux-monorepo"
    
  api:
    base_url: "https://api.github.com"
    graphql_url: "https://api.github.com/graphql"
    token_env: "GITHUB_TOKEN"
    rate_limit: 5000
    timeout: 30
    retry_attempts: 3
    headers:
      Accept: "application/vnd.github+json"
      X-GitHub-Api-Version: "2022-11-28"
    
  webhooks:
    enabled: true
    secret_env: "GITHUB_WEBHOOK_SECRET"
    endpoints:
      - name: "agent-review-auto-jules"
        path: "/github/webhook/agent-review-auto-jules"
        events:
          - "pull_request_review"
          - "pull_request_review_comment"
          - "issue_comment"
        active: true
        content_type: "application/json"
    
  agents:
    jules:
      enabled: true
      api_key_env: "JULES_API_KEY"
      reactive_mode: false
      auto_invoke: true
      
    coderabbit:
      enabled: true
      api_key_env: "CODERABBIT_API_KEY"
      
    devin:
      enabled: false
      api_key_env: "DEVIN_API_KEY"
```

### Webhook Configuration

#### GitHub Webhook Endpoints

```yaml
# .github/connectors/webhooks.yaml
webhooks:
  github:
    base_url: "https://github.com/timerloggedout-spec/termux-monorepo"
    secret_env: "GITHUB_WEBHOOK_SECRET"
    endpoints:
      - name: "agent-review-auto-jules"
        path: "/github/webhook/agent-review-auto-jules"
        events:
          - "pull_request_review"
          - "pull_request_review_comment"
          - "issue_comment"
        active: true
        content_type: "application/json"
        action: "jules_auto_resolve"
        
      - name: "agent-jules-on-issues"
        path: "/github/webhook/agent-jules-on-issues"
        events:
          - "issues"
          - "issue_comment"
        active: true
        content_type: "application/json"
        action: "jules_issue_response"
        
      - name: "agent-feedback-linear-sync"
        path: "/github/webhook/agent-feedback-linear-sync"
        events:
          - "issues"
          - "pull_request"
        active: true
        content_type: "application/json"
        action: "linear_sync"
        
      - name: "gemini-dispatch"
        path: "/github/webhook/gemini-dispatch"
        events:
          - "push"
          - "pull_request"
        active: true
        content_type: "application/json"
        action: "gemini_dispatch"
        
      - name: "publish-wiki"
        path: "/github/webhook/publish-wiki"
        events:
          - "push"
        paths:
          - "wiki/**"
        active: true
        content_type: "application/json"
        action: "publish_wiki"

  # Webhook security
  security:
    validate_signature: true
    validate_content_type: true
    rate_limiting:
      enabled: true
      max_requests: 100
      burst_limit: 20
```

---

## Connector Management Scripts

### Python Connector Manager

The ConnectorManager Python library provides a unified interface for managing all connectors. See the full implementation in [.github/connectors/connector_manager.py](connectors/connector_manager.py).

**Usage Example:**

```python
from connector_manager import ConnectorManager

manager = ConnectorManager()

# List all connectors
connectors = manager.list_connectors()

# Get specific connector
deepseek_config = manager.get_llm_provider("deepseek")

# Test connector
result = manager.test_connector("llm_providers", "deepseek")
```

### Connector Health Check Script

The health_check.sh script validates connector configurations and tests enabled connectors. See the full implementation in [.github/connectors/health_check.sh](connectors/health_check.sh).

**Usage Example:**

```bash
# Run health check
bash .github/connectors/health_check.sh
```

---

## Connector Security

### Environment Variables

All sensitive connector configuration should use environment variables:

```bash
# Required environment variables
export DEEPSEEK_API_KEY="your_deepseek_api_key"
export MISTRAL_API_KEY="your_mistral_api_key"
export GITHUB_TOKEN="your_github_token"
export GITHUB_WEBHOOK_SECRET="your_webhook_secret"
export JULES_API_KEY="your_jules_api_key"

# Optional environment variables
export CLAUDE_API_KEY="your_claude_api_key"
export GROK_API_KEY="your_grok_api_key"
export YOBIT_API_KEY="your_yobit_api_key"
export YOBIT_API_SECRET="your_yobit_api_secret"
```

### Security Best Practices

1. **Never commit secrets**: All API keys and tokens should be in environment variables or secret management systems
2. **Use GitHub Secrets**: For CI/CD workflows, use GitHub Secrets
3. **Rotate credentials**: Regularly rotate API keys and tokens
4. **Limit permissions**: Use the principle of least privilege for all connectors
5. **Audit access**: Regularly audit connector access and usage

### Secret Management

```yaml
# .github/connectors/secrets_template.yaml
# This file shows the structure for secret management
# DO NOT COMMIT ACTUAL SECRETS TO GIT

secrets:
  required:
    - DEEPSEEK_API_KEY
    - MISTRAL_API_KEY
    - GITHUB_TOKEN
    - GITHUB_WEBHOOK_SECRET
    
  optional:
    - CLAUDE_API_KEY
    - GROK_API_KEY
    - YOBIT_API_KEY
    - YOBIT_API_SECRET
    - KUCOIN_API_KEY
    - KUCOIN_API_SECRET
    - JULES_API_KEY
    - CODERABBIT_API_KEY
```

---

## Connector Usage Examples

### Using LLM Providers

```python
from connector_manager import ConnectorManager
import requests
import os

manager = ConnectorManager()

# Get DeepSeek configuration
deepseek_config = manager.get_llm_provider("deepseek")

if deepseek_config and deepseek_config.get("enabled", False):
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    base_url = deepseek_config.get("base_url")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "Hello"}]
    }
    
    response = requests.post(
        f"{base_url}/chat/completions",
        headers=headers,
        json=data,
        timeout=deepseek_config.get("timeout", 60)
    )
    
    print(response.json())
```

### Using Exchange APIs

```python
from connector_manager import ConnectorManager
import requests
import hashlib
import hmac
import time
import os

manager = ConnectorManager()

# Get Yobit configuration
yobit_config = manager.get_exchange("yobit")

if yobit_config and yobit_config.get("enabled", False):
    api_key = os.environ.get("YOBIT_API_KEY")
    api_secret = os.environ.get("YOBIT_API_SECRET")
    base_url = yobit_config.get("base_url")
    
    # Create signed request
    nonce = str(int(time.time() * 1000))
    message = f"nonce={nonce}"
    signature = hmac.new(
        api_secret.encode(),
        message.encode(),
        hashlib.sha512
    ).hexdigest()
    
    headers = {
        "Key": api_key,
        "Sign": signature
    }
    
    params = {
        "nonce": nonce
    }
    
    response = requests.get(
        f"{base_url}/api/3/info",
        headers=headers,
        params=params,
        timeout=yobit_config.get("timeout", 30)
    )
    
    print(response.json())
```

---

## Connector Monitoring

### Health Metrics

```yaml
# .github/connectors/metrics.yaml
metrics:
  llm_providers:
    enabled: true
    track:
      - request_count
      - error_count
      - response_time
      - token_usage
    
  exchanges:
    enabled: true
    track:
      - request_count
      - error_count
      - response_time
      - rate_limits
    
  github:
    enabled: true
    track:
      - api_calls
      - webhook_events
      - error_count
```

### Monitoring Script

Connector monitoring and metrics tracking can be implemented as needed. The ConnectorManager provides built-in health checking via the `test_connector()` method and `health_check.sh` script.

---

## Connector Documentation

### Available Connectors

| Connector Type | Name | Status | Documentation |
|---------------|------|--------|---------------|
| LLM Provider | DeepSeek | Enabled | [DeepSeek API Docs](https://deepseek.com/docs) |
| LLM Provider | Mistral | Enabled | [Mistral API Docs](https://docs.mistral.ai) |
| LLM Provider | Claude | Disabled | [Claude API Docs](https://docs.anthropic.com) |
| LLM Provider | Grok | Disabled | [Grok API Docs](https://docs.grok.com) |
| Exchange | Yobit | Enabled | [Yobit API Docs](https://yobit.net/en/api) |
| Exchange | Kucoin | Enabled | [Kucoin API Docs](https://docs.kucoin.com) |
| Exchange | Binance | Disabled | [Binance API Docs](https://binance-docs.github.io) |
| Platform | GitHub | Enabled | [GitHub API Docs](https://docs.github.com) |

### Connector Setup Guides

#### Setting up DeepSeek

1. Get API key from [DeepSeek](https://deepseek.com)
2. Set environment variable: `export DEEPSEEK_API_KEY="your_key"`
3. Enable in `llm_providers.yaml`: `deepseek.enabled: true`
4. Test connection: `PYTHONPATH=.github/connectors python3 -c "from connector_manager import ConnectorManager; m = ConnectorManager(); print(m.test_connector('llm_providers', 'deepseek'))"`

#### Setting up GitHub Webhooks

1. Go to repository Settings > Webhooks
2. Add webhook with URL: `https://your-server/github/webhook`
3. Set secret: `GITHUB_WEBHOOK_SECRET`
4. Select events: push, pull_request, issues, issue_comment
5. Enable webhook

---

## Troubleshooting

### Common Issues

1. **Authentication Failed**: Check that API keys are correctly set in environment variables
2. **Rate Limit Exceeded**: Check rate limits in connector configuration and implement retries
3. **Connection Timeout**: Increase timeout values in connector configuration
4. **Invalid Request**: Check request format and parameters

### Debug Mode

Enable debug logging for connectors:

```bash
export CONNECTOR_DEBUG=true
python3 your_script.py
```

### Log Files

Connector logs are stored in `.github/connectors/logs/`:
- `llm_providers.log`: LLM provider API calls
- `exchanges.log`: Exchange API calls
- `github.log`: GitHub API calls
- `webhooks.log`: Webhook events

---

## Maintenance

### Regular Tasks

1. **Update API keys**: Rotate API keys regularly
2. **Check rate limits**: Monitor API usage and adjust rate limits
3. **Test connectors**: Regularly test all enabled connectors
4. **Update documentation**: Keep connector documentation up-to-date
5. **Review security**: Regularly review connector security settings

### Version Updates

When updating connector configurations:
1. Test changes in a development environment
2. Update documentation
3. Announce changes to team
4. Monitor for issues after deployment

---

## Quick Reference

| Task | Command |
|------|---------|
| List connectors | `python3 .github/connectors/connector_manager.py` |
| Check health | `bash .github/connectors/health_check.sh` |
| Test connector | `PYTHONPATH=.github/connectors python3 -c "from connector_manager import ConnectorManager; m = ConnectorManager(); print(m.test_connector('llm_providers', 'deepseek'))"` |

---

*Last updated: 2026-08-06*
*Maintainer: @timerloggedout-spec*
