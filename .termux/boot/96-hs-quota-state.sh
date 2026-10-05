#!/data/data/com.termux/files/usr/bin/sh
mkdir -p "$HOME/.deepcli/locks"
exec 9>"$HOME/.deepcli/locks/96-hs-quota-state.lock"
flock -n 9 || exit 0
termux-wake-lock
sleep 60
while true; do
  ~/.local/bin/hs-quota-state >> ~/.deepcli/logs/hs-parity.jsonl 2>&1
  sleep 300
done
