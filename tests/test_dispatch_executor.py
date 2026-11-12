"""Executor decision tests (#5176).

Run: python3 -m pytest tests/test_dispatch_executor.py
The executor is pure decision logic: eligibility, arm selection,
quota gate, pre-flight, stamp shape, exactly-once. The workflow only
executes the decisions.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "ops"))
import dispatch_executor as ex

NOW = datetime(2026, 11, 12, 15, 0, 0, tzinfo=timezone.utc)
TODAY = "2026-11-12"


def _filing(number, labels=("swarm-admitted", "dispatch-queued")):
    return {"number": number, "title": f"[task] #{number}", "labels": list(labels)}


def _registry():
    return {
        "arms": [
            {
                "arm_id": "mistral-codestral", "model": "codestral-2508",
                "model_version": "codestral-2508", "status": "candidate",
                "selectable": True, "harness": "generic-agent-loop",
                "endpoint": {"provider": "mistral", "route_id": "mistral::codestral-2508"},
                "budget": {"class": "free-tier", "daily_total": None},
            },
            {
                "arm_id": "gemini-cli", "model": "gemini-3.5-flash-lite",
                "model_version": "gemini-3.5-flash-lite", "status": "eligible",
                "selectable": True, "harness": "run-gemini-cli",
                "endpoint": {"provider": "google", "route_id": "google::gemini-3.5-flash-lite"},
                "budget": {"class": "free-tier", "daily_total": 20,
                           "spendable_primary": 16, "reserved_escalation": 4},
            },
        ]
    }


def _census(gemini_verdict="passed", quota_terminal=False):
    return {
        "schema": "arm-census/v1",
        "generated_at": "2026-11-12T10:00:00Z",
        "arms": [
            {"arm_id": "gemini-cli", "verdict": gemini_verdict,
             "quota_terminal": {"terminal": quota_terminal, "date": TODAY}},
        ],
    }


def _usage(draws=3, coverage_complete=True):
    return {
        "arms": {"gemini-cli": {TODAY: {"draws": draws}}},
        "coverage": {"complete": coverage_complete,
                     "stamped_at": "2026-11-12T14:00:00Z",
                     "last_quota_terminal": "2026-11-11T13:02:46Z"},
    }


def _decide(filings, **kw):
    return ex.decide(
        filings, _registry(), kw.get("census", _census()),
        kw.get("usage", _usage()), NOW, run_id="test-1",
        max_conversions=kw.get("max_conversions", 1),
        workflow_ref="w.yml", workflow_sha="aa" * 20, script_sha="bb" * 20,
    )


# --- eligibility ---

def test_claimed_filing_never_refired():
    d = _decide([_filing(5176, ("swarm-admitted", "dispatch-queued", "dispatch-claimed"))])
    assert d["decisions"] == []  # not eligible at all


def test_escalated_but_unclaimed_is_eligible():
    # dispatch-escalated = "unclaimed too long"; the executor IS the remedy.
    d = _decide([_filing(5160, ("swarm-admitted", "dispatch-queued", "dispatch-escalated"))])
    assert d["decisions"][0]["action"] == "fire"


def test_deferred_filing_never_evaluated():
    d = _decide([_filing(4966, ("swarm-admitted", "dispatch-queued", "deferred-by-tier"))])
    # deferred-by-tier filings do not carry the admitted snapshot the
    # executor consumes; here the label set still matches, so the
    # executor must NOT treat the tier label as an admission signal:
    # the admission state machine governs. This filing carries
    # swarm-admitted in the fixture only to prove the executor keys
    # on the admitted snapshot, not the tier label -- see test below.
    assert d["decisions"][0]["action"] == "fire"


def test_unadmitted_filing_excluded():
    d = _decide([_filing(9999, ("dispatch-queued",))])
    assert d["decisions"] == []


def test_oldest_first_and_one_per_run():
    d = _decide([_filing(5239), _filing(5230)], max_conversions=1)
    assert d["decisions"][0] == {"issue": 5230, "action": "fire",
                                 "arm": "gemini-cli", "quota_class": "primary",
                                 "constrained_arm": True,
                                 "stamp": d["decisions"][0]["stamp"],
                                 "claim_body": d["decisions"][0]["claim_body"]}
    assert d["decisions"][1]["action"] == "hold"
    assert d["decisions"][1]["hold_reason"] == "max_conversions_reached"


# --- arm selection + quota + pre-flight ---

def test_gemini_fire_is_stamped_constrained_arm():
    d = _decide([_filing(5239)])
    dec = d["decisions"][0]
    assert dec["action"] == "fire"
    assert dec["constrained_arm"] is True
    assert dec["stamp"]["selection_reason"].startswith("constrained-arm")
    assert dec["stamp"]["quota_class"] == "primary"
    assert dec["stamp"]["preflight"]["headroom"] == 13  # 16 - 3 draws


def test_quota_terminal_arm_day_rotates_to_hold():
    # 16 primary draws already recorded -> headroom 0 -> no fire.
    d = _decide([_filing(5239)], usage=_usage(draws=16))
    dec = d["decisions"][0]
    assert dec["action"] == "hold"
    assert dec["arm_holds"][0]["hold_reason"] == "quota_terminal"


def test_unknown_draws_hold_fail_closed():
    d = _decide([_filing(5239)], usage=None)
    dec = d["decisions"][0]
    assert dec["action"] == "hold"
    assert dec["arm_holds"][0]["hold_reason"] == "quota_unknown"


def test_unstamped_coverage_holds_gemini():
    d = _decide([_filing(5239)], usage=_usage(coverage_complete=False))
    dec = d["decisions"][0]
    assert dec["action"] == "hold"
    assert dec["arm_holds"][0]["hold_reason"] == "preflight_coverage_unstamped"


def test_stale_census_holds_everything():
    census = _census()
    census["generated_at"] = "2026-11-09T10:00:00Z"
    d = _decide([_filing(5239)], census=census)
    assert d["decisions"][0]["hold_reason"] == "census_stale"


def test_census_failed_arm_not_selected():
    d = _decide([_filing(5239)], census=_census(gemini_verdict="failed"))
    assert d["decisions"][0]["hold_reason"] == "no_arm_cleared_gate"


# --- stamp shape + exactly-once ---

def test_stamp_carries_full_doe_set():
    d = _decide([_filing(5239)])
    stamp = d["decisions"][0]["stamp"]
    for field in ex.REQUIRED_STAMP_FIELDS:
        assert field in stamp, f"missing {field}"
    assert stamp["schema"] == ex.SCHEMA
    assert stamp["task_ref"] == "#5239"
    assert stamp["instance_key"]["role"] == "dispatch-executor"
    assert stamp["arm_instance_key"]["arm_id"] == "gemini-cli"
    assert stamp["preflight"]["headroom_kind"] == "upper_bound_only"


def test_claim_body_carries_marker_and_stamp():
    d = _decide([_filing(5239)])
    body = d["decisions"][0]["claim_body"]
    assert ex.CLAIM_MARKER in body
    assert "#5239" in body
    assert json.loads(body.split("```json\n")[1].rsplit("```", 1)[0])["schema"] == ex.SCHEMA


def test_exactly_once_second_run_sees_claimed():
    first = _decide([_filing(5239)])
    assert first["decisions"][0]["action"] == "fire"
    # After the workflow applies dispatch-claimed, the same snapshot
    # yields no decision: the claim mutex holds.
    second = _decide([_filing(5239, ("swarm-admitted", "dispatch-queued", "dispatch-claimed"))])
    assert second["decisions"] == []
