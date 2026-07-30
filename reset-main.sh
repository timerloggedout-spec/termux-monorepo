#!/data/data/com.termux/files/usr/bin/bash
# reset-main.sh — replace main.py with clean engine bootstrap

set -euo pipefail

MAIN="$HOME/_1-Projects/a/yobitrageswap/main.py"

echo "==> Resetting $MAIN"

cat > "$MAIN" <<'PY'
import sys

# --- Auto-generated clean bootstrap ---
try:
    from .strategies.engine import run_all
    from .api.uniswap_api import UniswapAPI
    from .api.yobit_api import YobitAPI
    from .api.polygon_api import PolygonAPI
    from .api.indodax_api import IndodaxAPI
    from .api.tastytrade_api import TastytradeAPI
    from .api.solana_api import SolanaAPI
    from .api.pumpfun_api import PumpfunAPI

    _apis = []
    for cls in [UniswapAPI, YobitAPI, PolygonAPI, IndodaxAPI,
                TastytradeAPI, SolanaAPI, PumpfunAPI]:
        try:
            _apis.append(cls())
        except Exception as e:
            print(f"[engine] failed to init {cls.__name__}: {e}", file=sys.stderr)

    _res = run_all(_apis)
    print("[engine] books:",
          {k: {kk: v[:1] for kk, v in val.items()}
           for k, val in _res["books"].items()})
except Exception as e:
    print("[engine] init error:", e, file=sys.stderr)
PY

echo "==> Linting..."
if python -m py_compile "$MAIN"; then
  echo "✅ main.py syntax OK"
else
  echo "❌ main.py still has syntax errors"
  exit 1
fi

echo "==> Done. Run with:"
echo "cd ~/_1-Projects/a && python -m yobitrageswap.main"
