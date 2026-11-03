"""Tests for the dispatch claim/lease machinery.

Watchdog classification (claimed / watching / flag / escalate,
dedupe by posted markers, age from the routing receipt), the claim
comment format, and the routing receipt's claim-expectation line.
All offline fixtures — the sweep's API shell is not exercised here.
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from claim_task import claim_comment  # noqa: E402
from dispatch_watchdog import (classify, has_claim, queued_since)  # noqa: E402
from project_task import receipt_comment  # noqa: E402

NOW = datetime(2026, 11, 3, 12, 0, tzinfo=timezone.utc)


def _issue(number=1, minutes_old=0, labels=(), author="filer"):
    created = (NOW - timedelta(minutes=minutes_old)).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    return {"number": number, "created_at": created,
            "labels": [{"name": n} for n in labels],
            "user": {"login": author}}


def _comment(body, minutes_old):
    created = (NOW - timedelta(minutes=minutes_old)).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    return {"body": body, "created_at": created}


RECEIPT = _comment("ROUTING RECEIPT — task accepted", 0)


def test_age_runs_from_receipt_not_creation():
    issue = _issue(minutes_old=600)
    comments = [_comment("ROUTING RECEIPT — x", 45)]
    assert queued_since(issue, comments) == NOW - timedelta(minutes=45)
    verdict = classify(issue, comments, NOW)
    assert verdict["age_min"] == 45.0
    assert verdict["action"] == "flag"


def test_claim_by_label_and_by_comment():
    issue = _issue(minutes_old=300, labels=("dispatch-claimed",))
    assert classify(issue, [RECEIPT], NOW)["state"] == "claimed"
    issue2 = _issue(minutes_old=300)
    claim = _comment("PRODUCER CLAIM — dispatch pickup.", 290)
    assert has_claim(issue2, [RECEIPT, claim])
    assert classify(issue2, [RECEIPT, claim], NOW)["state"] == \
        "claimed"


def test_thresholds_and_dedupe():
    young = classify(_issue(minutes_old=10),
                     [_comment("ROUTING RECEIPT", 10)], NOW)
    assert young["state"] == "watching" and young["action"] is None
    old = classify(_issue(minutes_old=90),
                   [_comment("ROUTING RECEIPT", 90)], NOW)
    assert old["action"] == "escalate"
    flagged = _comment("DISPATCH WATCHDOG — FLAG — ...", 20)
    again = classify(_issue(minutes_old=45),
                     [_comment("ROUTING RECEIPT", 45), flagged], NOW)
    assert again["state"] == "flagged" and again["action"] is None
    esc = _comment("DISPATCH WATCHDOG — ESCALATION — ...", 5)
    escalated = classify(_issue(minutes_old=120),
                         [_comment("ROUTING RECEIPT", 120), esc], NOW)
    assert escalated["state"] == "escalated"
    assert escalated["action"] is None


def test_claim_comment_carries_who_when_seat():
    body = claim_comment("optimizations-assurance", "Some seat",
                         "command-dispatch", "sess-1", NOW)
    assert "PRODUCER CLAIM" in body
    assert "command-dispatch" in body and "sess-1" in body
    assert "2026-11-03T12:00:00Z" in body
    assert "dispatch-claimed" in body


def test_receipt_states_the_claim_expectation():
    fields = {"entry": "D1", "scope": "x", "target-repo": "r"}
    text = receipt_comment(42, fields)
    assert "dispatch-queued" in text
    assert "claim_task.py" in text
    assert "watchdog" in text
