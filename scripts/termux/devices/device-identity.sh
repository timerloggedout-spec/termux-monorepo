#!/data/data/com.termux/files/usr/bin/bash
# Opaque device identity, kept separate from hardware/software fingerprints.
# See docs/ops/DEVICE-IDENTITY.md.
#
#   device-identity.sh init [--id tmx-node-xxxx] [--role observer|bridge] [--origin-id tmx-node-primary]
#   device-identity.sh show
#   device-identity.sh keygen                 # operator age keypair (once, on one trusted unit)
#   device-identity.sh seal [--recipient age1...]... [--secret] [--commit]
#   device-identity.sh verify
#
# The public id is random (from /dev/urandom). It is NEVER derived from, hashed from,
# or salted with any hardware or build value. Fingerprints exist only inside an
# age-encrypted envelope.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib.sh
. "$SCRIPT_DIR/lib.sh"

RECIPIENTS_FILE="${TMX_AGE_RECIPIENTS_FILE:-$TERMUX_MONOREPO_ROOT/ops/devices/age-recipients.txt}"
SEALED_DIR="$TMX_CONFIG_DIR/sealed"

mint_id() { printf 'tmx-node-%s\n' "$(od -An -N4 -tx1 /dev/urandom | tr -d ' \n')"; }

secret_name() { printf 'TMX_FPMAP_%s' "$(printf '%s' "${1#tmx-node-}" | tr 'a-z-' 'A-Z_')"; }

cmd_init() {
  local id="" role="observer" origin="$TMX_ORIGIN_DEVICE_ID"
  while [ $# -gt 0 ]; do
    case "$1" in
      --id) id="$2"; shift 2 ;;
      --role) role="$2"; shift 2 ;;
      --origin-id) origin="$2"; shift 2 ;;
      *) tmx_die "init: unknown arg $1" ;;
    esac
  done
  if [ -r "$TMX_IDENTITY_ENV" ] && [ -n "${TERMUX_DEVICE_ID:-}" ]; then
    if [ -z "$id" ] || [ "$id" = "$TERMUX_DEVICE_ID" ]; then
      tmx_log "identity already set: $TERMUX_DEVICE_ID (unchanged)"; return 0
    fi
    tmx_die "identity already set to $TERMUX_DEVICE_ID; refusing to overwrite (move $TMX_IDENTITY_ENV aside manually if intended)"
  fi
  [ -n "$id" ] || id="$(mint_id)"
  printf '%s' "$id" | grep -Eq "$TMX_ID_REGEX" || tmx_die "invalid id '$id'"
  case "$role" in observer|bridge|worker) ;; *) tmx_die "role must be observer|bridge|worker" ;; esac
  mkdir -p "$TMX_CONFIG_DIR" "$TMX_STATE_DIR"; chmod 700 "$TMX_CONFIG_DIR"
  umask 077
  cat >"$TMX_IDENTITY_ENV" <<EOF
# tmx device identity (local only, never committed). Opaque, random, hardware-independent.
export TERMUX_DEVICE_ID="$id"
export TERMUX_DEVICE_ROLE="$role"
export TMX_ORIGIN_DEVICE_ID="$origin"
export TERMUX_MONOREPO_ROOT="$TERMUX_MONOREPO_ROOT"
EOF
  chmod 600 "$TMX_IDENTITY_ENV"
  tmx_log "identity written: $id (role=$role, origin=$origin)"
}

cmd_show() {
  tmx_require_identity
  printf 'device_id=%s\nrole=%s\norigin_device_id=%s\nfpmap_secret=%s\n' \
    "$TERMUX_DEVICE_ID" "${TERMUX_DEVICE_ROLE:-observer}" "$TMX_ORIGIN_DEVICE_ID" "$(secret_name "$TERMUX_DEVICE_ID")"
}

# Fingerprint JSON goes to stdout ONLY when piped straight into age (see cmd_seal).
collect_fingerprint() {
  python - "$TERMUX_DEVICE_ID" <<'PY'
import json, subprocess, sys
from datetime import datetime, timezone
def prop(k):
    try: return subprocess.run(["getprop", k], capture_output=True, text=True, timeout=5).stdout.strip() or None
    except Exception: return None
keys = ["ro.product.manufacturer","ro.product.brand","ro.product.model","ro.product.device",
        "ro.build.fingerprint","ro.build.version.release","ro.build.version.sdk",
        "ro.build.version.security_patch","ro.serialno","ro.boot.serialno","ro.hardware"]
fp = {k: prop(k) for k in keys}
try:
    fp["termux_version"] = subprocess.run(["sh","-c","echo ${TERMUX_VERSION:-}"],capture_output=True,text=True).stdout.strip() or None
except Exception: pass
print(json.dumps({"schema_version":1,"device_id":sys.argv[1],
  "sealed_at":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
  "fingerprint":fp}, indent=2))
PY
}

cmd_keygen() {
  tmx_have age-keygen || tmx_die "pkg install age"
  local key="$TMX_CONFIG_DIR/operator-age.key"
  [ ! -e "$key" ] || tmx_die "$key exists; refusing to overwrite"
  mkdir -p "$TMX_CONFIG_DIR"; umask 077
  age-keygen -o "$key" 2>/dev/null
  chmod 600 "$key"
  echo "public recipient (safe to commit to ops/devices/age-recipients.txt):"
  age-keygen -y "$key"
  echo
  echo "PRIVATE key: $key"
  echo "Store it off-device (password manager) and optionally as a GitHub secret:"
  echo "  gh secret set TMX_DEVICE_AGE_IDENTITY --repo $TMX_REPO < $key"
}

cmd_seal() {
  tmx_require_identity
  tmx_have age || tmx_die "pkg install age"
  local want_secret=0 want_commit=0; local -a rargs=()
  while [ $# -gt 0 ]; do
    case "$1" in
      --recipient) rargs+=(-r "$2"); shift 2 ;;
      --secret) want_secret=1; shift ;;
      --commit) want_commit=1; shift ;;
      *) tmx_die "seal: unknown arg $1" ;;
    esac
  done
  if [ -r "$RECIPIENTS_FILE" ] && grep -q '^age1' "$RECIPIENTS_FILE"; then rargs+=(-R "$RECIPIENTS_FILE"); fi
  [ ${#rargs[@]} -gt 0 ] || tmx_die "no age recipients: add one to $RECIPIENTS_FILE or pass --recipient age1..."
  mkdir -p "$SEALED_DIR"; chmod 700 "$SEALED_DIR"
  local out="$SEALED_DIR/$TERMUX_DEVICE_ID.fpmap.age"
  # Plaintext never touches disk: getprop -> python -> age (armored).
  collect_fingerprint | age -a "${rargs[@]}" -o "$out"
  chmod 600 "$out"
  tmx_log "sealed fingerprint map -> $out"
  if [ "$want_secret" = 1 ]; then
    local name; name="$(secret_name "$TERMUX_DEVICE_ID")"
    gh secret set "$name" --repo "$TMX_REPO" <"$out"
    tmx_log "GitHub secret $name set (age-armored ciphertext)"
  fi
  if [ "$want_commit" = 1 ]; then
    local dest="$TERMUX_MONOREPO_ROOT/ops/devices/sealed/$TERMUX_DEVICE_ID.fpmap.age"
    [ ! -e "$dest" ] || tmx_die "$dest exists; refusing to overwrite (additive-only)"
    mkdir -p "$(dirname "$dest")"; cp "$out" "$dest"
    tmx_log "copied ciphertext into working tree: $dest (commit it via a normal PR)"
  fi
}

cmd_verify() {
  tmx_require_identity
  local rc=0
  echo "device_id: $TERMUX_DEVICE_ID"
  # 1. The id must not contain any fingerprint value (or an obvious slice of one).
  local k v
  for k in ro.product.model ro.product.device ro.serialno ro.boot.serialno ro.hardware; do
    v="$(getprop "$k" 2>/dev/null | tr 'A-Z' 'a-z' | tr -cd 'a-z0-9')"
    [ ${#v} -ge 4 ] || continue
    if printf '%s' "$TERMUX_DEVICE_ID" | tr -cd 'a-z0-9' | grep -qF "$v"; then
      echo "FAIL: device_id contains $k"; rc=1
    fi
  done
  # 2. Public files this lane publishes must not contain fingerprint strings.
  local f
  for f in "$TERMUX_MONOREPO_ROOT/ops/devices/registry.json" "$TMX_STATE_DIR/heartbeat.json"; do
    [ -r "$f" ] || continue
    for k in ro.build.fingerprint ro.serialno ro.boot.serialno; do
      v="$(getprop "$k" 2>/dev/null)"
      [ ${#v} -ge 6 ] || continue
      if grep -qF "$v" "$f"; then echo "FAIL: $f leaks $k"; rc=1; fi
    done
  done
  [ -r "$SEALED_DIR/$TERMUX_DEVICE_ID.fpmap.age" ] && echo "sealed map: present" || echo "sealed map: not yet (run seal)"
  [ $rc = 0 ] && echo "verify: OK"
  return $rc
}

sub="${1:-show}"; shift || true
case "$sub" in
  init) cmd_init "$@" ;;
  show) cmd_show ;;
  keygen) cmd_keygen ;;
  seal) cmd_seal "$@" ;;
  verify) cmd_verify ;;
  *) sed -n '2,12p' "$0"; exit 2 ;;
esac
