#!/data/data/com.termux/files/usr/bin/sh
termux-wake-lock
sleep 60
while true; do
  ~/.local/bin/hs-quota-state >> ~/.deepcli/logs/hs-parity.jsonl 2>&1
  sleep 300
done
