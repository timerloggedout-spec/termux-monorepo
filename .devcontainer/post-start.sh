#!/usr/bin/env bash
set -euo pipefail
cd "$HOME/hindsight" 2>/dev/null || exit 0
[ -d .venv ] || exit 0
. .venv/bin/activate
command -v hindsight-api >/dev/null 2>&1 || exit 0
pgrep -f hindsight-api >/dev/null 2>&1 && exit 0

export HINDSIGHT_API_WORKER_ID=hindsight-termux-monorepo
export HINDSIGHT_API_LLM_PROVIDER=gemini
export HINDSIGHT_API_LLM_MODEL=gemini-3.8-flash
export HINDSIGHT_API_LLM_GEMINI_SERVICE_TIER=flex
export HINDSIGHT_API_EMBEDDINGS_PROVIDER=google
export HINDSIGHT_API_EMBEDDINGS_MODEL=gemini-embedding-001
export HINDSIGHT_API_RERANKER_PROVIDER=rrf
export HINDSIGHT_API_RERANKER_REQUIRED=false
export HINDSIGHT_API_FILE_PARSER=markitdown
export HINDSIGHT_API_PORT=8888
export HINDSIGHT_API_HOST=0.0.0.0

nohup hindsight-api --port 8888 --host 0.0.0.0 > /tmp/hs.log 2>&1 &
for i in $(seq 1 30); do sleep 3; curl -fsS http://localhost:8888/health >/dev/null 2>&1 && break; done
curl -fsS http://localhost:8888/health 2>/dev/null | head -c 200 || true
