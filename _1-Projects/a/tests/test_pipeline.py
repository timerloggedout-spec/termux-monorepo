def test_compute_pipeline_runs():
    from yobitrageswap.pipeline.compute_pipeline import compute
    vault = {'id': 'vault-001', 'cash': 10000.0, 'positions': [{'symbol': 'GENERIC', 'qty': 10.0, 'avgPrice': 100.0}]}
    plan = {'id': 'plan-001', 'constraints': {'maxPositions': 25, 'minCash': 1000.0, 'riskBudget': 0.0},
            'metrics': {'expectedReturn': 0.15, 'expectedVol': 0.2}}
    books = {'VenueA': {'bids': [(101.0, 1.0)], 'asks': [(102.0, 1.0)]},
             'VenueB': {'bids': [(103.0, 1.0)], 'asks': [(104.0, 1.0)]}}
    res = compute(vault, plan, books, prev_vault=None, prices={'GENERIC': 101.0})
    assert 'vault' in res and 'plan' in res and 'validation' in res
