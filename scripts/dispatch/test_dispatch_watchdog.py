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


# ---- priority_timebox riding (owner addendum 2026-11-03) ----

from dispatch_watchdog import (current_tier, entry_of,  # noqa: E402
                               load_timeboxes, thresholds_for)

D1_TIMEBOX = {
    "wall": "2026-11-04T23:59:00-08:00",
    "tiers": [
        {"tier": 0, "name": "BASE", "from": "window open"},
        {"tier": 1, "name": "CUSHION",
         "at": "2026-11-03T09:00:00-08:00"},
        {"tier": 2, "name": "WALL-DAY",
         "at": "2026-11-04T00:00:00-08:00"},
        {"tier": 3, "name": "ESCALATION",
         "at": "2026-11-04T19:59:00-08:00"},
        {"tier": 4, "name": "FINAL",
         "at": "2026-11-04T23:29:00-08:00"},
    ],
}


def test_entry_parsed_from_receipt():
    comments = [{"body": "ROUTING RECEIPT\n- entry: D1\n- scope: x",
                 "created_at": "2026-11-03T00:00:00Z"}]
    assert entry_of(comments) == "D1"
    assert entry_of([]) is None


def test_current_tier_from_timebox_clock():
    before = datetime(2026, 11, 3, 8, 0, tzinfo=timezone.utc)
    assert current_tier(D1_TIMEBOX, before) == (0, "BASE")
    cushion = datetime(2026, 11, 3, 10, 30, tzinfo=timezone.utc)
    # 09:00-08:00 == 17:00Z — not yet; use 18:00Z
    cushion = datetime(2026, 11, 3, 18, 0, tzinfo=timezone.utc)
    assert current_tier(D1_TIMEBOX, cushion) == (1, "CUSHION")
    final = datetime(2026, 11, 5, 7, 35, tzinfo=timezone.utc)
    assert current_tier(D1_TIMEBOX, final) == (4, "FINAL")
    # state-triggered tiers never advance the clock ladder
    domino = {"tiers": [{"tier": 0, "name": "BASE", "at": "now"},
                         {"tier": 1, "name": "CUSHION",
                          "at": "state: filing-ready"}]}
    assert current_tier(domino, cushion) == (0, "BASE")


def test_thresholds_tighten_with_tier():
    assert thresholds_for(0, "BASE") == (30, 60)
    assert thresholds_for(1, "CUSHION") == (20, 40)
    assert thresholds_for(2, "WALL-DAY") == (10, 20)
    assert thresholds_for(3, "ESCALATION") == (5, 10)
    assert thresholds_for(4, "FINAL") == (0, 5)
    # D4-style 6-tier ladder: GATE tier sits at CUSHION class
    assert thresholds_for(1, "GATE — Kiro credit form", 6) == (20, 40)
    assert thresholds_for(5, "FINAL", 6) == (0, 5)


def test_classify_uses_tier_thresholds():
    receipt = {"body": "ROUTING RECEIPT\n- entry: D1",
               "created_at": "2026-11-03T17:30:00Z"}
    issue = {"number": 9, "created_at": "2026-11-03T17:30:00Z",
             "labels": [], "user": {"login": "filer"}}
    at_1755 = datetime(2026, 11, 3, 17, 55, tzinfo=timezone.utc)
    # CUSHION tier (since 17:00Z), 25 min unclaimed: BASE would
    # only watch (flag at 30); CUSHION flags at 20
    verdict = classify(issue, [receipt], at_1755,
                       timeboxes={"D1": D1_TIMEBOX})
    assert verdict["tier"] == "CUSHION"
    assert verdict["action"] == "flag"
    # no timebox -> BASE defaults, still watching at 25 min
    plain = classify(issue, [receipt], at_1755)
    assert plain["action"] is None and plain["tier"] == "BASE"


def test_load_timeboxes_from_feed(tmp_path):
    feed = tmp_path / "desk-feed.json"
    feed.write_text('{"traversals": [{"entry": "D1", '
                    '"priority_timebox": {"wall": "x"}}, '
                    '{"entry": "D0"}]}')
    boxes = load_timeboxes(str(feed))
    assert set(boxes) == {"D1"}
    assert load_timeboxes("/nonexistent.json") == {}
    assert load_timeboxes(None) == {}
