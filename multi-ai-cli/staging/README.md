# Multi-AI CLI - Staging Environment

This directory contains staging-specific configurations for the Multi-AI CLI.

## Staging Setup

### Environment Configuration

```bash
# Create staging environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install staging-specific packages
pip install gunicorn uvloop
```

### Configuration Files

Create `staging_config.yaml`:

```yaml
# Backend configurations
backends:
  deepseek:
    token_path: ~/.config/deepseek/token.txt
    timeout: 60
  
  antigravity:
    api_key_path: ~/.config/antigravity/api_key.txt
    provider: gemini
    
  eigent:
    base_url: https://staging.eigent.ai
    api_key_path: ~/.config/eigent/api_key.txt

# Tool configurations
tools:
  audit_agent:
    max_file_size: 10485760  # 10MB
    timeout: 300
    
  search_bridge:
    provider: duckduckgo
    limit: 10

# Logging
logging:
  level: INFO
  file: /var/log/multi-ai-cli/staging.log
```

### Running in Staging

```bash
# Start the CLI
python cli.py --config staging_config.yaml

# Or use environment variables
export MULTI_AI_ENV=staging
python cli.py
```

### Health Checks

```bash
# Check all backends
python cli.py check --all

# Check specific backend
python cli.py check --backend deepseek

# Check tools
python cli.py check --tools
```

## Monitoring

### Metrics

```python
from core.session_manager import SessionManager
from core.chat_dispatcher import ChatDispatcher

mgr = SessionManager()
dispatcher = ChatDispatcher(mgr)

# Get backend metrics
metrics = dispatcher.get_metrics()
print(metrics)
```

### Logging

```bash
# View logs
tail -f /var/log/multi-ai-cli/staging.log

# Filter errors
grep ERROR /var/log/multi-ai-cli/staging.log
```

## Testing in Staging

### Integration Tests

```bash
# Run integration tests
python -m pytest tests/integration/

# Test specific backend
python -m pytest tests/integration/test_deepseek.py

# Test all tools
python -m pytest tests/integration/test_tools.py
```

### Load Testing

```bash
# Simple load test
for i in {1..10}; do
    python cli.py chat --provider deepseek "Test message $i" &
done

# Using Locust for load testing
locust -f tests/loadtest.py
```

## Deployment to Staging

### Manual Deployment

```bash
# Pull latest changes
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Restart services
systemctl restart multi-ai-cli
```

### Automated Deployment

```yaml
# .github/workflows/staging-deploy.yml
name: Staging Deployment

on:
  push:
    branches: [ staging ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r staging-requirements.txt
      
      - name: Run tests
        run: |
          python -m pytest tests/
      
      - name: Deploy
        run: |
          # Copy files to staging server
          scp -r . user@staging-server:/opt/multi-ai-cli
          ssh user@staging-server "systemctl restart multi-ai-cli"
```

## Troubleshooting

### Common Issues

1. **Backend not available**:
   ```bash
   # Check backend configuration
   python cli.py check --backend <backend>
   
   # Test backend manually
   python -c "from backends.<backend> import <Backend>; b = <Backend>(None); print(b.is_available())"
   ```

2. **Authentication errors**:
   ```bash
   # Check API keys
   ls -la ~/.config/*/token.txt ~/.config/*/api_key.txt
   
   # Test API key
   curl -H "Authorization: Bearer <API_KEY>" <API_ENDPOINT>
   ```

3. **Performance issues**:
   ```bash
   # Check response times
   time python cli.py chat --provider deepseek "Test"
   
   # Profile backend
   python -c "import cProfile; cProfile.run('from backends.deepseek import DeepSeekBackend; b = DeepSeekBackend(None); b.send_message(\"Test\")')"
   ```

### Debug Mode

```bash
# Enable debug logging
export MULTI_AI_DEBUG=1
python cli.py --verbose

# Or in code
import logging
logging.basicConfig(level=logging.DEBUG)
```
