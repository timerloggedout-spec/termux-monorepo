# Multi-AI CLI - Production Environment

This directory contains production-specific configurations for the Multi-AI CLI.

## Production Setup

### Requirements

- **Python**: 3.10+
- **OS**: Linux (Ubuntu 22.04 LTS recommended)
- **Memory**: 4GB+ (8GB recommended for multiple backends)
- **Storage**: 10GB+ (for caching and logs)
- **Network**: Stable internet connection

### Installation

```bash
# Create production user
sudo useradd -r -m -d /opt/multi-ai-cli multi-ai-cli

# Create directories
sudo mkdir -p /opt/multi-ai-cli/{app,logs,config,data}
sudo chown -R multi-ai-cli:multi-ai-cli /opt/multi-ai-cli

# Install Python
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# Create virtual environment
sudo -u multi-ai-cli bash -c "python3 -m venv /opt/multi-ai-cli/venv"

# Install dependencies
sudo -u multi-ai-cli bash -c "/opt/multi-ai-cli/venv/bin/pip install -r /opt/multi-ai-cli/requirements.txt"
```

### Configuration

Create `/opt/multi-ai-cli/config/prod_config.yaml`:

```yaml
# Production configuration
production: true

# Backend configurations
backends:
  deepseek:
    token_path: /opt/multi-ai-cli/config/deepseek_token.txt
    timeout: 120
    max_retries: 3
    
  antigravity:
    api_key_path: /opt/multi-ai-cli/config/gemini_api_key.txt
    provider: gemini
    timeout: 120
    
  eigent:
    base_url: https://api.eigent.ai
    api_key_path: /opt/multi-ai-cli/config/eigent_api_key.txt
    timeout: 120
    
  opencode:
    model: mistral-large
    provider: openrouter
    timeout: 120
    
  velocity:
    model: mistral-large
    provider: openrouter
    timeout: 120

# Tool configurations
tools:
  audit_agent:
    max_file_size: 52428800  # 50MB
    timeout: 600
    max_depth: 10
    
  search_bridge:
    provider: google
    api_key_path: /opt/multi-ai-cli/config/google_api_key.txt
    limit: 20
    
  lazy_gravity:
    enabled: false
    api_key_path: /opt/multi-ai-cli/config/discord_token.txt
    
  antimatter:
    enabled: false
    host: 0.0.0.0
    port: 8080

# Logging
logging:
  level: WARNING
  file: /opt/multi-ai-cli/logs/multi-ai-cli.log
  max_size: 10485760  # 10MB
  backup_count: 5

# Security
security:
  allowed_origins: []
  rate_limit: 1000
  max_request_size: 10485760  # 10MB

# Performance
performance:
  max_concurrent_requests: 10
  request_timeout: 300
  cache_enabled: true
  cache_ttl: 3600  # 1 hour
```

### Systemd Service

Create `/etc/systemd/system/multi-ai-cli.service`:

```ini
[Unit]
Description=Multi-AI CLI Service
After=network.target

[Service]
User=multi-ai-cli
Group=multi-ai-cli
WorkingDirectory=/opt/multi-ai-cli
Environment=PATH=/opt/multi-ai-cli/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=PYTHONPATH=/opt/multi-ai-cli
ExecStart=/opt/multi-ai-cli/venv/bin/python /opt/multi-ai-cli/cli.py server
Restart=always
RestartSec=5
StandardOutput=append:/opt/multi-ai-cli/logs/service.log
StandardError=append:/opt/multi-ai-cli/logs/service_error.log

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable multi-ai-cli
sudo systemctl start multi-ai-cli
sudo systemctl status multi-ai-cli
```

## Production Operations

### Monitoring

```bash
# View service logs
sudo journalctl -u multi-ai-cli -f

# Check service status
sudo systemctl status multi-ai-cli

# View application logs
tail -f /opt/multi-ai-cli/logs/multi-ai-cli.log
```

### Metrics

```bash
# Get backend metrics
sudo -u multi-ai-cli bash -c "
    /opt/multi-ai-cli/venv/bin/python -c \"
    from core.chat_dispatcher import ChatDispatcher
    from core.session_manager import SessionManager
    mgr = SessionManager('/opt/multi-ai-cli/config/prod_config.yaml')
    dispatcher = ChatDispatcher(mgr)
    print(dispatcher.get_metrics())
    \"
"
```

### Health Checks

```bash
# Check all backends
curl http://localhost:8000/health

# Check specific backend
curl http://localhost:8000/health/deepseek

# Check tools
curl http://localhost:8000/health/tools
```

## Deployment

### Manual Deployment

```bash
# Pull latest changes
cd /opt/multi-ai-cli
git pull origin main

# Install new dependencies
/opt/multi-ai-cli/venv/bin/pip install -r requirements.txt

# Restart service
sudo systemctl restart multi-ai-cli
```

### Automated Deployment

```yaml
# .github/workflows/prod-deploy.yml
name: Production Deployment

on:
  push:
    tags: [ 'v*' ]

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
      
      - name: Run tests
        run: |
          python -m pytest tests/
      
      - name: Deploy
        run: |
          # Build distribution
          python setup.py sdist
          
          # Copy to production server
          scp dist/* user@prod-server:/tmp/
          ssh user@prod-server "
            sudo systemctl stop multi-ai-cli
            sudo cp /tmp/multi-ai-cli-* /opt/multi-ai-cli/
            cd /opt/multi-ai-cli
            sudo -u multi-ai-cli /opt/multi-ai-cli/venv/bin/pip install dist/*
            sudo systemctl start multi-ai-cli
          "
```

### Blue-Green Deployment

```bash
# Setup blue and green environments
sudo mkdir -p /opt/multi-ai-cli-{blue,green}

# Deploy to green
rsync -av /opt/multi-ai-cli-blue/ /opt/multi-ai-cli-green/

# Switch to green
sudo systemctl stop multi-ai-cli-blue
sudo systemctl start multi-ai-cli-green

# Verify green
curl http://localhost:8000/health

# Switch traffic (if using load balancer)
# Update load balancer configuration to point to green

# Cleanup blue (after verification)
sudo rm -rf /opt/multi-ai-cli-blue/*
```

## Security

### API Keys

```bash
# Store API keys securely
sudo -u multi-ai-cli bash -c "
    echo 'your_deepseek_token' > /opt/multi-ai-cli/config/deepseek_token.txt
    echo 'your_gemini_key' > /opt/multi-ai-cli/config/gemini_api_key.txt
    chmod 600 /opt/multi-ai-cli/config/*.txt
"
```

### Firewall

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp     # SSH
sudo ufw allow 80/tcp     # HTTP
sudo ufw allow 443/tcp    # HTTPS
sudo ufw allow 8000/tcp   # Application (if exposed)
sudo ufw enable
```

### SSL/TLS

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renew
sudo certbot renew --dry-run
```

## Backup

### Configuration Backup

```bash
# Backup configuration
sudo tar -czvf /backup/multi-ai-cli-config-$(date +%Y%m%d).tar.gz \
    /opt/multi-ai-cli/config
```

### Data Backup

```bash
# Backup data
sudo tar -czvf /backup/multi-ai-cli-data-$(date +%Y%m%d).tar.gz \
    /opt/multi-ai-cli/data
```

### Database Backup

```bash
# If using PostgreSQL
sudo -u postgres pg_dump multi_ai_cli > /backup/multi-ai-cli-db-$(date +%Y%m%d).sql
```

## Scaling

### Horizontal Scaling

```bash
# Run multiple instances
sudo cp /etc/systemd/system/multi-ai-cli.service \
    /etc/systemd/system/multi-ai-cli@.service

# Modify service to use instance ID
sudo sed -i 's/multi-ai-cli/multi-ai-cli@%i/' \
    /etc/systemd/system/multi-ai-cli@.service

# Start multiple instances
sudo systemctl start multi-ai-cli@1
sudo systemctl start multi-ai-cli@2
sudo systemctl start multi-ai-cli@3
```

### Load Balancing

```bash
# Install nginx
sudo apt install -y nginx

# Configure load balancer
cat > /etc/nginx/conf.d/multi-ai-cli.conf << 'EOF'
upstream multi_ai_cli {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://multi_ai_cli;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

sudo systemctl restart nginx
```

## Troubleshooting

### Log Rotation

```bash
# Configure logrotate
cat > /etc/logrotate.d/multi-ai-cli << 'EOF'
/opt/multi-ai-cli/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 multi-ai-cli multi-ai-cli
    sharedscripts
    postrotate
        systemctl reload multi-ai-cli > /dev/null 2>&1 || true
    endscript
}
EOF
```

### Error Tracking

```bash
# Setup Sentry
pip install sentry-sdk

# Configure in code
import sentry_sdk
sentry_sdk.init(
    dsn="your-dsn",
    integrations=[LoggingIntegration()],
    traces_sample_rate=1.0
)
```

### Performance Tuning

```bash
# Adjust worker count
# In cli.py server command
workers = (os.cpu_count() or 1) * 2 + 1

# Adjust timeouts
# In prod_config.yaml
performance:
  request_timeout: 600
  max_concurrent_requests: 20
```
