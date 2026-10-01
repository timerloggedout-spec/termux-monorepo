#!/usr/bin/env bash
# sovereign-run.sh — one orchestration tick.
# Reads rotator active model, runs one mvt-seed source batch.
set -u
cd /tmp

echo "=== SOVEREIGN TICK: $(date -u +%FT%TZ) ==="

_active=$(python3 /tmp/hs-stack.py status 2>/dev/null | grep '^active:' | awk '{print $2}')
if [ -z "$_active" ]; then
  echo "  no active model, forcing rotate..."
  python3 /tmp/hs-stack.py rotate >/dev/null 2>&1
  _active=$(python3 /tmp/hs-stack.py status 2>/dev/null | grep '^active:' | awk '{print $2}')
fi
echo "  active model: ${_active:-<none>}"

export HINDSIGHT_BASE_URL="${HINDSIGHT_BASE_URL:-http://localhost:8888}"
export HINDSIGHT_API_LLM_MODEL="${_active:-gemini-3.5-flash-lite}"
export HINDSIGHT_API_LLM_CACHE_AFFINITY="none"
export HINDSIGHT_API_LLM_PROMPT_CACHE_ENABLED="false"

# Rotate source each tick to spread load
_src_file=/tmp/sovereign-src.idx
_idx=$(cat "$_src_file" 2>/dev/null || echo 0)
_srcs=(fts5 conversations pointers codex)
_src="${_srcs[$((_idx % 4))]}"
echo "$(( _idx + 1 ))" > "$_src_file"
echo "  source this tick: $_src"

if [ -f /tmp/mvt-seed.py ]; then
  echo "  launching mvt-seed ($_src)..."
  SEED_SOURCE="$_src" timeout 240 python3 /tmp/mvt-seed.py 2>&1 | tail -8
  _rc=${PIPESTATUS[0]}
  if [ "$_rc" -eq 0 ]; then
    echo "  seed batch OK"
  else
    echo "  seed batch rc=$_rc — next tick may rotate"
  fi
else
  echo "  no /tmp/mvt-seed.py — skip"
fi

echo "=== TICK DONE ==="
