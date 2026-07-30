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
