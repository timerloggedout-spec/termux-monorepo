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
