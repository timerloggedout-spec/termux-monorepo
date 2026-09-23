#!/data/data/com.termux/files/usr/bin/bash
# Termux hub bootstrap.
# Usage:
#   sh bootstrap.sh '<COLLABORATOR_PUBLIC_KEY>'
#
# Installs only the base Termux packages required for the hub, configures
# key-only sshd on port 8022, and installs the read-only health probe.
# It does NOT install Tailscale, alter tailnet policy, configure Shizuku,
# create credentials, or expose SSH publicly.

set -eu

PUBKEY="${1:-}"
PREFIX="${PREFIX:-/data/data/com.termux/files/usr}"
HOME_DIR="${HOME:-/data/data/com.termux/files/home}"
REPO_ROOT="${TERMUX_HUB_REPO_ROOT:-$HOME_DIR/termux-monorepo}"

if [ -z "$PUBKEY" ]; then
  echo "usage: sh bootstrap.sh '<collaborator-public-key>'" >&2
  exit 64
fi

case "$PUBKEY" in
  ssh-ed25519\ *|ssh-rsa\ *|ecdsa-sha2-nistp256\ *|ecdsa-sha2-nistp384\ *|ecdsa-sha2-nistp521\ *)
    ;;
  *)
    echo "refusing: argument does not look like an SSH public key" >&2
    exit 64
    ;;
esac

echo "== Termux hub bootstrap =="

pkg update
pkg install -y openssh git python termux-api

mkdir -p "$HOME_DIR/.ssh"
chmod 700 "$HOME_DIR/.ssh"
touch "$HOME_DIR/.ssh/authorized_keys"
chmod 600 "$HOME_DIR/.ssh/authorized_keys"

if ! grep -Fqx -- "$PUBKEY" "$HOME_DIR/.ssh/authorized_keys"; then
  printf '%s\n' "$PUBKEY" >> "$HOME_DIR/.ssh/authorized_keys"
fi

SSHD_CONFIG="$PREFIX/etc/ssh/sshd_config"
if [ -f "$SSHD_CONFIG" ]; then
  cp "$SSHD_CONFIG" "$SSHD_CONFIG.termux-hub.bak"
fi

# Keep the Termux default port and force public-key authentication.
# Do not enable password authentication.
sed -i \
  -e 's/^#\?Port .*/Port 8022/' \
  -e 's/^#\?PasswordAuthentication .*/PasswordAuthentication no/' \
  -e 's/^#\?PubkeyAuthentication .*/PubkeyAuthentication yes/' \
  "$SSHD_CONFIG"

grep -q '^Port 8022$' "$SSHD_CONFIG" || printf '\nPort 8022\n' >> "$SSHD_CONFIG"
grep -q '^PasswordAuthentication no$' "$SSHD_CONFIG" || printf 'PasswordAuthentication no\n' >> "$SSHD_CONFIG"
grep -q '^PubkeyAuthentication yes$' "$SSHD_CONFIG" || printf 'PubkeyAuthentication yes\n' >> "$SSHD_CONFIG"

if [ -d "$REPO_ROOT/scripts/termux-hub" ]; then
  mkdir -p "$HOME_DIR/.local/bin"
  cp "$REPO_ROOT/scripts/termux-hub/health.sh" "$HOME_DIR/.local/bin/termux-hub-health"
  chmod 700 "$HOME_DIR/.local/bin/termux-hub-health"
  if [ -f "$REPO_ROOT/scripts/termux-hub/install-mcp.sh" ]; then
    sh "$REPO_ROOT/scripts/termux-hub/install-mcp.sh"
  fi
fi

# Optional Termux:Boot persistence. Do not assume Termux:Boot exists.
BOOT_DIR="$HOME_DIR/.termux/boot"
if [ -d "$BOOT_DIR" ]; then
  cat > "$BOOT_DIR/termux-hub-sshd" <<'EOF'
#!/data/data/com.termux/files/usr/bin/sh
termux-wake-lock 2>/dev/null || true
pgrep -x sshd >/dev/null 2>&1 || sshd
EOF
  chmod 700 "$BOOT_DIR/termux-hub-sshd"
  echo "boot_hook=installed"
else
  echo "boot_hook=not-installed"
fi

pgrep -x sshd >/dev/null 2>&1 || sshd

echo
echo "== readiness =="
echo "ssh_port=8022"
echo "ssh_key_auth=enabled"
echo "ssh_password_auth=disabled"

if command -v tailscale >/dev/null 2>&1; then
  echo "tailscale_binary=present"
  tailscale ip -4 2>/dev/null || true
else
  echo "tailscale_binary=missing"
fi

if command -v rish >/dev/null 2>&1 && rish -c 'id' >/dev/null 2>&1; then
  echo "shizuku=rish_ready"
elif command -v rish >/dev/null 2>&1; then
  echo "shizuku=rish_present_but_unavailable"
else
  echo "shizuku=rish_missing"
fi

echo "bootstrap=complete"
