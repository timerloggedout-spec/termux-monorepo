#!/data/data/com.termux/files/usr/bin/bash
# deploy-phase-3.sh — Hardened build: AST validation, flake8/pylint/mypy/pytest, alias patch, schema feed

set -euo pipefail

ROOT="$HOME/_1-Projects/a/yobitrageswap"
cd "$ROOT/.." >/dev/null

echo "==> Phase-three build starting"

[ -d "$ROOT" ] || { echo "Error: missing $ROOT"; exit 1; }

# 0) Ensure tools present (install if missing)
ensure() {
  local pkg="$1"; local import="$2"
  python - <<PY || (echo "==> Installing $pkg" && pip install "$pkg")
try:
    import $import  # noqa
    print("OK")
except Exception:
    raise
PY
}

ensure flake8 flake8
ensure pylint pylint
ensure mypy mypy
ensure pytest pytest

# 1) Patch triangular.py with legacy alias and keep stub logic
TRI="$ROOT/strategies/arbitrage/triangular.py"
mkdir -p "$(dirname "$TRI")"
cat > "$TRI" <<'PY'
# Triangular arbitrage stubs — legacy compatible, safe to import

from typing import Dict, List, Tuple

def analyzeyobit(orderbooks: Dict) -> List[Dict]:
    """Legacy stub retained for compatibility. Returns no opportunities."""
    return []

# Alias with underscore to satisfy legacy imports
analyze_yobit = analyzeyobit

def run_triangular(orderbooks: Dict[str, Dict[str, List[Tuple[float, float]]]]) -> List[Dict]:
    """Placeholder implementation computing dummy opportunities. Deterministic."""
    results = []
    venues = list(orderbooks.keys())
    if len(venues) < 2:
        return results

    # top-of-book snapshot
    top = {}
    for v in venues:
        bids = orderbooks.get(v, {}).get('bids', [])
        asks = orderbooks.get(v, {}).get('asks', [])
        if bids and asks:
            top[v] = {'bid': bids[0][0], 'ask': asks[0][0]}

    vlist = list(top.keys())
    for i in range(len(vlist)):
        for j in range(len(vlist)):
            if i == j: continue
            a = vlist[i]; b = vlist[j]
            a_bid = top[a]['bid']; b_ask = top[b]['ask']
            if not b_ask:
                continue
            spread_bps = ((a_bid - b_ask) / b_ask) * 10000
            if spread_bps > 0:
                results.append({
                    'id': f'{a}-{b}-tri',
                    'symbol': 'GENERIC',
                    'buyVenue': b,
                    'sellVenue': a,
                    'spread': float(spread_bps),
                    'volume': 0.0,
                    'confidence': 0.0,
                    'detectedAt': 0,
                    'expiresAt': 0,
                    'fees': {'buy': 0.0, 'sell': 0.0, 'network': 0.0}
                })
    return results
PY

# 2) Ensure volatility stub is valid
VOL="$ROOT/volatility/volatility.py"
mkdir -p "$(dirname "$VOL")"
cat > "$VOL" <<'PY'
# Volatility analysis stub — deterministic and non-throwing

from typing import List, Dict

def analyze_volatility(series: List[Dict]) -> Dict:
    """
    series: [{timestamp, close}, ...]
    Returns simple variance-based volatility placeholder.
    """
    closes = [p.get('close', 0.0) for p in series if 'close' in p]
    n = len(closes)
    if n < 2:
        return {'volatility': 0.0, 'samples': n}
    mean = sum(closes) / n
    var = sum((c - mean) ** 2 for c in closes) / (n - 1)
    return {'volatility': var ** 0.5, 'samples': n}
PY

# 3) Metrics, events, pipeline (ensure presence)
MET="$ROOT/metrics/metrics.py"
mkdir -p "$ROOT/metrics" "$ROOT/events" "$ROOT/pipeline"
cat > "$MET" <<'PY'
# Deterministic metrics calculation module

from typing import Dict, List, Tuple

def calc_spread_bps(buy: float, sell: float) -> float:
    return ((sell - buy) / buy) * 10000 if buy else 0.0

def calc_pnl_metrics(positions: List[Dict], prices: Dict[str, float]) -> Dict:
    realized = 0.0
    unrealized = 0.0
    for pos in positions:
        sym = pos['symbol']; qty = pos['qty']; avg = pos['avgPrice']
        last = prices.get(sym, avg)
        unrealized += (last - avg) * qty
    return {'realized': realized, 'unrealized': unrealized, 'total': realized + unrealized}

def calc_turnover(prev_positions: List[Dict], new_positions: List[Dict]) -> float:
    prev = {p['symbol']: p['qty'] for p in prev_positions}
    new = {p['symbol']: p['qty'] for p in new_positions}
    symbols = set(prev.keys()) | set(new.keys())
    change = sum(abs(new.get(s, 0.0) - prev.get(s, 0.0)) for s in symbols)
    return change

def calc_sharpe_placeholder(expected_return: float, expected_vol: float) -> float:
    return (expected_return / expected_vol) if expected_vol else 0.0
PY

EMIT="$ROOT/events/emitter.py"
cat > "$EMIT" <<'PY'
# Event emission scaffolding — idempotent payload formatting

import json
from typing import Dict, Optional

def format_event(event_type: str, data: Dict, ts: int = 0, event_id: Optional[str] = None) -> str:
    payload = {'type': event_type, 'timestamp': ts, 'data': data}
    if event_id:
        payload['id'] = event_id
    return json.dumps(payload, separators=(',', ':'))

def emit(event_type: str, data: Dict, ts: int = 0, event_id: Optional[str] = None) -> None:
    print(format_event(event_type, data, ts, event_id))
PY

PIPE="$ROOT/pipeline/compute_pipeline.py"
cat > "$PIPE" <<'PY'
# Compute pipeline — deterministic metrics, constraint validation, idempotent events

from typing import Dict, List, Tuple
from ..metrics.metrics import calc_pnl_metrics, calc_spread_bps, calc_turnover, calc_sharpe_placeholder
from ..events.emitter import emit

def validate_constraints(vault: Dict, plan: Dict, prices: Dict[str, float]) -> Dict:
    violations = []
    constraints = plan.get('constraints', {})
    positions = vault.get('positions', [])
    cash = vault.get('cash', 0.0)

    max_pos = constraints.get('maxPositions')
    if isinstance(max_pos, (int, float)) and len(positions) > max_pos:
        violations.append(f"maxPositions exceeded: {len(positions)} > {max_pos}")

    min_cash = constraints.get('minCash')
    if isinstance(min_cash, (int, float)) and cash < min_cash:
        violations.append(f"minCash violated: {cash} < {min_cash}")

    risk_budget = constraints.get('riskBudget')
    if isinstance(risk_budget, (int, float)) and risk_budget < 0:
        violations.append("riskBudget invalid: must be >= 0")

    return {'ok': len(violations) == 0, 'violations': violations}

def compute(vault: Dict, plan: Dict, orderbooks: Dict[str, Dict[str, List[Tuple[float, float]]]],
            prev_vault: Dict = None, prices: Dict[str, float] = None) -> Dict:
    prices = prices or {}
    prev_positions = (prev_vault or {}).get('positions', [])
    positions = vault.get('positions', [])

    pnl = calc_pnl_metrics(positions, prices)
    turnover = calc_turnover(prev_positions, positions)
    expected_return = plan.get('metrics', {}).get('expectedReturn', 0.0)
    expected_vol = plan.get('metrics', {}).get('expectedVol', 0.0)
    sharpe = calc_sharpe_placeholder(expected_return, expected_vol)

    venues = list(orderbooks.keys())
    spread_bps = 0.0
    if len(venues) >= 2:
        a, b = venues[0], venues[1]
        a_ask = orderbooks.get(a, {}).get('asks', [[0.0, 0.0]])[0][0]
        b_bid = orderbooks.get(b, {}).get('bids', [[0.0, 0.0]])[0][0]
        if a_ask and b_bid:
            spread_bps = calc_spread_bps(a_ask, b_bid)

    validation = validate_constraints(vault, plan, prices)

    result = {
        'vault': {'id': vault.get('id'), 'pnl': pnl, 'turnover': turnover, 'risk': {'placeholder': True}},
        'plan': {'id': plan.get('id'), 'metrics': {'expectedReturn': expected_return, 'expectedVol': expected_vol, 'sharpe': sharpe}},
        'market': {'spreadBpsSample': spread_bps},
        'validation': validation
    }

    emit('compute.result', result, ts=0, event_id=f"compute-{plan.get('id','unknown')}")
    return result
PY

# 4) Engine orchestrator (ensures pipeline call)
ENG="$ROOT/strategies/engine.py"
cat > "$ENG" <<'PY'
# Engine orchestrator — normalizes books, runs pipeline, aggregates outputs

from typing import Dict, List, Tuple
from ..pipeline.compute_pipeline import compute

def normalize_book(raw: Dict[str, List[Tuple[float, float]]]) -> Dict[str, List[Tuple[float, float]]]:
    bids = sorted(raw.get('bids', []), key=lambda x: x[0], reverse=True)
    asks = sorted(raw.get('asks', []), key=lambda x: x[0])
    return {'bids': bids, 'asks': asks}

def run_all(apis: List) -> Dict:
    books: Dict[str, Dict[str, List[Tuple[float, float]]]] = {}
    for api in apis:
        try:
            ob = api.fetch_orderbook('GENERIC')  # symbol placeholder
            books[api.name] = normalize_book(ob or {'bids': [], 'asks': []})
        except Exception:
            books[api.name] = {'bids': [], 'asks': []}

    vault = {'id': 'vault-001', 'cash': 10000.0, 'positions': [{'symbol': 'GENERIC', 'qty': 10.0, 'avgPrice': 100.0}]}
    plan = {'id': 'plan-001', 'constraints': {'maxPositions': 25, 'minCash': 1000.0, 'riskBudget': 0.0},
            'metrics': {'expectedReturn': 0.15, 'expectedVol': 0.2}}

    result = compute(vault, plan, books, prev_vault=None, prices={'GENERIC': 101.0})
    return {'books': books, 'compute': result}
PY

# 5) Ensure main.py bootstrap
MAIN="$ROOT/main.py"
cat > "$MAIN" <<'PY'
import sys

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
            print(f"[engine] failed to init {cls.__name__}: {e}", file=sys.stderr)

    _res = run_all(_apis)
    top = {k: {'bid': (v['bids'][0][0] if v['bids'] else None),
               'ask': (v['asks'][0][0] if v['asks'] else None)} for k, v in _res['books'].items()}
    print("[engine] top-of-book:", top)
    print("[compute] summary:", _res['compute'])
except Exception as e:
    print("[engine] init error:", e, file=sys.stderr)
PY

# 6) Linters and type-check configs
CFG="$ROOT/../setup.cfg"
cat > "$CFG" <<'CFG'
[flake8]
max-line-length = 100
extend-ignore = E203, W503
exclude = .git,__pycache__,build,dist

[tool:pytest]
testpaths = tests
CFG

PYLINTRC="$ROOT/../.pylintrc"
cat > "$PYLINTRC" <<'RC'
[MASTER]
ignore=venv,build,dist,__pycache__
[MESSAGES CONTROL]
disable=missing-docstring,too-few-public-methods,invalid-name
RC

MYPYINI="$ROOT/../mypy.ini"
cat > "$MYPYINI" <<'INI'
[mypy]
python_version = 3.11
ignore_missing_imports = True
strict = False
INI

# 7) Tests: smoke test for pipeline
TESTS="$ROOT/../tests"
mkdir -p "$TESTS"
cat > "$TESTS/test_pipeline.py" <<'PY'
def test_compute_pipeline_runs():
    from yobitrageswap.pipeline.compute_pipeline import compute
    vault = {'id': 'vault-001', 'cash': 10000.0, 'positions': [{'symbol': 'GENERIC', 'qty': 10.0, 'avgPrice': 100.0}]}
    plan = {'id': 'plan-001', 'constraints': {'maxPositions': 25, 'minCash': 1000.0, 'riskBudget': 0.0},
            'metrics': {'expectedReturn': 0.15, 'expectedVol': 0.2}}
    books = {'VenueA': {'bids': [(101.0, 1.0)], 'asks': [(102.0, 1.0)]},
             'VenueB': {'bids': [(103.0, 1.0)], 'asks': [(104.0, 1.0)]}}
    res = compute(vault, plan, books, prev_vault=None, prices={'GENERIC': 101.0})
    assert 'vault' in res and 'plan' in res and 'validation' in res
PY

# 8) AST validator utility
VAL="$ROOT/../validate_ast.py"
cat > "$VAL" <<'PY'
import ast, sys
ok = True
for path in sys.argv[1:]:
    try:
        with open(path, "r") as f:
            src = f.read()
        ast.parse(src, filename=path)
        print(f"✅ AST OK: {path}")
    except SyntaxError as e:
        print(f"❌ AST parse failed in {path}: {e}")
        ok = False
if not ok:
    sys.exit(1)
PY

# 9) Frontend schema feed (aligned to TSX structures)
SCHEMA="$ROOT/../schema_feed.json"
cat > "$SCHEMA" <<'JSON'
{
  "AllocationPlan": {
    "fields": ["id","createdAt","status","topology","constraints","metrics","provenance"]
  },
  "AssetAllocation": {
    "fields": ["symbol","targetWeight","minWeight","maxWeight","slippageBps","venue"]
  },
  "VaultState": {
    "fields": ["id","updatedAt","cash","positions","pnl","risk"]
  },
  "Position": {
    "fields": ["symbol","qty","avgPrice","value"]
  },
  "ArbitrageOpportunity": {
    "fields": ["id","symbol","buyVenue","sellVenue","spread","volume","confidence","detectedAt","expiresAt","fees"]
  },
  "Provenance": {
    "fields": ["parentId","merkleRoot","lineage","ipfsHash","pinned"]
  },
  "PeerNode": {
    "fields": ["nodeId","publicKey","role","lastSeen","capabilities","reputation","seedList"]
  },
  "SyncState": {
    "fields": ["contentId","version","ipfsHash","magnetUri","seeders","verified","replicas"]
  },
  "ConsensusProposal": {
    "fields": ["proposalId","proposer","planId","proposedChanges","votes","quorum","status","expiresAt"]
  },
  "UserAccount": {
    "fields": ["userId","username","email","createdAt","subAccounts","socialGraph","preferences","kycStatus"]
  },
  "SubAccount": {
    "fields": ["subAccountId","exchange","apiKey","permissions","isActive","lastSync"]
  },
  "GameSession": {
    "fields": ["sessionId","userId","gameType","startedAt","endedAt","wagerTotal","payoutTotal","pointsEarned","provablyFairSeed","outcomes"]
  },
  "GameOutcome": {
    "fields": ["roundId","timestamp","wager","payout","result","hash"]
  },
  "SocialConnection": {
    "fields": ["fromUserId","toUserId","type","createdAt","metadata"]
  },
  "AuthToken": {
    "fields": ["keyId","secret","userId","scope","issuedAt","expiresAt","deviceId"]
  },
  "RequestSignature": {
    "fields": ["timestamp","signature","bodyHash","method","path"]
  },
  "ReplayProtection": {
    "fields": ["key","timestamp","signature","firstSeen","expiresAt"]
  },
  "Constraints": {
    "fields": ["maxTurnover","maxPositions","riskBudget","minCash","rules"]
  },
  "PlanMetrics": {
    "fields": ["expectedReturn","expectedVol","sharpe","turnover","trackingError"]
  },
  "TimeSeriesData": {
    "fields": ["symbol","timestamp","open","high","low","close","volume","venue"]
  },
  "Event": {
    "fields": ["type","timestamp","data","id"]
  }
}
JSON

# 10) Syntax compile and AST validate
echo "==> Syntax compile"
find "$ROOT" -name "*.py" -print -exec python -m py_compile {} \;

echo "==> AST validation"
find "$ROOT" -name "*.py" -print | xargs -I{} python "$VAL" {}

# 11) Linting & type check
echo "==> flake8"
flake8 "$ROOT"

echo "==> pylint (summary)"
pylint -j 0 "$ROOT" || true

echo "==> mypy"
mypy "$ROOT" || true

# 12) Pytest smoke test
echo "==> pytest"
pytest -q || { echo "❌ pytest failed"; exit 1; }

echo "==> Phase-three build complete"
echo "Run: cd ~/_1-Projects/a && python -m yobitrageswap.main"
