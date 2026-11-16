#!/data/data/com.termux/files/usr/bin/bash
# Publish this node's heartbeat to ops/devices/heartbeat/<device_id>.json on the
# `device-heartbeat` branch (never master; commit messages carry [skip ci]).
# Runs on ANY node (origin or secondary) as Termux job 43110 every 15 min.
# Payload: opaque device_id, battery, uptime, process flags. No hardware identifiers.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib.sh
. "$SCRIPT_DIR/lib.sh"
tmx_require_identity
tmx_have gh || tmx_die "gh is required"
tmx_have python || tmx_die "python is required"
mkdir -p "$TMX_STATE_DIR"

battery="$(tmx_battery_json)"
pinggy_proc=false; pgrep -f 'pinggy|manus-termux-reverse-ssh|ssh .*-R.*8022' >/dev/null 2>&1 && pinggy_proc=true
sshd_proc=false; pgrep -x sshd >/dev/null 2>&1 && sshd_proc=true
guard=false; [ -x "$HOME/.local/bin/git" ] && grep -q tmx-git-guard "$HOME/.local/bin/git" 2>/dev/null && guard=true
endpoint=""; log_mtime=""
if [ -r "$TERMUX_REVERSE_SSH_LOG" ]; then
  endpoint="$(awk '/^tcp:\/\// { v=$0; sub(/^tcp:\/\//,"",v); print v }' "$TERMUX_REVERSE_SSH_LOG" | tail -n 1)"
  log_mtime="$(date -u -d "@$(stat -c %Y "$TERMUX_REVERSE_SSH_LOG")" +%FT%TZ 2>/dev/null || true)"
fi

out="$TMX_STATE_DIR/heartbeat.json"
TMX_BATTERY_JSON="$battery" python - "$out" "$TERMUX_DEVICE_ID" "${TERMUX_DEVICE_ROLE:-observer}" "$pinggy_proc" "$sshd_proc" "$guard" "$endpoint" "$log_mtime" <<'PY'
import json, os, sys
from datetime import datetime, timezone
out, did, role, pp, sp, gd, ep, lm = sys.argv[1:9]
try: b = json.loads(os.environ.get("TMX_BATTERY_JSON") or "{}")
except Exception: b = {}
up = None
try: up = int(float(open("/proc/uptime").read().split()[0]))
except Exception: pass
d = {
  "schema_version": 1,
  "device_id": did,
  "device_role": role,
  "observed_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z"),
  "interval_minutes": 15,
  "battery": {k: b.get(k) for k in ("percentage","status","plugged","temperature","health")},
  "uptime_s": up,
  "processes": {"pinggy": pp == "true", "sshd": sp == "true"},
  "pinggy": {"last_endpoint": ep or None, "log_updated_at": lm or None},
  "git_guard": gd == "true",
  "note": "Opaque device_id only; fingerprints live in the age-sealed map (docs/ops/DEVICE-IDENTITY.md).",
}
json.dump(d, open(out, "w"), indent=2); open(out, "a").write("\n")
PY

if [ "${1:-}" = "--local-only" ]; then cat "$out"; exit 0; fi
tmx_ensure_branch "$TMX_HEARTBEAT_BRANCH" || { tmx_log "cannot reach GitHub; heartbeat kept locally"; exit 0; }
tmx_gh_put_file "$TMX_HEARTBEAT_DIR/$TERMUX_DEVICE_ID.json" "$TMX_HEARTBEAT_BRANCH" "$out" \
  "ops(devices): heartbeat $TERMUX_DEVICE_ID [skip ci]" \
  || { tmx_log "heartbeat publish failed; kept locally"; exit 0; }
tmx_log "heartbeat published for $TERMUX_DEVICE_ID"
