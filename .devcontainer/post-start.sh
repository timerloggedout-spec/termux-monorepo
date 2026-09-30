#!/usr/bin/env bash
set -euo pipefail
# Bring up Hindsight slim in Docker. Idempotent.
if ! docker ps --format '{{.Names}}' | grep -q '^hindsight$'; then
  echo "[post-start] launching hindsight slim"
  docker run -d --name hindsight --restart unless-stopped \
    -p 8888:8888 \
    -v "$HOME/.hindsight/data:/home/hindsight/.pg0" \
    -e HINDSIGHT_API_LLM_PROVIDER="${HINDSIGHT_API_LLM_PROVIDER:-gemini}" \
    -e HINDSIGHT_API_LLM_API_KEY="${HINDSIGHT_API_LLM_API_KEY:-}" \
    -e HINDSIGHT_API_LLM_MODEL="${HINDSIGHT_API_LLM_MODEL:-gemini-2.0-flash}" \
    -e HINDSIGHT_API_LLM_GEMINI_SERVICE_TIER=on_demand \
    -e HINDSIGHT_API_FILE_PARSER=markitdown,iris \
    -e HINDSIGHT_API_FILE_PARSER_ALLOWLIST=markitdown,iris \
    ghcr.io/vectorize-io/hindsight:latest-slim
  sleep 6
fi
for i in 1 2 3 4 5 6 7 8 9 10; do
  if curl -fsS http://localhost:8888/health >/dev/null 2>&1; then
    echo "[post-start] hindsight healthy"
    curl -sS http://localhost:8888/health | head -c 200
    echo
    exit 0
  fi
  sleep 2
done
echo "[post-start] hindsight not ready; check: docker logs hindsight"
