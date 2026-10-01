#!/usr/bin/env python3
import importlib.util
from pathlib import Path

import sys

p = Path(__file__).resolve().parents[1] / "scripts" / "bayesian_routing.py"
spec = importlib.util.spec_from_file_location("bayesian_routing", p)
m = importlib.util.module_from_spec(spec)
sys.modules["bayesian_routing"] = m
spec.loader.exec_module(m)

b = m.posterior([
    {"experiment_id":"a","executed":True,"attributed":True,"outcome":True},
    {"experiment_id":"b","executed":True,"attributed":True,"outcome":False},
    {"experiment_id":"b","executed":True,"attributed":True,"outcome":False},
    {"experiment_id":"c","executed":False,"attributed":True,"outcome":False},
    {"experiment_id":"d","executed":True,"attributed":False,"outcome":False},
])
assert b.alpha == 2.0 and b.beta == 2.0, (b.alpha, b.beta)
assert abs(b.mean - 0.5) < 1e-12

x = m.BetaBelief(9, 1)
y = m.BetaBelief(1, 9)
assert m.probability_a_exceeds_b(x, y, draws=2000, seed=42) > 0.95
assert abs(m.expected_value_of_information(0.7, 0.9, 0.1) - 0.1) < 1e-12
print("bayesian routing tests: PASS")
