#!/usr/bin/env bash
set -u
cd /tmp

echo "=== SOVEREIGN TICK: $(date -u +%FT%TZ) ==="

_active=$(python3 /tmp/hs-stack.py status 2>/dev/null | grep '^active:' | awk '{print $2}')
if [ -z "$_active" ]; then
  python3 /tmp/hs-stack.py rotate >/dev/null 2>&1
  _active=$(python3 /tmp/hs-stack.py status 2>/dev/null | grep '^active:' | awk '{print $2}')
fi
echo "  active model: ${_active:-<none>}"

# Propagate codespace secrets into the tick env
export HINDSIGHT_BASE_URL="${HINDSIGHT_BASE_URL:-http://localhost:8888}"
export HINDSIGHT_API_KEY="${HINDSIGHT_API_KEY:-}"
export HINDSIGHT_API_LLM_API_KEY="${HINDSIGHT_API_LLM_API_KEY:-${HINDSIGHT_API_KEY:-}}"
export HINDSIGHT_API_LLM_MODEL="${_active:-gemini-3.5-flash-lite}"
export HINDSIGHT_API_LLM_CACHE_AFFINITY="none"
export HINDSIGHT_API_LLM_PROMPT_CACHE_ENABLED="false"

echo "  key: $([ -n "${HINDSIGHT_API_KEY}" ] && echo SET || echo MISSING)"

_src_file=/tmp/sovereign-src.idx
_idx=$(cat "$_src_file" 2>/dev/null || echo 0)
_srcs=(fts5 conversations pointers codex)
_src="${_srcs[$((_idx % 4))]}"
echo "$(( _idx + 1 ))" > "$_src_file"
echo "  source this tick: $_src"

if [ -f /tmp/mvt-seed.py ]; then
  echo "  launching mvt-seed ($_src)..."
  SEED_SOURCE="$_src" python3 /tmp/mvt-seed.py 2>&1 | tail -15
  _rc=${PIPESTATUS[0]}
  echo "  seed batch rc=$_rc"
  if grep -q "ABORT lane" /tmp/mvt-seed.log 2>/dev/null; then
    echo "  lane aborted — rotating model"
    python3 /tmp/hs-stack.py rotate >/dev/null 2>&1
    _new=$(python3 /tmp/hs-stack.py status 2>/dev/null | grep '^active:' | awk '{print $2}')
    echo "  new active: $_new"
  fi
else
  echo "  no /tmp/mvt-seed.py"
fi
echo "=== TICK DONE ==="
