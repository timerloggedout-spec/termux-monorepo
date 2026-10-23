#!/usr/bin/env bash
# Tier-1 engine proof — EVIDENCE collector, not a benchmark assertion.
# For each engine binary in $PROOF_BIN_DIR: capture --help, start its CDP
# serve mode against a local fixture page, poll the CDP HTTP surface,
# sample peak RSS (VmHWM), and emit one JSON object per engine.
# Usage: run_proof.sh <bin_dir> <fixture_url> <out.json>
set -u
BIN_DIR="${1:?bin dir}"; FIXTURE_URL="${2:?fixture url}"; OUT="${3:?out json}"
MEM_CAP_MB="${MEM_CAP_MB:-512}"
mkdir -p "$(dirname "$OUT")"

json_escape() { python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))"; }

probe_engine() {
  local name="$1" bin="$2" port="$3"
  local work; work="$(mktemp -d)"
  local result="{}"
  [ -x "$bin" ] || { echo "{\"engine\":\"$name\",\"binary_ok\":false,\"error\":\"missing binary\"}"; return; }
  "$bin" --help >"$work/help.txt" 2>&1 || "$bin" help >"$work/help.txt" 2>&1 || true
  local help_head; help_head="$(head -c 600 "$work/help.txt" | json_escape)"
  # Try the documented serve shapes in order; first that answers /json/version wins.
  local serve_pid=""
  for args in "serve --host 127.0.0.1 --port $port" "serve --port $port" "--port $port" "serve -p $port"; do
    # shellcheck disable=SC2086
    ( ulimit -v $((MEM_CAP_MB * 1024)) 2>/dev/null; exec "$bin" $args ) >"$work/serve.log" 2>&1 &
    serve_pid=$!
    for _ in $(seq 1 20); do
      sleep 0.5
      if curl -sf "http://127.0.0.1:$port/json/version" >"$work/version.json" 2>/dev/null; then break 2; fi
      kill -0 "$serve_pid" 2>/dev/null || break
    done
    kill "$serve_pid" 2>/dev/null; wait "$serve_pid" 2>/dev/null; serve_pid=""
  done
  local version_json="null" cdp_ok="false" vmhwm="null" new_tab="null"
  if [ -s "$work/version.json" ]; then
    cdp_ok="true"; version_json="$(cat "$work/version.json")"
    # Ask CDP HTTP to open the fixture (works on Chromium-shaped surfaces;
    # recorded either way — a refusal is evidence too).
    curl -sf "http://127.0.0.1:$port/json/new?$FIXTURE_URL" >"$work/new.json" 2>/dev/null \
      && new_tab="$(cat "$work/new.json" | head -c 400 | json_escape)" || new_tab="\"refused-or-unsupported\""
    sleep 2
    # Restart-free RSS sample: relaunch is costly; VmHWM of serve pid if alive.
    if [ -n "$serve_pid" ] && kill -0 "$serve_pid" 2>/dev/null; then
      vmhwm="$(awk '/VmHWM/{print $2}' /proc/"$serve_pid"/status 2>/dev/null || echo null)"
    fi
  fi
  [ -n "$serve_pid" ] && { kill "$serve_pid" 2>/dev/null; wait "$serve_pid" 2>/dev/null; }
  local serve_log; serve_log="$(tail -c 800 "$work/serve.log" 2>/dev/null | json_escape)"
  cat <<EOF
{"engine":"$name","binary_ok":true,"arch":"$(uname -m)","mem_cap_mb":$MEM_CAP_MB,
 "cdp_answered":$cdp_ok,"cdp_version":$version_json,"new_tab":$new_tab,
 "serve_peak_rss_kb":$vmhwm,"help_head":$help_head,"serve_log_tail":$serve_log}
EOF
  rm -rf "$work"
}

{
  echo "["
  first=1
  for entry in "obscura:9331" "lightpanda:9332"; do
    name="${entry%%:*}"; port="${entry##*:}"
    bin="$(find "$BIN_DIR" -maxdepth 3 -type f -name "$name*" -perm -u+x 2>/dev/null | head -1)"
    [ $first -eq 0 ] && echo ","
    first=0
    if [ -n "$bin" ]; then probe_engine "$name" "$bin" "$port"; else echo "{\"engine\":\"$name\",\"binary_ok\":false,\"error\":\"not downloaded\"}"; fi
  done
  echo "]"
} > "$OUT"
cat "$OUT"
