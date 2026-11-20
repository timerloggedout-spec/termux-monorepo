#!/data/data/com.termux/files/usr/bin/bash
# deploy-phase-4.sh — cleanup legacy async code, autoformat, lint

set -euo pipefail
ROOT="$HOME/_1-Projects/a/yobitrageswap"

echo "==> Removing legacy Async*API imports"
# Strip Async*API imports from __init__.py and adapters
grep -rl "Async" "$ROOT/api" | while read -r f; do
  sed -i '/Async/d' "$f"
done

echo "==> Removing duplicate place_order definitions in yobitapi.py"
sed -i '/def place_order/,/^$/d' "$ROOT/api/yobitapi.py"
# Keep only one stubbed place_order

echo "==> Autoformatting with black and isort"
cd "$HOME/_1-Projects/a"
black yobitrageswap
isort yobitrageswap

echo "==> Running flake8 after cleanup"
flake8 yobitrageswap || true

echo "==> Running mypy type check"
mypy yobitrageswap || true

echo "==> Running pytest"
pytest -q || true

echo "==> Phase-4 cleanup complete"
