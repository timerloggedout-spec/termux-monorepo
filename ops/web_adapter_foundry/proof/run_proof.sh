#!/usr/bin/env bash
# Tier-1 engine proof v2 — EVIDENCE collector, not a benchmark assertion.
#
# Round-1 lessons baked in (run 39908222462, diagnosed locally before this
# rewrite): (1) binary discovery must match the EXACT binary name — a glob
# picked up obscura.tar.gz / obscura-worker; (2) NO `ulimit -v` cap: V8 and
# Zig reserve large virtual address space at startup, so a 512 MB VA cap
# silently prevented serve from answering — the honest B160V metric is
# measured resident memory (VmHWM), sampled idle and after navigation.
#
# Usage: run_proof.sh <bin_dir> <fixture_url> <out.json>
set -u
BIN_DIR="${1:?bin dir}"; FIXTURE_URL="${2:?fixture url}"; OUT="${3:?out json}"
mkdir -p "$(dirname "$OUT")"

json_escape() { python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))"; }
hwm() { awk '/VmHWM/{print $2}' /proc/"$1"/status 2>/dev/null || echo null; }

probe_engine() {
  local name="$1" bin="$2" port="$3"; shift 3
  local serve_args=("$@")
  local work; work="$(mktemp -d)"
  [ -x "$bin" ] || { echo "{\"engine\":\"$name\",\"binary_ok\":false,\"error\":\"binary not found: $bin\"}"; return; }
  "$bin" --help >"$work/help.txt" 2>&1 || true
  local help_head; help_head="$(head -c 400 "$work/help.txt" | json_escape)"
  "$bin" serve "${serve_args[@]}" --host 127.0.0.1 --port "$port" >"$work/serve.log" 2>&1 &
  local pid=$!
  local version_json="null" cdp_ok="false"
  for _ in $(seq 1 40); do
    sleep 0.5
    if curl -sf "http://127.0.0.1:$port/json/version" >"$work/version.json" 2>/dev/null; then
      cdp_ok="true"; version_json="$(cat "$work/version.json")"; break
    fi
    kill -0 "$pid" 2>/dev/null || break
  done
  local rss_idle="null" rss_nav="null" new_tab="null"
  if [ "$cdp_ok" = "true" ]; then
    sleep 1; rss_idle="$(hwm "$pid")"
    if curl -sf "http://127.0.0.1:$port/json/new?$FIXTURE_URL" >"$work/new.json" 2>/dev/null; then
      new_tab="$(head -c 300 "$work/new.json" | json_escape)"
    else
      new_tab="\"refused-or-unsupported\""
    fi
    sleep 2; rss_nav="$(hwm "$pid")"
  fi
  kill "$pid" 2>/dev/null; wait "$pid" 2>/dev/null
  local serve_log; serve_log="$(tail -c 500 "$work/serve.log" 2>/dev/null | json_escape)"
  cat <<EOF
{"engine":"$name","binary_ok":true,"arch":"$(uname -m)","cdp_answered":$cdp_ok,
 "cdp_version":$version_json,"new_tab":$new_tab,
 "serve_rss_idle_kb":$rss_idle,"serve_rss_after_nav_kb":$rss_nav,
 "help_head":$help_head,"serve_log_tail":$serve_log}
EOF
  rm -rf "$work"
}

OBSCURA_BIN="$(find "$BIN_DIR" -maxdepth 3 -type f -name obscura -perm -u+x 2>/dev/null | head -1)"
LIGHTPANDA_BIN="$(find "$BIN_DIR" -maxdepth 3 -type f -name lightpanda -perm -u+x 2>/dev/null | head -1)"

{
  echo "["
  # Obscura blocks private-network fetches by default (SSRF guard); the
  # fixture is loopback, so the proof explicitly opts in.
  probe_engine obscura "${OBSCURA_BIN:-$BIN_DIR/obscura}" 9331 --allow-private-network
  echo ","
  probe_engine lightpanda "${LIGHTPANDA_BIN:-$BIN_DIR/lightpanda}" 9332
  echo "]"
} > "$OUT"
cat "$OUT"
