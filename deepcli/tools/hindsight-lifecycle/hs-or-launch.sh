#!/usr/bin/env bash
set -u
_main=$(pgrep -f 'hindsight-api --port 8888' | head -1)
[ -z "$_main" ] && { echo "no :8888 api"; exit 1; }

# Capture the Gemini key BEFORE we override LLM_API_KEY
_gem=$(tr '\0' '\n' < /proc/$_main/environ | grep '^HINDSIGHT_API_LLM_API_KEY=' | cut -d= -f2-)

# Inherit all HINDSIGHT_* from primary
while IFS='=' read -r _k _v; do
  case "$_k" in HINDSIGHT_*) export "$_k=$_v" ;; esac
done < <(tr '\0' '\n' < /proc/$_main/environ)

# Pin embeddings to the Gemini key so embeddings don't pick up the OR key
export HINDSIGHT_API_EMBEDDINGS_GEMINI_API_KEY="$_gem"
export HINDSIGHT_API_EMBEDDINGS_API_KEY="$_gem"

# Override LLM to OpenRouter
export HINDSIGHT_API_LLM_PROVIDER="openrouter"
export HINDSIGHT_API_LLM_MODEL="qwen/qwen3.8-27b:free"
export HINDSIGHT_API_LLM_API_KEY=$(tr '\0' '\n' < /proc/$_main/environ | grep '^OPENROUTER_API_KEY=' | cut -d= -f2-)
export HINDSIGHT_API_WORKER_ID="hindsight-openrouter"
export HINDSIGHT_API_PORT=8889
export HINDSIGHT_API_HOST=0.0.0.0

echo "llm_key_len=${#HINDSIGHT_API_LLM_API_KEY}  embed_gem_len=${#HINDSIGHT_API_EMBEDDINGS_GEMINI_API_KEY}"

pkill -9 -f 'hindsight-api --port 8889' 2>/dev/null || true
sleep 1
setsid nohup bash -c 'cd ~/hindsight && . .venv/bin/activate && exec hindsight-api --port 8889 --host 0.0.0.0' \
  > /tmp/hs-or.log 2>&1 < /dev/null &
for i in $(seq 1 30); do sleep 2; c=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 3 http://localhost:8889/health 2>/dev/null || echo 000); [ "$c" = "200" ] && break; done
echo "or_health=$c  or_pid=$(pgrep -f 'hindsight-api --port 8889' | head -1)"
tail -4 /tmp/hs-or.log 2>/dev/null
