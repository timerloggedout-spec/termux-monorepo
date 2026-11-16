"""Strands pass — packaging-first variant suites (handler, E-08, claims)."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
APP = ROOT / "apps" / "weekend-challenge-delphi-oracle"
sys.path.insert(0, str(APP))

from scripts.delphi.budget_breaker import BudgetTripped, CapGuard  # noqa: E402


def test_handler_conformance():
    from lambda_handler import handler
    out = handler({"id": "conformance-abstain", "action": "inspect",
                   "artifact": None}, None)
    assert out["statusCode"] == 200
    abstain = json.loads(out["body"])
    assert abstain["decision_final"] == "ABSTAIN"
    out = handler({"id": "conformance-escalate",
                   "action": "credential_mutation", "artifact": None}, None)
    escalate = json.loads(out["body"])
    assert escalate["decision_final"] == "ESCALATE"
    assert escalate["external_calls"] == 0


def test_e08_budget_breaker():
    calls = []
    guard = CapGuard(lambda: calls.append(1), limit=3)
    for _ in range(3):
        guard()
    assert guard.tripped and len(calls) == 3
    try:
        guard()
    except BudgetTripped:
        pass
    else:
        raise AssertionError("post-cap call must be denied before invocation")
    receipt = guard.receipt()
    assert receipt["overshoot"] == 0 and receipt["denied"] == 1


def test_no_deploy_claim():
    demo = json.loads((APP / "evidence" / "demo-run.json").read_text())
    assert demo["scenarios"], "the D0 demo record must carry its scenarios"
    for scenario in demo["scenarios"]:
        receipt = scenario["receipt"]
        # The claim under test is NO DEPLOYMENT. (The fetched-evidence
        # scenario legitimately records read-only API calls — that is
        # the tool working, not a deployment.)
        assert receipt["deployment"] is False
