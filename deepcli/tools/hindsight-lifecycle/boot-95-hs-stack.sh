#!/data/data/com.termux/files/usr/bin/sh
termux-wake-lock
sleep 120
while true; do
  ~/.local/bin/hs-stack-watchdog
  sleep 300
done
