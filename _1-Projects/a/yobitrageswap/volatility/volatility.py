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
