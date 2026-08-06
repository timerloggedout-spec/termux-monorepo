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
    api_key: "${DEEPSEEK_API_KEY}"
    base_url: "https://api.deepseek.com"
    rate_limit: 100
    timeout: 60
    retry_attempts: 3
    models:
      - "deepseek-chat"
      - "deepseek-coder"
    
  mistral:
    enabled: true
    api_key: "${MISTRAL_API_KEY}"
    base_url: "https://api.mistral.ai"
    rate_limit: 100
    timeout: 60
    retry_attempts: 3
    models:
      - "mistral-tiny"
      - "mistral-small"
      - "mistral-medium"
      - "mistral-large"
    
  claude:
    enabled: false
    api_key: "${CLAUDE_API_KEY}"
    base_url: "https://api.anthropic.com"
    rate_limit: 100
    timeout: 60
    retry_attempts: 3
    models:
      - "claude-3-haiku"
      - "claude-3-sonnet"
      - "claude-3-opus"
    
  grok:
    enabled: false
    api_key: "${GROK_API_KEY}"
    base_url: "https://api.grok.com"
    rate_limit: 100
    timeout: 60
    retry_attempts: 3
    models:
      - "grok-beta"
      - "grok-1"
```

#### Exchange API Connectors

```yaml
# .github/connectors/exchanges.yaml
exchanges:
  yobit:
    enabled: true
    api_key: "${YOBIT_API_KEY}"
    api_secret: "${YOBIT_API_SECRET}"
    base_url: "https://yobit.net"
    rate_limit: 10
    timeout: 30
    retry_attempts: 3
    pairs:
      - "BTC_USD"
      - "ETH_USD"
      - "LTC_USD"
    
  binance:
    enabled: false
    api_key: "${BINANCE_API_KEY}"
    api_secret: "${BINANCE_API_SECRET}"
    base_url: "https://api.binance.com"
    rate_limit: 1200
    timeout: 30
    retry_attempts: 3
    
  kucoin:
    enabled: true
    api_key: "${KUCOIN_API_KEY}"
    api_secret: "${KUCOIN_API_SECRET}"
    base_url: "https://api.kucoin.com"
    rate_limit: 100
    timeout: 30
    retry_attempts: 3
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
    token: "${GITHUB_TOKEN}"
    rate_limit: 5000
    timeout: 30
    retry_attempts: 3
    
  webhooks:
    enabled: true
    secret: "${GITHUB_WEBHOOK_SECRET}"
    events:
      - "push"
      - "pull_request"
      - "issues"
      - "issue_comment"
      - "pull_request_review"
      - "pull_request_review_comment"
    
  agents:
    jules:
      enabled: true
      api_key: "${JULES_API_KEY}"
      reactive_mode: false
      
    coderabbit:
      enabled: true
      api_key: "${CODERABBIT_API_KEY}"
      
    devin:
      enabled: false
      api_key: "${DEVIN_API_KEY}"
```

### Webhook Configuration

#### GitHub Webhook Endpoints

```yaml
# .github/connectors/webhooks.yaml
webhooks:
  github:
    agent_review_auto_jules:
      endpoint: "/github/webhook/agent-review-auto-jules"
      events:
        - "pull_request_review"
        - "pull_request_review_comment"
        - "issue_comment"
      active: true
      
    agent_jules_on_issues:
      endpoint: "/github/webhook/agent-jules-on-issues"
      events:
        - "issues"
        - "issue_comment"
      active: true
      
    agent_feedback_linear_sync:
      endpoint: "/github/webhook/agent-feedback-linear-sync"
      events:
        - "issues"
        - "pull_request"
      active: true
      
    gemini_dispatch:
      endpoint: "/github/webhook/gemini-dispatch"
      events:
        - "push"
        - "pull_request"
      active: true
      
    publish_wiki:
      endpoint: "/github/webhook/publish-wiki"
      events:
        - "push"
      paths:
        - "wiki/**"
      active: true
```

---

## Connector Management Scripts

### Python Connector Manager

```python
# .github/connectors/connector_manager.py
#!/usr/bin/env python3
"""
Connector Management System for termux-monorepo
Manages API connectors, webhooks, and external service integrations
"""

import os
import yaml
import json
import requests
from typing import Dict, Any, Optional
from pathlib import Path

CONNECTORS_DIR = Path(__file__).parent

class ConnectorManager:
    def __init__(self):
        self.connectors = {}
        self.load_connectors()
    
    def load_connectors(self):
        """Load all connector configurations from YAML files"""
        for config_file in CONNECTORS_DIR.glob("*.yaml"):
            if config_file.name == "webhooks.yaml":
                continue
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                for connector_type, config_data in config.items():
                    self.connectors[connector_type] = config_data
    
    def get_connector(self, connector_type: str, connector_name: str) -> Optional[Dict]:
        """Get a specific connector configuration"""
        if connector_type in self.connectors:
            if connector_name in self.connectors[connector_type]:
                return self.connectors[connector_type][connector_name]
        return None
    
    def list_connectors(self) -> Dict[str, Any]:
        """List all available connectors"""
        return {
            "llm_providers": list(self.connectors.get("llm_providers", {}).keys()),
            "exchanges": list(self.connectors.get("exchanges", {}).keys()),
            "github": self.connectors.get("github", {}),
            "webhooks": self.connectors.get("webhooks", {})
        }
    
    def test_connector(self, connector_type: str, connector_name: str) -> bool:
        """Test a connector by making a simple API call"""
        connector = self.get_connector(connector_type, connector_name)
        if not connector or not connector.get("enabled", False):
            return False
        
        # Implement actual API test based on connector type
        # This is a placeholder - implement actual API calls
        return True
    
    def get_llm_provider(self, provider_name: str) -> Optional[Dict]:
        """Get LLM provider configuration"""
        return self.get_connector("llm_providers", provider_name)
    
    def get_exchange(self, exchange_name: str) -> Optional[Dict]:
        """Get exchange API configuration"""
        return self.get_connector("exchanges", exchange_name)
    
    def get_github_config(self) -> Optional[Dict]:
        """Get GitHub configuration"""
        return self.connectors.get("github")

# Usage example
if __name__ == "__main__":
    manager = ConnectorManager()
    print("Available connectors:")
    print(json.dumps(manager.list_connectors(), indent=2))
```

### Connector Health Check Script

```bash
#!/bin/bash
# .github/connectors/health_check.sh

set -e

echo "=== Connector Health Check ==="
echo ""

# Check LLM providers
echo "LLM Providers:"
python3 -c "
from connector_manager import ConnectorManager
manager = ConnectorManager()
for provider in manager.list_connectors()['llm_providers']:
    config = manager.get_llm_provider(provider)
    status = 'enabled' if config.get('enabled', False) else 'disabled'
    print(f'  {provider}: {status}')
"

echo ""
echo "Exchanges:"
python3 -c "
from connector_manager import ConnectorManager
manager = ConnectorManager()
for exchange in manager.list_connectors()['exchanges']:
    config = manager.get_exchange(exchange)
    status = 'enabled' if config.get('enabled', False) else 'disabled'
    print(f'  {exchange}: {status}')
"

echo ""
echo "GitHub:"
python3 -c "
from connector_manager import ConnectorManager
manager = ConnectorManager()
github = manager.get_github_config()
if github:
    print(f'  Repository: {github.get(\"repository\", {}).get(\"owner\", \"unknown\")}/{github.get(\"repository\", {}).get(\"name\", \"unknown\")}')
    print(f'  API: enabled')
    print(f'  Webhooks: {\"enabled\" if github.get(\"webhooks\", {}).get(\"enabled\", False) else \"disabled\"}')
"

echo ""
echo "Health check complete."
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

```python
# .github/connectors/monitor.py
#!/usr/bin/env python3
"""
Connector Monitoring System
Tracks usage, errors, and performance of all connectors
"""

import json
import time
from datetime import datetime
from pathlib import Path
from connector_manager import ConnectorManager

METRICS_FILE = Path(__file__).parent / "metrics.json"

class ConnectorMonitor:
    def __init__(self):
        self.manager = ConnectorManager()
        self.metrics = self.load_metrics()
    
    def load_metrics(self):
        """Load existing metrics"""
        if METRICS_FILE.exists():
            with open(METRICS_FILE, 'r') as f:
                return json.load(f)
        return {
            "llm_providers": {},
            "exchanges": {},
            "github": {}
        }
    
    def save_metrics(self):
        """Save metrics to file"""
        with open(METRICS_FILE, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def record_request(self, connector_type: str, connector_name: str, success: bool, response_time: float):
        """Record a connector request"""
        if connector_type not in self.metrics:
            self.metrics[connector_type] = {}
        
        if connector_name not in self.metrics[connector_type]:
            self.metrics[connector_type][connector_name] = {
                "requests": 0,
                "errors": 0,
                "total_time": 0,
                "last_request": None
            }
        
        self.metrics[connector_type][connector_name]["requests"] += 1
        self.metrics[connector_type][connector_name]["total_time"] += response_time
        
        if not success:
            self.metrics[connector_type][connector_name]["errors"] += 1
        
        self.metrics[connector_type][connector_name]["last_request"] = datetime.now().isoformat()
        self.save_metrics()
    
    def get_stats(self, connector_type: str, connector_name: str) -> dict:
        """Get statistics for a connector"""
        if (connector_type in self.metrics and 
            connector_name in self.metrics[connector_type]):
            stats = self.metrics[connector_type][connector_name]
            avg_time = (stats["total_time"] / stats["requests"]) if stats["requests"] > 0 else 0
            return {
                **stats,
                "avg_response_time": avg_time,
                "success_rate": 1 - (stats["errors"] / stats["requests"]) if stats["requests"] > 0 else 1
            }
        return {}
    
    def get_all_stats(self) -> dict:
        """Get statistics for all connectors"""
        return self.metrics

# Usage example
if __name__ == "__main__":
    monitor = ConnectorMonitor()
    
    # Record a sample request
    monitor.record_request("llm_providers", "deepseek", True, 1.5)
    monitor.record_request("llm_providers", "deepseek", True, 2.1)
    monitor.record_request("llm_providers", "deepseek", False, 0.5)
    
    print("DeepSeek Stats:")
    print(json.dumps(monitor.get_stats("llm_providers", "deepseek"), indent=2))
```

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
4. Test connection: `python3 -c "from connector_manager import ConnectorManager; m = ConnectorManager(); print(m.test_connector('llm_providers', 'deepseek'))"`

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
| Test connector | `python3 -c "from connector_manager import ConnectorManager; m = ConnectorManager(); print(m.test_connector('llm_providers', 'deepseek'))"` |
| View metrics | `python3 .github/connectors/monitor.py` |

---

*Last updated: 2026-08-06*
*Maintainer: @timerloggedout-spec*
