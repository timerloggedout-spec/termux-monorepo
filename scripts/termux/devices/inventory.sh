#!/data/data/com.termux/files/usr/bin/bash
# Read-only inventory of THIS phone. Run first on any node before provisioning (RECON).
# Writes $TMX_STATE_DIR/inventory.json locally. Never publishes: the file can hold a
# Termux version + app list, but NO serial/IMEI/MAC/build fingerprint (those go only
# into the age-sealed map, see DEVICE-IDENTITY.md).
#   inventory.sh            # write + print summary
#   inventory.sh --json     # print JSON only
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib.sh
. "$SCRIPT_DIR/lib.sh"
mkdir -p "$TMX_STATE_DIR"; out="$TMX_STATE_DIR/inventory.json"

pkgs="$( (pm list packages 2>/dev/null || cmd package list packages 2>/dev/null) | sed 's/^package://' | sort -u)"
want='com.termux com.termux.api com.termux.boot com.termux.widget com.termux.styling com.termux.window
moe.shizuku.privileged.api com.android.shell.plus
eu.sisik.hackendebug
com.tailscale.ipn com.wireguard.android org.zerotier.one
com.foxdebug.acode'
apps_json="$(python - "$pkgs" "$want" <<'PY'
import json,sys
have=set(sys.argv[1].split()); want=sys.argv[2].split()
shiz=sorted(p for p in have if "shizuku" in p.lower())
print(json.dumps({"checked":{p:(p in have) for p in want},"shizuku_like":shiz,"listable":bool(have)}))
PY
)"
tools=""; for t in git gh ssh sshd python jq age curl adb rish termux-notification termux-job-scheduler termux-clipboard-set pinggy; do
  tmx_have "$t" && tools+="$t "; done
free_kb="$(df -k "$HOME" 2>/dev/null | awk 'NR==2{print $4}')"
python - "$out" "$apps_json" "$tools" "${TERMUX_VERSION:-unknown}" "$(getprop ro.build.version.release 2>/dev/null)" \
  "$(getprop ro.build.version.sdk 2>/dev/null)" "${free_kb:-0}" "$(uname -m)" "${TERMUX_DEVICE_ID:-uninitialised}" "${TERMUX_DEVICE_ROLE:-}" <<'PY'
import json,sys,datetime
o,apps,tools,tv,rel,sdk,free,arch,did,role=sys.argv[1:]
d={"schema":"tmx-inventory/1","device_id":did,"role":role,"generated_at":datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
   "termux_version":tv,"android_release":rel,"android_sdk":sdk,"arch":arch,"home_free_mb":int(free or 0)//1024,
   "tools":tools.split(),"apps":json.loads(apps),
   "notes":["Shizuku present => rish can run pm/settings/cmd as shell uid (no ADB host needed after pairing)",
            "Check termux_version on BOTH nodes; scripts target the newer one and stay POSIX-bash on the older"]}
open(o,"w").write(json.dumps(d,indent=2))
print(json.dumps(d,indent=2))
PY
[ "${1:-}" = "--json" ] || tmx_log "inventory written to $out (local only, not committed)"
