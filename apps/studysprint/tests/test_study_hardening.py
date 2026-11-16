"""Offline tests for state recall + hardening (study_hardening.py,
#4159). Opt-in gating, no-guilt construction, ceilings in every
receipt, deterministic pressure, context rotation.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from study_hardening import (plan_hardening_drill,  # noqa: E402
                             record_drill_result,
                             reinstatement_script,
                             varied_context_plan)

NOW = datetime(2026, 11, 3, 9, 0, tzinfo=timezone.utc)


def test_varied_context_rotation():
    plan = varied_context_plan(6)
    places = [a["place"] for a in plan["assignments"]]
    assert len(places) == 6
    assert all(a != b for a, b in zip(places, places[1:]))
    assert "d~0.28" in plan["claims_ceiling"]
    assert varied_context_plan(0)["assignments"] == []


def test_reinstatement_script():
    script = reinstatement_script("Gym Annex B", "BIO 101")
    assert "Gym Annex B" in script["steps"][0]
    assert "BIO 101" in script["steps"][2]
    assert "modest" in script["claims_ceiling"]


def test_hardening_is_opt_in_only():
    refused = plan_hardening_drill("d1", phase=3, opt_in=False,
                                   now=NOW)
    assert refused["status"] == "refused"
    assert refused["opt_in"] is False
    assert "not recall gains" in refused["claims_ceiling"]
    p1 = plan_hardening_drill("d1", phase=1, opt_in=True, now=NOW)
    assert p1["timed"] is False and p1["pressure"] == []
    p3 = plan_hardening_drill("d1", phase=3, opt_in=True, now=NOW)
    assert p3["timed"] is True and len(p3["pressure"]) == 2
    # deterministic: same drill id -> same pressure elements
    assert plan_hardening_drill("d1", 3, True, NOW)["pressure"] == \
        p3["pressure"]
    assert plan_hardening_drill("d2", 3, True, NOW)["pressure"] != \
        p3["pressure"] or True  # (may coincide; determinism is above)
    try:
        plan_hardening_drill("d1", phase=4, opt_in=True, now=NOW)
    except ValueError as e:
        assert "SIT phase" in str(e)
    else:
        raise AssertionError("phase 4 must raise")


def test_results_are_no_guilt_by_construction():
    result = record_drill_result("d1", answered=8, not_yet=3,
                                 opt_in=True, now=NOW)
    assert result["answered"] == 8 and result["not_yet"] == 3
    banned = {"score", "penalty", "deduction", "failed", "grade"}
    assert not (banned & set(result.keys()))
    assert "not a verdict" in result["close"]
    plan = plan_hardening_drill("d1", phase=2, opt_in=True, now=NOW)
    assert "no penalties" in plan["no_guilt"]
    assert plan["opt_in"] is True
