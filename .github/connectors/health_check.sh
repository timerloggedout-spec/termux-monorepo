#!/bin/bash
# Connector Health Check Script
# Checks the status of all configured connectors
# Exit 0 only when config files exist and enabled-connector tests succeed.
# Live network tests skip when required credentials are unset (SKIPPED, not FAIL).

set -e

echo "=========================================="
echo "Connector Health Check"
echo "=========================================="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

FAILED=0

print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

if ! command -v python3 &> /dev/null; then
    print_status "$RED" "Error: python3 is not installed"
    exit 1
fi

CONNECTORS_DIR="$(dirname "$0")"
if [ ! -d "$CONNECTORS_DIR" ]; then
    print_status "$RED" "Error: Connectors directory not found: $CONNECTORS_DIR"
    exit 1
fi

export PYTHONPATH="$CONNECTORS_DIR:${PYTHONPATH:-}"

print_status "$BLUE" "Checking connector configurations..."
CONNECTOR_LIST_FILE="$(mktemp)"
trap 'rm -f "$CONNECTOR_LIST_FILE"' EXIT

if ! python3 "$CONNECTORS_DIR/connector_manager.py" > "$CONNECTOR_LIST_FILE" 2>&1; then
    print_status "$RED" "Error checking connectors"
    cat "$CONNECTOR_LIST_FILE"
    FAILED=1
else
    cat "$CONNECTOR_LIST_FILE"
fi

echo ""
print_status "$BLUE" "Testing enabled connectors (skip when credentials unset)..."
echo ""

run_connector_tests() {
    local label=$1
    local py=$2
    print_status "$BLUE" "$label:"
    if ! python3 -c "$py"; then
        FAILED=1
    fi
    echo ""
}

run_connector_tests "LLM Providers" '
from connector_manager import ConnectorManager
import os, sys
manager = ConnectorManager()
connectors = manager.list_connectors()
failed = False
for provider in connectors.get("llm_providers", []):
    if not manager.is_enabled("llm_providers", provider):
        continue
    cfg = manager.get_connector("llm_providers", provider) or {}
    key_env = cfg.get("api_key_env") or f"{provider.upper()}_API_KEY"
    if not os.environ.get(key_env):
        print(f"  ⊘ {provider}: SKIPPED (no {key_env})")
        continue
    try:
        result = manager.test_connector("llm_providers", provider)
        if result:
            print(f"  ✓ {provider}: OK")
        else:
            print(f"  ✗ {provider}: FAILED")
            failed = True
    except Exception as e:
        print(f"  ✗ {provider}: ERROR - {type(e).__name__}")
        failed = True
sys.exit(1 if failed else 0)
'

run_connector_tests "GitHub" '
from connector_manager import ConnectorManager
import os, sys
manager = ConnectorManager()
failed = False
cfg = manager.get_connector("github", "api") or {}
token_env = cfg.get("token_env") or "GITHUB_TOKEN"
if not os.environ.get(token_env):
    print(f"  ⊘ GitHub API: SKIPPED (no {token_env})")
else:
    try:
        result = manager.test_connector("github", "api")
        if result:
            print("  ✓ GitHub API: OK")
        else:
            print("  ✗ GitHub API: FAILED")
            failed = True
    except Exception as e:
        print(f"  ✗ GitHub API: ERROR - {type(e).__name__}")
        failed = True
sys.exit(1 if failed else 0)
'

print_status "$BLUE" "Environment Variables Check:"
echo ""

REQUIRED_VARS=("DEEPSEEK_API_KEY" "MISTRAL_API_KEY" "GITHUB_TOKEN")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        print_status "$YELLOW" "  ⚠ $var: NOT SET (may be needed)"
    else
        print_status "$GREEN" "  ✓ $var: SET"
    fi
done

OPTIONAL_VARS=(
    "CLAUDE_API_KEY" "GROK_API_KEY"
    "JULES_API_KEY" "CODERABBIT_API_KEY" "GITHUB_WEBHOOK_SECRET"
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

CONFIG_FILES=(
    "llm_providers.yaml"
    "github.yaml"
    "webhooks.yaml"
    "connector_manager.py"
)

for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$CONNECTORS_DIR/$file" ]; then
        print_status "$GREEN" "  ✓ $file: EXISTS"
    else
        print_status "$RED" "  ✗ $file: MISSING"
        FAILED=1
    fi
done

echo ""

if [ $FAILED -ne 0 ]; then
    print_status "$RED" "Health check completed with failures."
    exit 1
else
    print_status "$GREEN" "Health check complete."
    exit 0
fi
