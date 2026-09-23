#!/data/data/com.termux/files/usr/bin/sh
set -u

say() { printf '%s=%s\n' "$1" "$2"; }

say timestamp "$(date -Iseconds)"
say termux_prefix "${PREFIX:-unknown}"
say python "$(python3 --version 2>&1 || printf missing)"
say openssh "$(command -v sshd || printf missing)"
say tailscale "$(command -v tailscale || printf missing)"
say termux_api "$(command -v termux-battery-status || printf missing)"
say rish "$(command -v rish || printf missing)"

if command -v tailscale >/dev/null 2>&1; then
  say tailscale_ipv4 "$(tailscale ip -4 2>/dev/null || printf unavailable)"
  tailscale status 2>&1 | head -30
fi

if command -v pgrep >/dev/null 2>&1 && command -v sshd >/dev/null 2>&1; then
  pgrep -a sshd || true
fi

if command -v rish >/dev/null 2>&1; then
  say shizuku_identity "$(rish -c 'id' 2>/dev/null || printf unavailable)"
  say shizuku_package "$(rish -c 'pm path moe.shizuku.privileged.api' 2>/dev/null || printf unavailable)"
  say accessibility "$(rish -c 'settings get secure enabled_accessibility_services' 2>/dev/null || printf unavailable)"
fi

if [ -x "$HOME/.local/bin/termux-hub-mcp" ]; then
  say mcp_entrypoint ready
else
  say mcp_entrypoint missing
fi
