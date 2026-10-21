#!/data/data/com.termux/files/usr/bin/sh
# Termux:Boot (secondary node). Re-assert scheduled jobs after reboot, then post a fresh
# heartbeat + origin status once the network is up.
ROOT="${TERMUX_MONOREPO_ROOT:-$HOME/termux-monorepo}"
[ -r "$HOME/.config/tmx-device/identity.env" ] && . "$HOME/.config/tmx-device/identity.env"
ROOT="${TERMUX_MONOREPO_ROOT:-$ROOT}"
LOG="$HOME/.local/state/tmx-device/boot.log"
mkdir -p "$(dirname "$LOG")"
(
  i=0
  while [ $i -lt 30 ]; do
    ping -c1 -W2 api.github.com >/dev/null 2>&1 && break
    i=$((i+1)); sleep 10
  done
  echo "boot $(date -u +%FT%TZ) net_wait=${i}"
  kind=secondary; [ "${TERMUX_DEVICE_ID:-}" = "${TMX_ORIGIN_DEVICE_ID:-tmx-node-primary}" ] && kind=origin
  bash "$ROOT/scripts/termux/devices/install-device-jobs.sh" --role "$kind"
) >>"$LOG" 2>&1 &
