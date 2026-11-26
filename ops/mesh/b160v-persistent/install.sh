#!/data/data/com.termux/files/usr/bin/sh
# install.sh — one-shot install of the B160V persistent-SSH package (Termux).
# Run from the extracted bundle directory:  sh install.sh
#
# Conforms to the device's own arrangements (read firsthand 2026-11-26):
#  - persistence = a service under ~/bin/supervisor.sh (rish probe gate,
#    pgrep-guarded nohup starts, 60s loop) + a boot entry in the existing
#    numbering (00 · 10 · 45 · 50 · 99 — this takes slot 20)
#  - services are long-running loops in ~/bin (cf. mem-guard.sh,
#    wifi-watchdog.sh); the tunnel loop installs there too
set -e
SRC=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
DIR="$HOME/b160v-persistent"
mkdir -p "$DIR" "$HOME/.termux/boot" "$HOME/bin"
cp "$SRC/b160v-tunnel.sh" "$HOME/bin/b160v-tunnel.sh"
cp "$SRC/rendezvous-push.py" "$SRC/start.sh" "$SRC/status.sh" "$DIR/"
chmod +x "$HOME/bin/b160v-tunnel.sh" "$DIR/start.sh" "$DIR/status.sh"
# cloudflared carries the tunnel (Termux package; static Go binary).
if ! command -v cloudflared >/dev/null 2>&1; then
  echo "installing cloudflared via pkg..."
  pkg install -y cloudflared || echo "WARN: pkg install cloudflared failed — install it manually"
fi
# cf.env template (named mode default) — never overwritten once present.
if [ ! -f "$DIR/cf.env" ]; then
  cat > "$DIR/cf.env" <<'EOF'
# b160v-persistent tunnel config (sourced by b160v-tunnel.sh)
# named mode: set CF_HOSTNAME to the tunnel's stable hostname and put the
# tunnel token in ~/b160v-persistent/cf-token (chmod 600). See README.
CF_MODE=named
CF_HOSTNAME=
# alternate: CF_MODE=quick (anonymous trycloudflare hostname; rotates,
# and unreachable from the muse-vm egress — see README "Carrier evidence")
EOF
  echo "wrote $DIR/cf.env (named mode — set CF_HOSTNAME, see README)"
fi
# sshd boot entry — only if the fleet's 00-sshd.sh is not already there.
if [ ! -f "$HOME/.termux/boot/00-sshd.sh" ]; then
  printf '#!/data/data/com.termux/files/usr/bin/sh\nsshd\n' > "$HOME/.termux/boot/00-sshd.sh"
  chmod +x "$HOME/.termux/boot/00-sshd.sh"
  echo "installed ~/.termux/boot/00-sshd.sh"
fi
# Retire earlier revisions: the v1 10-slot boot entry, and any leftover
# artifacts of the revoked carrier's watchdog (owner ruling 2026-11-26).
rm -f "$HOME/.termux/boot/10-b160v-tunnel.sh"
rm -f "$HOME/.termux/boot/20-persistent-ssh.sh" "$HOME/bin/tunnel-watchdog.sh"
cp "$SRC/boot-20-b160v-persistent.sh" "$HOME/.termux/boot/20-b160v-persistent.sh"
chmod +x "$HOME/.termux/boot/20-b160v-persistent.sh"
# Supervisor stanza — idempotent, marker-guarded, one backup taken.
SUP="$HOME/bin/supervisor.sh"
if [ -f "$SUP" ] && ! grep -q "b160v-tunnel.sh" "$SUP" 2>/dev/null; then
  cp "$SUP" "$SUP.bak-b160v"
  python3 - "$SUP" <<'PY'
import sys
path = sys.argv[1]
src = open(path).read()
anchor = 'nohup ~/bin/wifi-watchdog.sh > /dev/null 2>&1 &'
stanza = ('\n        # b160v-persistent (installed by b160v-persistent/install.sh)\n'
          '        if ! pgrep -f "b160v-tunnel.sh" > /dev/null; then\n'
          '            nohup ~/bin/b160v-tunnel.sh > /dev/null 2>&1 &\n'
          '        fi')
idx = src.find(anchor)
if idx < 0:
    # Fall back: append the guard before the sleep 60 line.
    src = src.replace('    sleep 60', stanza.replace('        ', '    ') + '\n    sleep 60', 1)
else:
    fi_idx = src.find('        fi', idx)
    src = src[:fi_idx + len('        fi')] + stanza + src[fi_idx + len('        fi'):]
open(path, 'w').write(src)
print('supervisor stanza added (backup: supervisor.sh.bak-b160v)')
PY
elif grep -q "b160v-tunnel.sh" "$SUP" 2>/dev/null; then
  echo "supervisor stanza already present"
else
  echo "WARN: ~/bin/supervisor.sh not found — tunnel runs via boot entry only"
fi
pgrep sshd >/dev/null 2>&1 || sshd
sh "$DIR/start.sh"
sleep 8
echo "---"
sh "$DIR/status.sh"
echo "---"
echo "Install done. Two one-time provisionings may still be open (README):"
echo "  1. named tunnel: cf-token + CF_HOSTNAME in ~/b160v-persistent/cf.env"
echo "  2. rendezvous writer: WEBWRAPPER_GH_TOKEN in ~/b160v-persistent/token.env"
echo "Until (1) the loop waits; until (2) the VM cannot learn the endpoint."
