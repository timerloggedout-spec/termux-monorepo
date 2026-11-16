#!/data/data/com.termux/files/usr/bin/bash
# cleanup-main-v3.sh — remove obsolete strategy fragments from main.py

set -euo pipefail

MAIN="$HOME/_1-Projects/a/yobitrageswap/main.py"

if [ ! -f "$MAIN" ]; then
  echo "Error: $MAIN not found"
  exit 1
fi

echo "==> Cleaning $MAIN"

# Remove any lines mentioning Async*API
sed -i '/Async.*API/d' "$MAIN"
sed -i '/async with /d' "$MAIN"

# Remove dangling strategy method checks
sed -i "/if method ==/d" "$MAIN"
sed -i "/elif method ==/d" "$MAIN"
sed -i "/else:/d" "$MAIN"

echo "==> Cleanup complete"
echo "Now run: cd ~/_1-Projects/a && python -m yobitrageswap.main"
