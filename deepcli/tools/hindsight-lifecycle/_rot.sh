#!/usr/bin/env bash
mkdir -p /tmp/hs-stack
pkill -9 -f 'hs-stack.py watch' 2>/dev/null || true
sleep 1
setsid nohup python3 /tmp/hs-stack.py watch > /tmp/hs-stack-watch.log 2>&1 < /dev/null &
sleep 3
pgrep -af 'hs-stack.py watch' | head -2
