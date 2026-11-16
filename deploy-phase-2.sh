#!/data/data/com.termux/files/usr/bin/bash
# deploy-phase-2.sh — Phase-two build: compute pipeline, metrics, validation, events, strategy stubs

set -euo pipefail

ROOT="$HOME/_1-Projects/a/yobitrageswap"

echo "==> Phase-two build starting"

[ -d "$ROOT" ] || { echo "Error: missing $ROOT"; exit 1; }

mkdir -p "$ROOT/pipeline" "$ROOT/events" "$ROOT/metrics"
mkdir -p "$ROOT/strategies/arbitrage" "$ROOT/strategies/gridtrading"
mkdir -p "$ROOT/volatility"

# 1) Fix triangular with legacy analyzeyobit stub + modern entry
cat > "$ROOT/strategies/arbitrage/triangular.py" <<'PY'
# Triangular arbitrage stubs — legacy compatible, safe to import

from typing import Dict, List, Tuple

def analyzeyobit(orderbooks: Dict) -> List[Dict]:
    """
    Legacy stub retained for compatibility. Returns no opportunities.
    """
    return []

def run_triangular(orderbooks: Dict[str, Dict[str, List[Tuple[float, float]]]]) -> List[Dict]:
    """
    Placeholder implementation computing dummy opportunities. Non-throwing, deterministic.
    """
    results = []
    # Example: look for cross-venue spreads on same symbol (bids vs asks)
    # orderbooks: { venue: { 'bids': [(price, qty), ...], 'asks': [(price, qty), ...] } }
    venues = list(orderbooks.keys())
    if len(venues) < 2:
        return results

    # Take top-of-book if present, otherwise skip
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
            spread_bps = ((a_bid - b_ask) / b_ask) * 10000 if b_ask else 0.0
            if spread_bps > 0:
                results.append({
                    'id': f'{a}-{b}-tri',
                    'symbol': 'GENERIC',
                    'buyVenue': b,
                    'sellVenue': a,
                    'spread': spread_bps,
                    'volume': 0.0,
                    'confidence': 0.0,
                    'detectedAt': 0,
                    'expiresAt': 0,
                    'fees': {'buy': 0.0, 'sell': 0.0, 'network': 0.0}
                })
    return results
PY

# 2) Fix volatility with safe stub
cat > "$ROOT/volatility/volatility.py" <<'PY'
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

# 3) Metrics expansion (PnL, spreads, turnover, Sharpe placeholder)
cat > "$ROOT/metrics/metrics.py" <<'PY'
# Deterministic metrics calculation module

from typing import Dict, List, Tuple

def calc_spread_bps(buy: float, sell: float) -> float:
    return ((sell - buy) / buy) * 10000 if buy else 0.0

def calc_pnl_metrics(positions: List[Dict], prices: Dict[str, float]) -> Dict:
    """
    positions: [{symbol, qty, avgPrice}, ...]
    prices: {symbol: last}
    """
    realized = 0.0  # placeholder for future realized tracking
    unrealized = 0.0
    for pos in positions:
        sym = pos['symbol']; qty = pos['qty']; avg = pos['avgPrice']
        last = prices.get(sym, avg)
        unrealized += (last - avg) * qty
    return {'realized': realized, 'unrealized': unrealized, 'total': realized + unrealized}

def calc_turnover(prev_positions: List[Dict], new_positions: List[Dict]) -> float:
    """
    Naive turnover placeholder: sum abs change in qty.
    """
    prev = {p['symbol']: p['qty'] for p in prev_positions}
    new = {p['symbol']: p['qty'] for p in new_positions}
    symbols = set(prev.keys()) | set(new.keys())
    change = sum(abs(new.get(s, 0.0) - prev.get(s, 0.0)) for s in symbols)
    return change

def calc_sharpe_placeholder(expected_return: float, expected_vol: float) -> float:
    """
    Simplified Sharpe placeholder; assumes risk-free ~0.
    """
    return (expected_return / expected_vol) if expected_vol else 0.0
PY

# 4) Events emitter (idempotent, structured)
cat > "$ROOT/events/emitter.py" <<'PY'
# Event emission scaffolding — idempotent payload formatting

import json
from typing import Dict

def format_event(event_type: str, data: Dict, ts: int = 0, event_id: str = None) -> str:
    """
    Returns a JSON line suitable for SSE or logging transport.
    """
    payload = {
        'type': event_type,
        'timestamp': ts,
        'data': data
    }
    if event_id:
        payload['id'] = event_id
    return json.dumps(payload, separators=(',', ':'))

def emit(event_type: str, data: Dict, ts: int = 0, event_id: str = None) -> None:
    """
    Emit to stdout for now; replace with REST/SSE publish in integration.
    """
    print(format_event(event_type, data, ts, event_id))
PY

# 5) Compute pipeline: deterministic, validated, idempotent
cat > "$ROOT/pipeline/compute_pipeline.py" <<'PY'
# Compute pipeline — deterministic metrics, constraint validation, idempotent events

from typing import Dict, List, Tuple
from ..metrics.metrics import calc_pnl_metrics, calc_spread_bps, calc_turnover, calc_sharpe_placeholder
from ..events.emitter import emit

def validate_constraints(vault: Dict, plan: Dict, prices: Dict[str, float]) -> Dict:
    """
    Validate simple constraints: maxPositions, minCash, riskBudget placeholder.
    Returns a dict with 'ok': bool and 'violations': [str].
    """
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

    # riskBudget placeholder (no VaR yet)
    risk_budget = constraints.get('riskBudget')
    if isinstance(risk_budget, (int, float)) and risk_budget < 0:
        violations.append("riskBudget invalid: must be >= 0")

    return {'ok': len(violations) == 0, 'violations': violations}

def compute(vault: Dict, plan: Dict, orderbooks: Dict[str, Dict[str, List[Tuple[float, float]]]],
            prev_vault: Dict = None, prices: Dict[str, float] = None) -> Dict:
    """
    Deterministic compute of metrics, validation, and event emission scaffold.
    """
    prices = prices or {}
    prev_positions = (prev_vault or {}).get('positions', [])
    positions = vault.get('positions', [])

    # Metrics
    pnl = calc_pnl_metrics(positions, prices)
    turnover = calc_turnover(prev_positions, positions)
    expected_return = plan.get('metrics', {}).get('expectedReturn', 0.0)
    expected_vol = plan.get('metrics', {}).get('expectedVol', 0.0)
    sharpe = calc_sharpe_placeholder(expected_return, expected_vol)

    # Simple spread sample between first two venues
    venues = list(orderbooks.keys())
    spread_bps = 0.0
    if len(venues) >= 2:
        a, b = venues[0], venues[1]
        a_ask = orderbooks.get(a, {}).get('asks', [[0.0, 0.0]])[0][0]
        b_bid = orderbooks.get(b, {}).get('bids', [[0.0, 0.0]])[0][0]
        if a_ask and b_bid:
            spread_bps = calc_spread_bps(a_ask, b_bid)

    # Validation
    validation = validate_constraints(vault, plan, prices)

    result = {
        'vault': {'id': vault.get('id'), 'pnl': pnl, 'turnover': turnover, 'risk': {'placeholder': True}},
        'plan': {'id': plan.get('id'), 'metrics': {'expectedReturn': expected_return, 'expectedVol': expected_vol, 'sharpe': sharpe}},
        'market': {'spreadBpsSample': spread_bps},
        'validation': validation
    }

    # Idempotent event emission (no side effects beyond emitting payload)
    emit('compute.result', result, ts=0, event_id=f"compute-{plan.get('id','unknown')}")
    return result
PY

# 6) Update strategies/engine.py to call pipeline
cat > "$ROOT/strategies/engine.py" <<'PY'
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
        except Exception as e:
            books[api.name] = {'bids': [], 'asks': []}

    # Minimal vault/plan placeholders for pipeline compute
    vault = {'id': 'vault-001', 'cash': 10000.0, 'positions': [{'symbol': 'GENERIC', 'qty': 10.0, 'avgPrice': 100.0}]}
    plan = {'id': 'plan-001', 'constraints': {'maxPositions': 25, 'minCash': 1000.0, 'riskBudget': 0.0},
            'metrics': {'expectedReturn': 0.15, 'expectedVol': 0.2}}

    result = compute(vault, plan, books, prev_vault=None, prices={'GENERIC': 101.0})

    return {'books': books, 'compute': result}
PY

# 7) Ensure main.py has clean bootstrap (keep existing if already reset)
cat > "$ROOT/main.py" <<'PY'
import sys

# --- Auto-generated clean bootstrap (phase-two) ---
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
    # Print top-of-book sample and compute summary
    top = {k: {'bid': (v['bids'][0][0] if v['bids'] else None),
               'ask': (v['asks'][0][0] if v['asks'] else None)} for k, v in _res['books'].items()}
    print("[engine] top-of-book:", top)
    print("[compute] summary:", _res['compute'])
except Exception as e:
    print("[engine] init error:", e, file=sys.stderr)
PY

# 8) Lint all Python files
echo "==> Linting package"
find "$ROOT" -name "*.py" -print -exec python -m py_compile {} \;

echo "==> Phase-two build complete"
echo "Run: cd ~/_1-Projects/a && python -m yobitrageswap.main"
