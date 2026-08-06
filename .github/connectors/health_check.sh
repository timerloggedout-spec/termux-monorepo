#!/bin/bash
# Connector Health Check Script
# Checks the status of all configured connectors

set -e

echo "=========================================="
echo "Connector Health Check"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track failures
FAILED=0

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_status "$RED" "Error: python3 is not installed"
    exit 1
fi

# Check if connectors directory exists
CONNECTORS_DIR="$(dirname "$0")"
if [ ! -d "$CONNECTORS_DIR" ]; then
    print_status "$RED" "Error: Connectors directory not found: $CONNECTORS_DIR"
    exit 1
fi

# Set PYTHONPATH so imports work from any directory
export PYTHONPATH="$CONNECTORS_DIR:$PYTHONPATH"

# Run Python health check
print_status "$BLUE" "Checking connector configurations..."
if ! python3 "$CONNECTORS_DIR/connector_manager.py" > /tmp/connector_list.txt 2>&1; then
    print_status "$RED" "Error checking connectors"
    cat /tmp/connector_list.txt
    FAILED=1
else
    cat /tmp/connector_list.txt
fi

echo ""
print_status "$BLUE" "Testing enabled connectors..."
echo ""

# Test LLM providers
print_status "$BLUE" "LLM Providers:"
if ! python3 -c "
from connector_manager import ConnectorManager
manager = ConnectorManager()
connectors = manager.list_connectors()
for provider in connectors.get('llm_providers', []):
    if manager.is_enabled('llm_providers', provider):
        try:
            result = manager.test_connector('llm_providers', provider)
            if result:
                print(f'  ✓ {provider}: OK')
            else:
                print(f'  ✗ {provider}: FAILED')
        except Exception as e:
            print(f'  ✗ {provider}: ERROR - {str(e)[:50]}')
" 2>&1; then
    FAILED=1
fi

echo ""

# Test exchanges
print_status "$BLUE" "Exchanges:"
if ! python3 -c "
from connector_manager import ConnectorManager
manager = ConnectorManager()
connectors = manager.list_connectors()
for exchange in connectors.get('exchanges', []):
    if manager.is_enabled('exchanges', exchange):
        try:
            result = manager.test_connector('exchanges', exchange)
            if result:
                print(f'  ✓ {exchange}: OK')
            else:
                print(f'  ✗ {exchange}: FAILED')
        except Exception as e:
            print(f'  ✗ {exchange}: ERROR - {str(e)[:50]}')
" 2>&1; then
    FAILED=1
fi

echo ""

# Test GitHub
print_status "$BLUE" "GitHub:"
if ! python3 -c "
from connector_manager import ConnectorManager
manager = ConnectorManager()
try:
    result = manager.test_connector('github', 'api')
    if result:
        print('  ✓ GitHub API: OK')
    else:
        print('  ✗ GitHub API: FAILED')
except Exception as e:
    print(f'  ✗ GitHub API: ERROR - {str(e)[:50]}')
" 2>&1; then
    FAILED=1
fi

echo ""

# Environment variable check
print_status "$BLUE" "Environment Variables Check:"
echo ""

# Check for required environment variables
REQUIRED_VARS=(
    "DEEPSEEK_API_KEY"
    "MISTRAL_API_KEY"
    "GITHUB_TOKEN"
)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        print_status "$YELLOW" "  ⚠ $var: NOT SET (may be needed)"
    else
        print_status "$GREEN" "  ✓ $var: SET"
    fi
done

# Check for optional environment variables
OPTIONAL_VARS=(
    "CLAUDE_API_KEY"
    "GROK_API_KEY"
    "YOBIT_API_KEY"
    "YOBIT_API_SECRET"
    "KUCOIN_API_KEY"
    "KUCOIN_API_SECRET"
    "JULES_API_KEY"
    "CODERABBIT_API_KEY"
    "GITHUB_WEBHOOK_SECRET"
)

for var in "${OPTIONAL_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        print_status "$YELLOW" "  ⚠ $var: NOT SET (optional)"
    else
        print_status "$GREEN" "  ✓ $var: SET"
    fi
done

echo ""
print_status "$BLUE" "Configuration Files Check:"
echo ""

# Check configuration files
CONFIG_FILES=(
    "llm_providers.yaml"
    "exchanges.yaml"
    "github.yaml"
    "webhooks.yaml"
    "connector_manager.py"
)

for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$CONNECTORS_DIR/$file" ]; then
        print_status "$GREEN" "  ✓ $file: EXISTS"
    else
        print_status "$RED" "  ✗ $file: MISSING"
    fi
done

echo ""

# Exit with failure if any check failed
if [ $FAILED -ne 0 ]; then
    print_status "$RED" "Health check completed with failures."
    exit 1
else
    print_status "$GREEN" "Health check complete."
    exit 0
fi
