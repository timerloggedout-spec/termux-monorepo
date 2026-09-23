#!/data/data/com.termux/files/usr/bin/sh
# Read-only Termux hub health probe.
# Never prints private keys, tokens, OTP material, or authorized_keys contents.
set -u

status=0
say() { printf '%s=%s\n' "$1" "$2"; }

say timestamp "$(date -Iseconds)"
say host "$(hostname 2>/dev/null || printf unknown)"
say user "$(whoami 2>/dev/null || printf unknown)"

if command -v tailscale >/dev/null 2>&1; then
  say tailscale_binary "$(command -v tailscale)"
  if tailscale ip -4 >/tmp/termux-hub-tailscale-ip.$$ 2>/dev/null; then
    say tailscale_ipv4 "$(cat /tmp/termux-hub-tailscale-ip.$$)"
  else
    say tailscale_ipv4 unavailable
    status=1
  fi
  rm -f /tmp/termux-hub-tailscale-ip.$$
else
  say tailscale_binary missing
  status=1
fi

if command -v sshd >/dev/null 2>&1; then
  say sshd_binary "$(command -v sshd)"
  if pgrep -x sshd >/dev/null 2>&1; then
    say sshd_process ready
  else
    say sshd_process missing
    status=1
  fi
else
  say sshd_binary missing
  status=1
fi

if command -v git >/dev/null 2>&1; then
  say git ready
else
  say git missing
  status=1
fi

if command -v python >/dev/null 2>&1; then
  say python "$(python --version 2>&1)"
else
  say python missing
  status=1
fi

if command -v termux-battery-status >/dev/null 2>&1; then
  if termux-battery-status >/dev/null 2>&1; then
    say termux_api battery_ready
  else
    say termux_api battery_unavailable
  fi
else
  say termux_api unavailable
fi

if command -v rish >/dev/null 2>&1; then
  if rish -c 'id' >/dev/null 2>&1; then
    say shizuku rish_ready
  else
    say shizuku rish_present_but_unavailable
  fi
else
  say shizuku rish_missing
fi

say result "$([ "$status" -eq 0 ] && printf READY || printf DEGRADED)"
exit "$status"
