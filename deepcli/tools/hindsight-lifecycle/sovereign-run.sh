#!/usr/bin/env bash
set -u
cd /tmp

echo "=== SOVEREIGN TICK: $(date -u +%FT%TZ) ==="
# purge stale termux-monorepo::primary if it reappears
if [ -f /tmp/purge-stale.sql ]; then
  _n=$(bash /tmp/hs-db-runner.sh /tmp/purge-stale.sql 2>/dev/null | tail -1)
  [ -n "$_n" ] && echo "  stale purge: $_n"
fi

# self-heal rotator state
mkdir -p /tmp/hs-stack
if [ ! -f /tmp/hs-stack/active.json ]; then
  echo '{"model":"gemini-3.1-flash-lite","ts":"auto-init"}' > /tmp/hs-stack/active.json
  echo "  created /tmp/hs-stack/active.json"
fi

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


# Auto-drain every 6 hours (configurable via HS_DRAIN_INTERVAL_S)
if [ -f /tmp/hs-drain-auto.sh ]; then
  _last_drain_file=/tmp/hs-last-drain.ts
  _now=$(date +%s)
  _last=$(cat "$_last_drain_file" 2>/dev/null || echo 0)
  _interval="${HS_DRAIN_INTERVAL_S:-21600}"
  if [ $(( _now - _last )) -ge "$_interval" ]; then
    echo "  auto-drain (interval=${_interval}s since last=${_last})"
    bash /tmp/hs-drain-auto.sh >> /tmp/hs-drain.log 2>&1
    echo "$_now" > "$_last_drain_file"
  fi
fi

# Dynamic batch size from model token limits
if [ -f /tmp/hs-batch-plan.py ]; then
  _bs=$(python3 /tmp/hs-batch-plan.py 2>/dev/null || echo 8)
  export MVT_BATCH_SIZE="$_bs"
  echo "  dynamic batch_size=$_bs"
fi

if [ -f /tmp/mvt-seed.py ]; then
  echo "  launching mvt-seed ($_src)..."
  SEED_SOURCE="$_src" python3 /tmp/mvt-seed.py 2>&1 | tail -15
  _rc=${PIPESTATUS[0]}
  echo "  seed batch rc=$_rc"
  # Count how many 200s this batch produced and bump the model counter
  _ok=$(grep -oE 'batch #[0-9]+ -> HTTP 200' /tmp/mvt-seed.log 2>/dev/null | wc -l)
  if [ "${_ok:-0}" -gt 0 ] && [ -n "${_active:-}" ]; then
    python3 -c "
import sys; sys.path.insert(0,'/tmp')
try:
    from hs_stack import _bump
except Exception:
    from hs_stack import _bump
" 2>/dev/null || true
    # fallback: direct json bump
    python3 - <<PYBUMP
import json, os
from datetime import datetime, timezone, timedelta
today = (datetime.now(timezone.utc) - timedelta(hours=8)).strftime("%Y-%m-%d")
sp = "/tmp/hs-stack/state.json"
st = {}
if os.path.exists(sp):
    try: st = json.load(open(sp))
    except Exception: st = {}
st.setdefault("${_active}", {})
st["${_active}"][today] = st["${_active}"].get(today, 0) + ${_ok}
json.dump(st, open(sp, "w"), indent=2)
PYBUMP
  fi
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
