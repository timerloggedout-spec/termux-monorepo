"""Offline tests for the memory methods (study_memory.py, RFP-D1-5).

All six methods covered, claims ceilings asserted where the RFP
binds them (loci: ordered recall not understanding; pomodoro:
pacing not memory)."""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from study_memory import (LeitnerScheduler, adapt_block_length,  # noqa: E402
                          apply_notification_grade, build_palace,
                          explain_back, fsrs_retrievability,
                          interleave_sessions, leitner_review,
                          plan_pomodoro, pomodoro_checkin,
                          retrievability_notifications, walk_review)
from study_sr import build_cards  # noqa: E402

NOW = datetime(2026, 11, 3, 9, 0, tzinfo=timezone.utc)


# 1. loci -----------------------------------------------------------------

def test_palace_places_items_on_route_in_order():
    palace = build_palace(
        ["Chapter 1: Cells", "Chapter 2: Energy"],
        {"Chapter 1: Cells": [{"term": "Cell membrane"},
                              {"term": "Nucleus"}],
         "Chapter 2: Energy": [{"term": "Photosynthesis"}]})
    placed = [(p["position"], p["locus"], p["item"])
              for p in palace["placements"]]
    assert placed[0][2] == "Cell membrane" and placed[0][0] == 1
    assert placed[2][2] == "Photosynthesis"
    assert palace["claims_ceiling"].startswith("ordered/concrete")


def test_walk_review_scores_ordered_recall():
    palace = build_palace(["Ch"], {"Ch": ["a", "b", "c", "d"]})
    r = walk_review(palace, ["a", "c", "b"], NOW)
    assert r["correct_in_position"] == 1  # only "a" sits in its place
    assert r["recalled_out_of_order"] == 2
    assert r["missed"] == ["d"]
    assert r["ordered_recall"] == 0.25
    perfect = walk_review(palace, ["a", "b", "c", "d"], NOW)
    assert perfect["ordered_recall"] == 1.0


# 2. pomodoro -------------------------------------------------------------

def test_pomodoro_plan_shape_and_ceiling():
    plan = plan_pomodoro()
    kinds = [b["kind"] for b in plan["blocks"]]
    assert kinds == ["focus", "short-break", "focus", "short-break",
                     "focus", "short-break", "focus"]
    assert plan["focused_minutes"] == 100
    assert plan["claims_ceiling"] == "pacing/starting, not memory"
    long_plan = plan_pomodoro(total_focus_blocks=5)
    assert "long-break" in [b["kind"] for b in long_plan["blocks"]]


def test_pomodoro_checkin_and_adaptation():
    plan = plan_pomodoro()
    done = pomodoro_checkin(plan, 4, NOW)
    assert done["status"] == "done" and done["minutes_focused"] == 100
    assert pomodoro_checkin(plan, 2, NOW)["status"] == "partial"
    assert pomodoro_checkin(plan, 0, NOW)["status"] == "missed"
    up = adapt_block_length([done, done, done], current_focus=25)
    assert up["suggested_focus"] == 30
    down = adapt_block_length(
        [pomodoro_checkin(plan, 1, NOW), pomodoro_checkin(plan, 0, NOW)],
        current_focus=25)
    assert down["suggested_focus"] == 20
    hold = adapt_block_length([done], current_focus=25)
    assert hold["suggested_focus"] == 25


# 3. retrievability notifications -----------------------------------------

def test_retrievability_curve_and_threshold_fire():
    assert fsrs_retrievability(10.0, 0.0) == 1.0
    assert fsrs_retrievability(10.0, 20.0) < 0.9  # R(S,S) ~= 0.9 by construction
    due_soon = {"card_id": "c1", "front": "What does the membrane do?",
                "state": {"stability": 2.0,
                          "last_review": "2026-10-24T09:00:00Z"}}
    fresh = {"card_id": "c2", "front": "Fresh card",
             "state": {"stability": 30.0,
                       "last_review": "2026-11-02T09:00:00Z"}}
    unreviewed = {"card_id": "c3", "front": "New", "state": {}}
    notes = retrievability_notifications([due_soon, fresh, unreviewed],
                                         NOW, threshold=0.9)
    assert [n["card_id"] for n in notes] == ["c1"]
    n = notes[0]
    assert n["cue"] == due_soon["front"]
    assert n["retrievability"] <= 0.9
    assert n["text"].startswith("When this reminder fires, I will")
    assert n["one_tap_grade"]["grades"] == [1, 2, 3, 4]


def test_apply_notification_grade_returns_sr_receipt():
    card = build_cards([{"q": "Q?", "a": "A."}])[0]
    _state, receipt = apply_notification_grade(card, None, 3, NOW)
    assert receipt["scheduler"] == "fsrs"
    assert receipt["via"] == "retrievability-notification"


# 4. feynman --------------------------------------------------------------

EVIDENCE = [{"term": "Photosynthesis",
             "definition": "Conversion of light energy into chemical "
                           "energy by plants."}]


def test_explain_back_grades_against_verified_evidence():
    good = explain_back(
        "Photosynthesis",
        "Photosynthesis is the conversion of light energy into "
        "chemical energy by plants.", EVIDENCE, NOW)
    assert good["verdict"] == "graded" and good["coverage"] == 1.0
    thin = explain_back("Photosynthesis", "Plants grow in soil.",
                        EVIDENCE, NOW)
    assert thin["verdict"] == "escalate"
    assert "conversion" in thin["missing_terms"]


def test_explain_back_abstains_without_evidence():
    out = explain_back("Anything", "A confident paragraph.", [], NOW)
    assert out["verdict"] == "abstain" and out["coverage"] is None


# 5. interleaving -----------------------------------------------------------

def test_interleave_mixes_topics_and_cards():
    quiz = {"cells": [{"q": "q1"}, {"q": "q2"}],
            "energy": [{"q": "q3"}]}
    cards = build_cards([{"term": "Nucleus", "definition": "DNA store.",
                          "tags": ["cells"]}])
    session = interleave_sessions(quiz, cards)
    assert session["item_count"] == 4
    # 3 cells items vs 1 energy: one same-topic adjacency is the
    # optimum (rotation cannot do better); a balanced mix reaches 0
    assert session["adjacent_same_topic"] == 1
    balanced = interleave_sessions(
        {"cells": [{"q": "q1"}], "energy": [{"q": "q3"}]}, cards)
    assert balanced["adjacent_same_topic"] == 0
    kinds = [i["kind"] for i in session["items"]]
    assert kinds.count("quiz") == 3 and kinds.count("card") == 1


# 6. leitner ----------------------------------------------------------------

def test_leitner_boxes_promote_demote_and_stamp():
    card = build_cards([{"q": "Q?", "a": "A."}])[0]
    sched = LeitnerScheduler()
    state = sched.new_state()
    assert state == {"box": 1}
    state, r1 = leitner_review(card, state, 1, NOW)
    assert r1["scheduler"] == "leitner" and r1["box"] == 2
    assert r1["interval_days"] == 2.0
    assert "box 2" in r1["plain_language"]
    state, _r = leitner_review(card, state, 1, NOW)
    state, r3 = leitner_review(card, state, 0, NOW)
    assert r3["box"] == 1 and r3["interval_days"] == 1.0
    # top box holds at 5
    state = {"box": 5}
    _s, r5 = leitner_review(card, state, 1, NOW)
    assert r5["box"] == 5 and r5["interval_days"] == 14.0
    try:
        leitner_review(card, {"box": 1}, 3, NOW)
    except ValueError as e:
        assert "0 (missed) or 1 (knew it)" in str(e)
    else:
        raise AssertionError("leitner grade 3 must raise")
    due = datetime.fromisoformat(r1["due"].replace("Z", "+00:00"))
    assert due - NOW == timedelta(days=2)
