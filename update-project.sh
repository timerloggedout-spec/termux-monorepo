#!/data/data/com.termux/files/usr/bin/bash
# update-project.sh — Make it happen

set -euo pipefail

ROOT="$HOME/_1-Projects/a/yobitrageswap"
REQ="$HOME/_1-Projects/a/requirements.txt"

echo "==> Verifying project layout"
[ -d "$ROOT" ] || { echo "Missing $ROOT"; exit 1; }

# --- Create BaseAPI ---
API_DIR="$ROOT/api"
mkdir -p "$API_DIR"

BASE_API="$API_DIR/base_api.py"
if [ ! -f "$BASE_API" ]; then
  cat > "$BASE_API" <<'PY'
class BaseAPI:
    def __init__(self, name: str):
        self.name = name

    def connect(self):
        raise NotImplementedError("connect() must be implemented")

    def fetch_orderbook(self, symbol: str):
        """Return dict with keys: bids, asks. Each: list[(price, qty)]."""
        raise NotImplementedError("fetch_orderbook() must be implemented")

    def place_order(self, symbol: str, side: str, qty: float, price: float | None = None):
        """side in {'buy','sell'}; price optional for market orders."""
        raise NotImplementedError("place_order() must be implemented")
PY
  echo " + Created $BASE_API"
else
  echo " ~ Exists $BASE_API (skipped)"
fi

# --- Strategy Engine stub ---
STRAT_DIR="$ROOT/strategies"
ENGINE="$STRAT_DIR/engine.py"
if [ ! -f "$ENGINE" ]; then
  cat > "$ENGINE" <<'PY'
from typing import Dict, Any, List

def normalize_books(books: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, List[tuple]]]:
    out = {}
    for name, book in books.items():
        bids = book.get("bids", [])
        asks = book.get("asks", [])
        out[name] = {
            "bids": [(float(p), float(q)) for p, q in bids],
            "asks": [(float(p), float(q)) for p, q in asks],
        }
    return out

def run_all(apis, symbol: str = "BTC/USDT"):
    books = {}
    for api in apis:
        try:
            api.connect()
            books[api.name] = api.fetch_orderbook(symbol)
        except Exception as e:
            books[api.name] = {"bids": [], "asks": [], "error": str(e)}
    nb = normalize_books(books)
    # Placeholder: hook strategy runners here (bellman_ford, triangular, grid_trading, etc.)
    return {"symbol": symbol, "books": nb}
PY
  echo " + Created $ENGINE"
else
  echo " ~ Exists $ENGINE (skipped)"
fi

# --- Minimal SSE client for live status ---
UTIL_DIR="$ROOT/utils"
mkdir -p "$UTIL_DIR"
SSE="$UTIL_DIR/sse_client.py"
if [ ! -f "$SSE" ]; then
  cat > "$SSE" <<'PY'
import time, sys, json
import urllib.parse, urllib.request

def stream_events(base_url: str, headers: dict):
    # SSE via query params because EventSource cannot set custom headers
    url = urllib.parse.urljoin(base_url, "/events/stream")
    q = urllib.parse.urlencode(headers)
    full = f"{url}?{q}"
    req = urllib.request.Request(full)
    with urllib.request.urlopen(req) as resp:
        buf = b""
        while True:
            chunk = resp.read(1024)
            if not chunk: break
            buf += chunk
            while b"\n\n" in buf:
                event, buf = buf.split(b"\n\n", 1)
                lines = event.decode().split("\n")
                etype = None
                data = ""
                for ln in lines:
                    if ln.startswith("event:"): etype = ln[6:].strip()
                    if ln.startswith("data:"): data += ln[5:].strip()
                if etype:
                    try:
                        payload = json.loads(data)
                    except Exception:
                        payload = {"raw": data}
                    print(json.dumps({"event": etype, "data": payload}))
                time.sleep(0.01)

if __name__ == "__main__":
    # Usage: python sse_client.py http://<ip>:8787 X-API-Key=<key> X-Timestamp=<ts> X-Signature=<sig>
    if len(sys.argv) < 5:
        print("Usage: sse_client.py BASE_URL key=val key=val key=val", file=sys.stderr); sys.exit(1)
    base = sys.argv[1]
    hdrs = dict(arg.split("=", 1) for arg in sys.argv[2:])
    stream_events(base, hdrs)
PY
  echo " + Created $SSE"
else
  echo " ~ Exists $SSE (skipped)"
fi

# --- Patch selected APIs to subclass BaseAPI (idempotent) ---
patch_api() {
  local file="$1"
  if [ -f "$file" ]; then
    if ! grep -q "from \.base_api import BaseAPI" "$file"; then
      sed -i '1i from .base_api import BaseAPI' "$file"
      echo " + import base_api in $(basename "$file")"
    fi
    if ! grep -q "class .*BaseAPI" "$file"; then
      # Wrap first class definition to subclass BaseAPI where feasible
      # This is a conservative textual patch; manual review may be needed for complex files.
      sed -i '0,/class/s//class /' "$file" # no-op anchor
      awk '
        BEGIN{patched=0}
        /^class[[:space:]]+[A-Za-z_][A-Za-z_0-9]*[[:space:]]*\(/{
          if(patched==0){
            sub(/\(/,"(BaseAPI, ",$0); patched=1
          }
        } {print}
      ' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
      echo " + subclass BaseAPI in $(basename "$file") (best-effort)"
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

# --- Add a simple runner in main.py if not present ---
MAIN="$ROOT/main.py"
if [ -f "$MAIN" ] && ! grep -q "run_all(" "$MAIN"; then
  cat >> "$MAIN" <<'PY'

# --- Auto-injected: strategy engine bootstrap ---
try:
    from .strategies.engine import run_all
    from .api.uniswap_api import UniswapAPI
    from .api.yobit_api import YobitAPI
    _apis = []
    try: _apis.append(UniswapAPI())
    except Exception: pass
    try: _apis.append(YobitAPI())
    except Exception: pass
    _res = run_all(_apis)
    print("[engine] books:", {k: {kk: v[:1] for kk, v in val.items()} for k, val in _res["books"].items()})
except Exception as e:
    print("[engine] init error:", e)
PY
  echo " + Injected engine bootstrap into main.py"
else
  echo " ~ main.py bootstrap exists or file missing (skipped)"
fi

# --- Requirements update (idempotent) ---
ensure_req() {
  local pkg="$1"
  grep -qiE "^${pkg}([=<>]|$)" "$REQ" 2>/dev/null || echo "$pkg" >> "$REQ"
}

[ -f "$REQ" ] || touch "$REQ"
ensure_req "requests"
ensure_req "urllib3"
echo " + Requirements updated"

# --- Summary ---
echo "==> Update complete"
echo "Files touched:"
echo " - $BASE_API"
echo " - $ENGINE"
echo " - $SSE"
echo " - patched APIs: uniswap_api.py, yobit_api.py, polygon_api.py, indodax_api.py, tastytrade_api.py, solana_api.py, pumpfun_api.py"
echo " - requirements.txt"

# --- Build (optional prompt) ---
if command -v pip >/dev/null 2>&1; then
  echo "==> Installing requirements (pip)"
  pip install -r "$REQ" >/dev/null 2>&1 && echo " + pip install ok" || echo " ! pip install encountered issues"
else
  echo "pip not found; install with: pkg install python && python -m ensurepip"
fi

echo "==> Run hints"
echo " - Python entry: python -m yobitrageswap.main"
echo " - SSE client: python $SSE http://<device-ip>:8787 X-API-Key=<key> X-Timestamp=<ts> X-Signature=<sig>"
