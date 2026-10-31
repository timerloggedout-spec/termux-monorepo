"""Offline tests for StudySprint: G2 kinds + G3 gate loop. No network."""

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent import run_agent  # noqa: E402
from study_tools import fetch_study_evidence  # noqa: E402

NOW = datetime(2026, 10, 30, tzinfo=timezone.utc)


def test_syllabus_evidence_stamped_and_material():
    ev = fetch_study_evidence({"kind": "syllabus",
                               "ref": "examples/syllabus.json"},
                              now=NOW, root=ROOT)
    assert ev["material"] is True
    assert ev["fresh_until"] == "2026-10-30T00:15:00Z"
    claims = {it["claim"]: it["value"] for it in ev["items"]}
    assert claims["syllabus.weeks"] == 3
    assert claims["syllabus.week.2.topics"] == ["photosynthesis", "respiration"]
    assert all(it["sha256"] for it in ev["items"])


def test_practice_set_evidence_hashes_questions():
    ev = fetch_study_evidence({"kind": "practice_set",
                               "ref": "examples/practice_set.json"},
                              now=NOW, root=ROOT)
    assert ev["material"] is True
    claims = {it["claim"]: it["value"] for it in ev["items"]}
    assert claims["practice.questions"] == 2


def test_agent_abstains_on_asserted_only():
    r = run_agent({"id": "t1", "action": "draft", "asserted": True},
                  now=NOW, root=ROOT)
    assert r["decision_on_asserted_evidence"] == "ABSTAIN"
    assert r["decision_final"] == "ABSTAIN"
    assert r["plan"] is None


def test_agent_plans_on_fetched_syllabus():
    r = run_agent({"id": "t2", "action": "draft", "asserted": True,
                   "artifact": {"kind": "syllabus",
                                "ref": "examples/syllabus.json"},
                   "missed_week": 1},
                  now=NOW, root=ROOT)
    assert r["decision_final"] == "ALLOW_RECOMMENDATION"
    assert r["plan"]["total_sessions"] == 12
    assert r["quiz"]["week"] == 1 and len(r["quiz"]["questions"]) == 2
    assert r["replan"]["carried_sessions"] == 4
    assert r["deployment"] is False


def test_agent_quiz_from_practice_set():
    r = run_agent({"id": "t4", "action": "draft", "asserted": True,
                   "artifact": {"kind": "practice_set",
                                "ref": "examples/practice_set.json"}},
                  now=NOW, root=ROOT)
    assert r["decision_final"] == "ALLOW_RECOMMENDATION"
    assert r["plan"] is None
    assert r["quiz"]["topic"] == "cell structure"
    assert len(r["quiz"]["questions"]) == 2
    assert r["quiz"]["questions"][0]["answer"].startswith("Controls")


def test_receipt_carries_version_of_record():
    r = run_agent({"id": "t5", "action": "draft", "asserted": True},
                  now=NOW, root=ROOT)
    version_file = (ROOT / "VERSION").read_text().strip()
    assert r["agent_version"] == version_file
    assert r["agent_version"] == "0.1.0"


def test_agent_escalates_consequential():
    r = run_agent({"id": "t3", "action": "credential_mutation",
                   "risk_tier": "consequential", "asserted": True,
                   "artifact": {"kind": "syllabus",
                                "ref": "examples/syllabus.json"}},
                  now=NOW, root=ROOT)
    assert r["decision_final"] == "ESCALATE"
    assert r["plan"] is None
