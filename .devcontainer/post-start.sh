#!/usr/bin/env bash
set -euo pipefail

# Ensure docker daemon up
if ! docker ps >/dev/null 2>&1; then
  echo "[post-start] starting docker daemon"
  sudo service docker start 2>&1 | tail -2 || \
    sudo /usr/local/share/docker-init.sh 2>&1 | tail -5 || true
  for i in $(seq 1 15); do
    docker ps >/dev/null 2>&1 && break
    sleep 2
  done
fi

if ! docker ps >/dev/null 2>&1; then
  echo "[post-start] docker daemon did not start"
  sudo journalctl -u docker 2>&1 | tail -10 || true
  exit 1
fi

# Hindsight
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

for i in $(seq 1 15); do
  if curl -fsS http://localhost:8888/health >/dev/null 2>&1; then
    echo "[post-start] hindsight healthy"
    curl -sS http://localhost:8888/health | head -c 200
    echo
    exit 0
  fi
  sleep 2
done

echo "[post-start] hindsight not ready; logs:"
docker logs hindsight 2>&1 | tail -20
