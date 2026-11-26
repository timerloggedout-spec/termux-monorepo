#!/data/data/com.termux/files/usr/bin/sh
# install.sh — one-shot install of the B160V persistent-SSH package (Termux).
# Run from the extracted bundle directory:  sh install.sh
set -e
SRC=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
DIR="$HOME/b160v-persistent"
mkdir -p "$DIR" "$HOME/.termux/boot"
cp "$SRC/b160v-tunnel.sh" "$SRC/rendezvous-push.py" "$SRC/start.sh" "$SRC/status.sh" "$DIR/"
chmod +x "$DIR/b160v-tunnel.sh" "$DIR/start.sh" "$DIR/status.sh"
# sshd boot entry — only if the fleet's 00-sshd.sh is not already there.
if [ ! -f "$HOME/.termux/boot/00-sshd.sh" ]; then
  printf '#!/data/data/com.termux/files/usr/bin/sh\nsshd\n' > "$HOME/.termux/boot/00-sshd.sh"
  chmod +x "$HOME/.termux/boot/00-sshd.sh"
  echo "installed ~/.termux/boot/00-sshd.sh"
fi
cp "$SRC/boot-10-b160v-tunnel.sh" "$HOME/.termux/boot/10-b160v-tunnel.sh"
chmod +x "$HOME/.termux/boot/10-b160v-tunnel.sh"
# The tunnel ssh needs a device keypair (Pinggy prompts for a password
# when the client has no key; a key makes the loop non-interactive).
if [ ! -f "$HOME/.ssh/id_ed25519" ]; then
  ssh-keygen -t ed25519 -N '' -f "$HOME/.ssh/id_ed25519" >/dev/null
  echo "generated ~/.ssh/id_ed25519 (device tunnel identity)"
fi
pgrep sshd >/dev/null 2>&1 || sshd
sh "$DIR/start.sh"
sleep 8
echo "---"
sh "$DIR/status.sh"
echo "---"
echo "Install done. If the rendezvous writer shows NOT ARMED, provision the"
echo "one-time token (README, 'Rendezvous credential') — until then the VM"
echo "cannot learn new endpoints automatically."
