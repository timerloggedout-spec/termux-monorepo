#!/data/data/com.termux/files/usr/bin/bash
# Hark one-time bootstrap: authorize Hark's sandbox key and keep a Pinggy TCP tunnel
# whose current endpoint is posted to ntfy so Hark can follow rotations. Additive only.
mkdir -p ~/.ssh && chmod 700 ~/.ssh
K='ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEhM206cskpSwqp5eiFdwD3LbAm9GNwT5eLXHHQtLJ1c hark-sandbox'
grep -qF "$K" ~/.ssh/authorized_keys 2>/dev/null || printf '%s\n' "$K" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
pgrep -x sshd >/dev/null || sshd
cat > ~/.hark-tunnel.sh <<'EOS'
#!/data/data/com.termux/files/usr/bin/bash
T=hark-tmx-173e722cc7b2
while true; do
  ssh -tt -p 443 -o StrictHostKeyChecking=accept-new -o ServerAliveInterval=30 -o ExitOnForwardFailure=yes \
    -R0:127.0.0.1:8022 -L4300:127.0.0.1:4300 tcp@free.pinggy.io >/dev/null 2>&1 &
  P=$!; last=""
  while kill -0 $P 2>/dev/null; do
    u=$(curl -s -m 5 127.0.0.1:4300/urls | grep -o 'tcp://[^"]*' | head -1)
    if [ -n "$u" ] && [ "$u" != "$last" ]; then
      curl -s -m 10 -d "$u" "https://ntfy.sh/$T" >/dev/null && last="$u"
      termux-notification --id hark-tunnel -t "Hark tunnel" -c "$u" >/dev/null 2>&1
    fi
    sleep 20
  done
  sleep 10
done
EOS
chmod 700 ~/.hark-tunnel.sh
pkill -f hark-tunnel.sh 2>/dev/null
termux-wake-lock >/dev/null 2>&1
nohup ~/.hark-tunnel.sh >/dev/null 2>&1 &
echo "Hark key installed; tunnel loop started"
