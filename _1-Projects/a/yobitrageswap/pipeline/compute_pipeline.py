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
