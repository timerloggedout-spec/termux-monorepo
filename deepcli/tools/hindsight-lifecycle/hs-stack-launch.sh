#!/usr/bin/env bash
set -u
cd /tmp

echo "=== probe ==="
python3 /tmp/hs-stack.py probe 2>&1 | tail -25

echo
echo "=== rotate ==="
python3 /tmp/hs-stack.py rotate 2>&1 | tail -5

echo
echo "=== status ==="
python3 /tmp/hs-stack.py status 2>&1

echo
echo "=== watch (setsid) ==="
pkill -9 -f 'hs-stack.py watch' 2>/dev/null
setsid nohup python3 /tmp/hs-stack.py watch > /tmp/hs-stack-watch.log 2>&1 < /dev/null &
sleep 3
echo "  watch pid: $(pgrep -f 'hs-stack.py watch' | head -1)"
