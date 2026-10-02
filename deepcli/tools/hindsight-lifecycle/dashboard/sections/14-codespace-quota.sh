#!/usr/bin/env bash
echo "[ CODESPACE QUOTA ]"
if [ -f /tmp/hs-cs-quota.py ]; then
  python3 /tmp/hs-cs-quota.py 2>&1 | sed "s/^/  /" | head -12
else
  echo "  (hs-cs-quota.py not shipped)"
fi
echo
