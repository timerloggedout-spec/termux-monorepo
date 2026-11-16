"""Second bundled sample course (#4593): the STAT 210 fixtures
ride the SAME pipeline as BIO 101 — ingest (evidence fetch)
-> plan (agent) -> SR (cards from the practice set) — with a
structurally different subject + assessment shape (problem
sets + final project, not quiz/lab/midterm). Content only:
no new code paths are exercised, which is the point.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent import run_agent  # noqa: E402
from study_sr import build_cards_from_practice_set, review_card  # noqa: E402
from study_tools import fetch_study_evidence  # noqa: E402

NOW = datetime(2026, 10, 30, tzinfo=timezone.utc)
SYL = {"kind": "syllabus", "ref": "examples/syllabus_stats.json"}
PS = {"kind": "practice_set", "ref": "examples/practice_set_stats.json"}


def test_stats_syllabus_evidence_stamped_and_material():
    ev = fetch_study_evidence(SYL, now=NOW, root=ROOT)
    assert ev["material"] is True
    claims = {it["claim"]: it["value"] for it in ev["items"]}
    assert claims["syllabus.weeks"] == 3
    assert claims["syllabus.week.1.topics"] == [
        "sampling and bias", "variables and measurement"]
    assert claims["syllabus.week.3.topics"] == [
        "the normal distribution", "sampling distributions"]
    assert all(it["sha256"] for it in ev["items"])


def test_stats_practice_set_evidence_hashes_questions():
    ev = fetch_study_evidence(PS, now=NOW, root=ROOT)
    assert ev["material"] is True
    claims = {it["claim"]: it["value"] for it in ev["items"]}
    assert claims["practice.questions"] == 2


def test_stats_agent_plans_on_fetched_syllabus():
    r = run_agent({"id": "s2", "action": "draft", "asserted": True,
                   "artifact": SYL, "missed_week": 1},
                  now=NOW, root=ROOT)
    assert r["decision_final"] == "ALLOW_RECOMMENDATION"
    assert r["plan"] is not None and r["plan"]["total_sessions"] > 0
    assert r["quiz"]["week"] == 1
    assert r["replan"] is not None
    assert r["deployment"] is False


def test_stats_agent_quiz_from_practice_set():
    r = run_agent({"id": "s4", "action": "draft", "asserted": True,
                   "artifact": PS},
                  now=NOW, root=ROOT)
    assert r["decision_final"] == "ALLOW_RECOMMENDATION"
    assert r["quiz"]["topic"] == "probability rules"
    assert len(r["quiz"]["questions"]) == 2
    assert r["quiz"]["questions"][0]["answer"].startswith(
        "Add the probabilities")


def test_stats_sr_cards_build_and_review():
    ps = json.loads((ROOT / PS["ref"]).read_text())
    cards = build_cards_from_practice_set(ps)
    assert len(cards) == 2
    assert all(c.front and c.back for c in cards)
    state = review_card(cards[0], None, 3)
    assert state is not None


def test_stats_readings_cover_the_syllabus_topics():
    syl = json.loads((ROOT / SYL["ref"]).read_text())
    readings = json.loads(
        (ROOT / "examples/readings_stats.json").read_text())
    topics = {t for w in syl["weeks"] for t in w["topics"]}
    assert set(readings) == topics
    assert all(len(v) > 200 for v in readings.values())


def test_stats_calendar_is_well_formed_for_the_geo_binding():
    cal = json.loads(
        (ROOT / "examples/calendar_stats.json").read_text())
    kinds = {a["kind"] for a in cal["assessments"]}
    assert kinds == {"problem set", "final project"}
    assert all(a["course"] == "STAT 210" for a in cal["assessments"])
    assert cal["origin"] in cal["coords"]
    assert all(w["location"] in cal["coords"]
               for w in cal["waypoints"])
