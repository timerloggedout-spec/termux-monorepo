"""Strands pass — kernel-first variant suites (E-05, E-01, E-03).

Each test is one named suite from the pass brief; the cycle's
implementation round records their real pass/fail counts.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.delphi.kernel_experiments import (e01_evidence_gate_delta,  # noqa: E402
                                               e03_counterfactual_replay,
                                               e05_adversarial_firewall)

FIXTURES = ROOT / "tests" / "fixtures" / "delphi_oracle_mvp.json"


def test_e05_adversarial_firewall():
    verdict = e05_adversarial_firewall(FIXTURES)
    assert verdict["adversarial_cases"] > 0
    assert verdict["passed"], verdict


def test_e01_evidence_gate_delta():
    verdict = e01_evidence_gate_delta(FIXTURES)
    assert verdict["oracle_unsafe_pass_through"] == 0
    assert verdict["passed"], verdict


def test_e03_counterfactual_replay():
    verdict = e03_counterfactual_replay(FIXTURES)
    assert verdict["material_pair_flips"] is True
    assert verdict["passed"], verdict
