#!/data/data/com.termux/files/usr/bin/bash
# cleanup-main-v5.sh — aggressive cleanup + lint check for main.py

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

# Remove CONFIG/exchange fragments
sed -i "/CONFIG\[/d" "$MAIN"
sed -i "/exchange in/d" "$MAIN"

# Remove any stray 'if ' at column 0 (top-level ifs that aren't in functions)
sed -i '/^if /d' "$MAIN"
sed -i '/^elif /d' "$MAIN"

echo "==> Cleanup done, now linting..."

# Syntax check with Python
if python -m py_compile "$MAIN"; then
  echo "✅ Syntax OK"
else
  echo "❌ Syntax errors remain in $MAIN"
  exit 1
fi

echo "==> Ready to run:"
echo "cd ~/_1-Projects/a && python -m yobitrageswap.main"
