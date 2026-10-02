#!/usr/bin/env bash
echo "[ ROTATOR STATE ]"
python3 /tmp/hs-stack.py status 2>/dev/null | head -20 | sed 's/^/  /'

echo
echo
