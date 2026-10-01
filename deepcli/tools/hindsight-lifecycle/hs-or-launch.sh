#!/usr/bin/env bash
set -u
_main=$(pgrep -f 'hindsight-api --port 8888' | head -1)
[ -z "$_main" ] && { echo "no :8888 api"; exit 1; }

# Source entire HINDSIGHT_* env from the live primary (embeddings, reranker, parser, tier)
while IFS='=' read -r _k _v; do
  case "$_k" in
    HINDSIGHT_*) export "$_k=$_v" ;;
  esac
done < <(tr '\0' '\n' < /proc/$_main/environ)

# Override only the LLM + port + worker
export HINDSIGHT_API_LLM_PROVIDER="openrouter"
export HINDSIGHT_API_LLM_MODEL="meta-llama/llama-3.3-70b-instruct:free"
export HINDSIGHT_API_LLM_API_KEY=$(tr '\0' '\n' < /proc/$_main/environ | grep '^OPENROUTER_API_KEY=' | cut -d= -f2-)
export HINDSIGHT_API_WORKER_ID="hindsight-openrouter"
export HINDSIGHT_API_PORT=8889
export HINDSIGHT_API_HOST=0.0.0.0

echo "or_key_len=${#HINDSIGHT_API_LLM_API_KEY}  or_model=$HINDSIGHT_API_LLM_MODEL"
echo "embed_provider=$HINDSIGHT_API_EMBEDDINGS_PROVIDER  embed_model=$HINDSIGHT_API_EMBEDDINGS_MODEL"

pkill -9 -f 'hindsight-api --port 8889' 2>/dev/null || true
sleep 1
setsid nohup bash -c 'cd ~/hindsight && . .venv/bin/activate && exec hindsight-api --port 8889 --host 0.0.0.0' \
  > /tmp/hs-or.log 2>&1 < /dev/null &
for i in $(seq 1 30); do sleep 2; c=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 3 http://localhost:8889/health 2>/dev/null || echo 000); [ "$c" = "200" ] && break; done
echo "or_health=$c  or_pid=$(pgrep -f 'hindsight-api --port 8889' | head -1)"
tail -4 /tmp/hs-or.log 2>/dev/null
