#!/data/data/com.termux/files/usr/bin/bash
# reset-triangular.sh — replace triangular.py with a safe stub

TRI="$HOME/_1-Projects/a/yobitrageswap/strategies/arbitrage/triangular.py"

cat > "$TRI" <<'PY'
# Safe stub for triangular arbitrage strategy

def run_triangular(orderbooks):
    """
    Placeholder implementation.
    Accepts a dict of orderbooks and returns an empty list of opportunities.
    """
    return []
PY

echo "==> triangular.py reset to safe stub"
python -m py_compile "$TRI" && echo "✅ Syntax OK"
