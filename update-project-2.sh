#!/data/data/com.termux/files/usr/bin/bash
# update-project-v2.sh — unify APIs, stub orderbooks, refactor main.py

set -euo pipefail

ROOT="$HOME/_1-Projects/a/yobitrageswap"
API_DIR="$ROOT/api"
MAIN="$ROOT/main.py"

echo "==> Verifying project layout"
[ -d "$ROOT" ] || { echo "Missing $ROOT"; exit 1; }

# --- Stub orderbook template ---
stub_fetch='
    def fetch_orderbook(self, symbol: str):
        # Stub: return dummy bids/asks
        return {
            "bids": [(100.0, 1.0), (99.5, 2.0)],
            "asks": [(101.0, 1.5), (101.5, 2.5)]
        }

    def place_order(self, symbol, side, qty, price=None):
        return {"status": "stub", "symbol": symbol, "side": side, "qty": qty, "price": price}
'

# --- Patch each API file ---
patch_api() {
  local file="$1"
  if [ -f "$file" ]; then
    if ! grep -q "def fetch_orderbook" "$file"; then
      echo " + Adding stub fetch_orderbook to $(basename "$file")"
      echo "$stub_fetch" >> "$file"
    else
      echo " ~ $(basename "$file") already has fetch_orderbook"
    fi
  fi
}

patch_api "$API_DIR/uniswap_api.py"
patch_api "$API_DIR/yobit_api.py"
patch_api "$API_DIR/polygon_api.py"
patch_api "$API_DIR/indodax_api.py"
patch_api "$API_DIR/tastytrade_api.py"
patch_api "$API_DIR/solana_api.py"
patch_api "$API_DIR/pumpfun_api.py"

# --- Refactor main.py ---
if [ -f "$MAIN" ]; then
  # Remove any async with AsyncYobitAPI lines
  sed -i '/AsyncYobitAPI/d' "$MAIN"

  # Ensure engine bootstrap is present
  if ! grep -q "Auto-injected: strategy engine bootstrap" "$MAIN"; then
    cat >> "$MAIN" <<'PY'

# --- Auto-injected: strategy engine bootstrap ---
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
    for cls in [UniswapAPI, YobitAPI, PolygonAPI, IndodaxAPI, TastytradeAPI, SolanaAPI, PumpfunAPI]:
        try:
            _apis.append(cls())
        except Exception as e:
            print(f"[engine] failed to init {cls.__name__}: {e}")

    _res = run_all(_apis)
    print("[engine] books:", {k: {kk: v[:1] for kk, v in val.items()} for k, val in _res["books"].items()})
except Exception as e:
    print("[engine] init error:", e)
PY
    echo " + Injected engine bootstrap into main.py"
  else
    echo " ~ main.py already has engine bootstrap"
  fi
else
  echo " ! main.py not found"
fi

echo "==> Update complete"
echo "Now run: python -m yobitrageswap.main"
