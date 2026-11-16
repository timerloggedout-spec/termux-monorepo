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
