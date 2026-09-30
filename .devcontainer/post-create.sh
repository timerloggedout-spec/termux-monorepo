#!/usr/bin/env bash
set -euo pipefail
echo "[post-create] installing toolchain"
pip install --quiet --upgrade pip
pip install --quiet ruff httpx pytest
curl -sSL "https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz" \
  | sudo tar -xz -C /usr/local/bin gitleaks
sudo chmod +x /usr/local/bin/gitleaks
gitleaks version

# Pre-seed hindsight api config (values filled from env secrets)
mkdir -p ~/.hindsight
cat > ~/.hindsight/env <<'HEOF'
HINDSIGHT_API_LLM_PROVIDER=${HINDSIGHT_API_LLM_PROVIDER:-gemini}
HINDSIGHT_API_LLM_MODEL=${HINDSIGHT_API_LLM_MODEL:-gemini-2.0-flash}
HINDSIGHT_API_LLM_GEMINI_SERVICE_TIER=on_demand
HINDSIGHT_API_FILE_PARSER=markitdown,iris
HINDSIGHT_API_FILE_PARSER_ALLOWLIST=markitdown,iris
HINDSIGHT_API_PORT=8888
HEOF
chmod 600 ~/.hindsight/env

echo "[post-create] done"
