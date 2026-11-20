#!/data/data/com.termux/files/usr/bin/bash
# cleanup-main-v2.sh — remove all obsolete Async*API code from main.py

set -euo pipefail

MAIN="$HOME/_1-Projects/a/yobitrageswap/main.py"

if [ ! -f "$MAIN" ]; then
  echo "Error: $MAIN not found"
  exit 1
fi

echo "==> Cleaning $MAIN"

# Remove any lines mentioning Async*API
sed -i '/Async.*API/d' "$MAIN"

# Remove dangling "async with" lines (if any remain)
sed -i '/async with /d' "$MAIN"

echo "==> Cleanup complete"
echo "Now run: cd ~/_1-Projects/a && python -m yobitrageswap.main"
