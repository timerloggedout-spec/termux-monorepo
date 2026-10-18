#!/data/data/com.termux/files/usr/bin/bash
# Provision a NEW BLU View 5 B160V (secondary node) from a fresh Termux install.
# Additive and idempotent: safe to re-run. Never touches the origin's jobs or manifest.
#
#   bash scripts/termux/devices/provision-secondary.sh --device-id tmx-node-55619bd5 [--skip-pkg] [--no-sshd]
#
# Steps: packages -> Termux:API check -> opaque identity -> git guard -> boot scripts
#        -> sshd key-only -> scheduled jobs (43110 heartbeat, 43111 origin status) -> verify
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
export TERMUX_MONOREPO_ROOT="$ROOT"
DEVICE_ID=""; ORIGIN_ID="tmx-node-primary"; SKIP_PKG=0; NO_SSHD=0
while [ $# -gt 0 ]; do
  case "$1" in
    --device-id) DEVICE_ID="$2"; shift 2 ;;
    --origin-id) ORIGIN_ID="$2"; shift 2 ;;
    --skip-pkg) SKIP_PKG=1; shift ;;
    --no-sshd) NO_SSHD=1; shift ;;
    *) echo "unknown arg $1" >&2; exit 2 ;;
  esac
done
[ "$DEVICE_ID" != "$ORIGIN_ID" ] || { echo "secondary must not reuse the origin id $ORIGIN_ID" >&2; exit 2; }
step() { printf '\n==> %s\n' "$*"; }

step "1/8 packages"
if [ "$SKIP_PKG" = 0 ]; then
  pkg update -y
  pkg install -y git gh openssh python termux-api jq age curl procps
fi

step "2/8 Termux:API companion"
if timeout 20 termux-battery-status >/dev/null 2>&1; then echo "Termux:API OK"
else echo "WARN: Termux:API app not responding. Install it from the SAME source as Termux (F-Droid), open it once, allow notifications."; fi
if pm list packages 2>/dev/null | grep -q 'com.termux.boot'; then echo "Termux:Boot installed"
else echo "NOTE: could not confirm Termux:Boot; install it from F-Droid and open it once so Android runs ~/.termux/boot."; fi

step "3/8 GitHub CLI auth"
gh auth status >/dev/null 2>&1 || gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git

step "4/8 opaque device identity"
if [ -n "$DEVICE_ID" ]; then
  bash "$SCRIPT_DIR/device-identity.sh" init --id "$DEVICE_ID" --role observer --origin-id "$ORIGIN_ID"
else
  bash "$SCRIPT_DIR/device-identity.sh" init --role observer --origin-id "$ORIGIN_ID"
fi
bash "$SCRIPT_DIR/device-identity.sh" show

step "5/8 destructive-git guard"
bash "$SCRIPT_DIR/install-git-guard.sh"
export PATH="$HOME/.local/bin:$PATH"

step "6/8 Termux:Boot scripts"
mkdir -p "$HOME/.termux/boot"
for f in "$SCRIPT_DIR"/boot/*.sh; do
  dest="$HOME/.termux/boot/$(basename "$f")"
  install -m 700 "$f" "$dest"; echo "installed $dest"
done

step "7/8 sshd (key-only, LAN/ADB recovery)"
if [ "$NO_SSHD" = 0 ]; then
  mkdir -p "$HOME/.ssh"; chmod 700 "$HOME/.ssh"; touch "$HOME/.ssh/authorized_keys"; chmod 600 "$HOME/.ssh/authorized_keys"
  cfg="$PREFIX/etc/ssh/sshd_config"
  grep -q '^# tmx-secondary' "$cfg" 2>/dev/null || printf '\n# tmx-secondary\nPasswordAuthentication no\nPermitRootLogin no\n' >>"$cfg"
  pgrep -x sshd >/dev/null || sshd
  [ -s "$HOME/.ssh/authorized_keys" ] || echo "NOTE: add your workstation public key to ~/.ssh/authorized_keys"
fi

step "8/8 scheduled jobs + first run"
bash "$SCRIPT_DIR/install-device-jobs.sh" --role secondary
bash "$SCRIPT_DIR/device-identity.sh" verify || true

cat <<MSG

Provisioned $(bash "$SCRIPT_DIR/device-identity.sh" show | head -n1).
Next (once): seal the fingerprint map -> docs/ops/DEVICE-IDENTITY.md
  bash $SCRIPT_DIR/device-identity.sh seal --secret
Test the guard (new shell):   git -C "$ROOT" reset --hard   # expect BLOCKED
MSG
