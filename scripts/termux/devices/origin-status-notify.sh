#!/data/data/com.termux/files/usr/bin/bash
# Cross-device status notification (runs on the SECONDARY node as Termux job 43111).
# Reads the origin's heartbeat (device-heartbeat branch) and the Pinggy bridge manifest
# (master: ops/termux-bridge/current.json), TCP-probes the tunnel, and posts:
#   id 43111  ongoing status card  (Refresh / Copy SSH / Mute 2h buttons)
#   id 43112  high-priority alert, only on a transition into DEGRADED/DOWN; cleared on recovery
#
#   origin-status-notify.sh            # normal run
#   origin-status-notify.sh --mute 120 # silence alerts for N minutes (status card still updates)
#   origin-status-notify.sh --print    # print computed state, no notification
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib.sh
. "$SCRIPT_DIR/lib.sh"
mkdir -p "$TMX_STATE_DIR"
MUTE_FILE="$TMX_STATE_DIR/origin-alert-mute-until"
LAST_FILE="$TMX_STATE_DIR/origin-last-state"
STALE_MIN="${TMX_ORIGIN_STALE_MINUTES:-45}"
LOW_BATT="${TMX_ORIGIN_LOW_BATTERY:-20}"
HOT_C="${TMX_ORIGIN_HOT_CELSIUS:-45}"

if [ "${1:-}" = "--mute" ]; then
  echo $(( $(date +%s) + ${2:-120} * 60 )) >"$MUTE_FILE"
  tmx_have termux-toast && termux-toast "Origin alerts muted ${2:-120} min" || true
  exit 0
fi

hb="$(tmx_gh_get_file "$TMX_HEARTBEAT_DIR/$TMX_ORIGIN_DEVICE_ID.json" "$TMX_HEARTBEAT_BRANCH" 2>/dev/null || true)"
mf="$(tmx_gh_get_file "$TMX_BRIDGE_MANIFEST" "$TMX_MASTER_BRANCH" 2>/dev/null || true)"
gh_ok=1; [ -n "$hb$mf" ] || gh_ok=0
self_batt="$(tmx_battery_json)"

state="$(TMX_HB="$hb" TMX_MF="$mf" TMX_SELF="$self_batt" python - "$STALE_MIN" "$LOW_BATT" "$HOT_C" "$gh_ok" "$TMX_ORIGIN_DEVICE_ID" <<'PY'
import json, os, socket, sys
from datetime import datetime, timezone
stale_min, low, hot, gh_ok, origin = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), sys.argv[4] == "1", sys.argv[5]
now = datetime.now(timezone.utc)
def load(k):
    try: return json.loads(os.environ.get(k) or "null")
    except Exception: return None
def ts(s):
    try: return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception: return None
def ago(dt):
    m = int((now - dt).total_seconds() // 60)
    return f"{m}m" if m < 120 else f"{m//60}h{m%60:02d}m"
hb, mf, me = load("TMX_HB"), load("TMX_MF"), load("TMX_SELF") or {}
level, issues = "OK", []
def worse(l):
    global level
    order = ["OK", "DEGRADED", "DOWN"]
    if order.index(l) > order.index(level): level = l

# Heartbeat / battery
hb_txt, batt_txt = "no heartbeat", "batt ?"
if not gh_ok:
    level = "UNKNOWN"; issues.append("GitHub unreachable from this phone")
elif not hb:
    worse("DOWN"); issues.append("origin has never published a heartbeat")
else:
    t = ts(hb.get("observed_at") or "")
    if not t: worse("DOWN"); issues.append("heartbeat unreadable")
    else:
        hb_txt = f"hb {ago(t)} ago"
        if (now - t).total_seconds() > stale_min * 60:
            worse("DOWN"); issues.append(f"heartbeat stale ({ago(t)})")
    b = hb.get("battery") or {}
    p, st = b.get("percentage"), (b.get("status") or "").upper()
    if p is not None:
        batt_txt = f"{p}%" + (" ⚡" if st in ("CHARGING", "FULL") else "")
        if p < low and st not in ("CHARGING", "FULL"):
            worse("DEGRADED"); issues.append(f"origin battery {p}% not charging")
    tc = b.get("temperature")
    if isinstance(tc, (int, float)) and tc >= hot:
        worse("DEGRADED"); issues.append(f"origin hot {tc:.0f}°C")
    if (hb.get("processes") or {}).get("pinggy") is False:
        worse("DEGRADED"); issues.append("pinggy process not running")

# Pinggy tunnel (manifest + live probe)
tun_txt, ssh_cmd = "tunnel ?", ""
if mf and gh_ok:
    st = mf.get("status") or "unknown"
    host, port, user = mf.get("endpoint"), mf.get("port"), mf.get("ssh_user")
    exp = ts(mf.get("expires_at") or "")
    if exp and exp < now:
        st = "expired"
    if mf.get("device_id") not in (None, origin):
        worse("DEGRADED"); issues.append(f"bridge manifest claimed by {mf.get('device_id')}, not origin")
    probe = None
    if host and port:
        try:
            with socket.create_connection((host, int(port)), timeout=5): probe = True
        except OSError: probe = False
        ssh_cmd = f"ssh -p {port} {user or '$USER'}@{host}"
    tun_txt = f"tunnel {st}" + ("" if probe is None else (" ✓" if probe else " ✗probe"))
    if probe is False or st in ("stale", "expired"):
        worse("DEGRADED"); issues.append(f"tunnel {st}, probe {'ok' if probe else 'failed'}")
    elif st == "unknown" and probe is not True:
        worse("DEGRADED"); issues.append("tunnel state unknown (publisher not refreshing)")

me_txt = f"this phone {me.get('percentage','?')}%"
print(json.dumps({"level": level, "title": f"Origin {level}",
  "content": " · ".join([batt_txt, tun_txt, hb_txt]) + f"  |  {me_txt}",
  "issues": issues, "ssh": ssh_cmd}))
PY
)"

if [ "${1:-}" = "--print" ]; then printf '%s\n' "$state"; exit 0; fi
j() { printf '%s' "$state" | python -c "import json,sys;v=json.load(sys.stdin).get('$1');print(' ; '.join(v) if isinstance(v,list) else (v or ''))"; }
level="$(j level)"; title="$(j title)"; content="$(j content)"; issues="$(j issues)"; ssh_cmd="$(j ssh)"
tmx_have termux-notification || { echo "$title: $content ${issues:+($issues)}"; exit 0; }

self="$SCRIPT_DIR/origin-status-notify.sh"
icon=check_circle; [ "$level" = DEGRADED ] && icon=warning; [ "$level" = DOWN ] && icon=error; [ "$level" = UNKNOWN ] && icon=help
nargs=(--id "$TMX_NOTIFY_STATUS_ID" --group tmx-origin --ongoing --alert-once --priority low --icon "$icon"
  --title "$title" --content "$content${issues:+ — $issues}"
  --button1 "Refresh" --button1-action "bash '$self'"
  --button3 "Mute 2h" --button3-action "bash '$self' --mute 120")
[ -z "$ssh_cmd" ] || nargs+=(--button2 "Copy SSH" --button2-action "termux-clipboard-set '$ssh_cmd'; termux-toast 'SSH command copied'")
termux-notification "${nargs[@]}"

last="$(cat "$LAST_FILE" 2>/dev/null || echo OK)"; printf '%s' "$level" >"$LAST_FILE"
muted=0; [ -r "$MUTE_FILE" ] && [ "$(cat "$MUTE_FILE")" -gt "$(date +%s)" ] 2>/dev/null && muted=1
case "$level" in
  DEGRADED|DOWN)
    if [ "$level" != "$last" ] && [ "$muted" = 0 ]; then
      termux-notification --id "$TMX_NOTIFY_ALERT_ID" --group tmx-origin --priority high \
        --vibrate 300,150,300 --led-color FF3B30 --sound --icon "$icon" \
        --title "⚠ Origin phone $level" --content "${issues:-$content}" \
        --button1 "Refresh" --button1-action "bash '$self'"
    fi ;;
  OK) [ "$last" = OK ] || termux-notification-remove "$TMX_NOTIFY_ALERT_ID" 2>/dev/null || true ;;
esac

# Observer|controller 🎮 nodes also refresh the control pane (id 43114) in the same group.
if [ "${TERMUX_DEVICE_ROLE:-}" = observer-controller ]; then bash "$SCRIPT_DIR/controller-panel.sh" draw || true; fi
