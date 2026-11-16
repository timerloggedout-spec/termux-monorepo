"""StudySprint — D1 entry agent (Strands-wired, D0-foundation).

Starting agent (stated, per the D0/D1 submission pattern): the Delphi
Oracle evidence gate from the D0 completion package — a deterministic
oracle (`foundation/oracle_kernel.py`, vendored verbatim, blob
9a4a1c78) that judges a proposed action against an evidence set and
returns ALLOW_RECOMMENDATION / ABSTAIN / ESCALATE, failing closed, with
the D0 tool `fetch_evidence` (`foundation/fetch_evidence.py`, verbatim)
for read-only artifact retrieval.

What StudySprint adds (this build, original + unpublished):
- G2 study artifact kinds (`study_tools.fetch_study_evidence`):
  syllabus + practice_set evidence sets in the D0 stamped shape.
- The StudySprint tools: build_study_plan / generate_quiz /
  replan_on_missed — for first-gen college students: syllabus ->
  week-by-week plan, daily recall quizzes, re-plans on missed weeks.
- Strands wiring: when the Strands Agents SDK is installed, the tools
  are registered on a `strands.Agent` (see `build_strands_agent`); the
  deterministic gate loop below is the offline execution path and the
  receipt contract either way. No model call is made in the offline
  path and none is claimed in its receipts (`deployment: False`).

Loop (the D0 pattern, domain-shifted): judge the plan request on
asserted evidence (ABSTAIN — a claim about a course is not a syllabus)
-> fetch the syllabus evidence set -> judge again -> only on
ALLOW_RECOMMENDATION build the plan/quiz. Consequential actions
ESCALATE before evidence is weighed, exactly as in D0.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "foundation"))

from oracle_kernel import deterministic_oracle  # noqa: E402  (vendored, G1)
from study_tools import (  # noqa: E402
    PRIVACY_STATEMENT, build_study_plan, fetch_study_evidence,
    format_accessible_status, format_trust_receipt, generate_quiz,
    plain_language_action, record_daily_checkin, reflow_plan_budget,
    render_today_view, replan_on_missed,
)

RECEIPT_SCHEMA = "studysprint-agent-receipt/v1"


def _agent_version() -> str:
    """Version of record: the repo-root VERSION file (VERSIONING.md)."""
    try:
        return (Path(__file__).resolve().parent / "VERSION") \
            .read_text().strip()
    except OSError:
        return "unknown"


AGENT_VERSION = _agent_version()


def build_strands_agent():
    """Register StudySprint's tools on a Strands Agent when available.

    Returns None when the Strands Agents SDK is not installed — the
    offline gate loop in `run_agent` is then the execution path. The
    workshop (D1 gate, completed 2026-10-30) exercised this same SDK
    surface in the Builder sandbox (Modules 1-7, all EXIT:0).
    """
    try:
        from strands import Agent, tool
    except ImportError:
        return None

    @tool
    def fetch_syllabus_evidence(ref: str) -> str:
        """Fetch a stamped evidence set for a syllabus file."""
        return json.dumps(fetch_study_evidence(
            {"kind": "syllabus", "ref": ref})["items"])

    @tool
    def make_plan(course_json: str) -> str:
        """Build a week-by-week study plan from a syllabus document."""
        return json.dumps(build_study_plan(json.loads(course_json)))

    @tool
    def make_quiz(course_json: str, week: int) -> str:
        """Generate recall questions for one syllabus week."""
        return json.dumps(generate_quiz(json.loads(course_json), week))

    @tool
    def replan(plan_json: str, missed_week: int) -> str:
        """Fold a missed week's sessions into the next week."""
        return json.dumps(replan_on_missed(json.loads(plan_json), missed_week))

    @tool
    def get_today_view(plan_json: str, day_index: int = 0) -> str:
        """Render the single today-view card for daily study loop."""
        return json.dumps(render_today_view(json.loads(plan_json), day_index))

    @tool
    def adjust_time_budget(plan_json: str, minutes_per_day: int) -> str:
        """Re-flow study plan sessions around available daily time budget."""
        return json.dumps(reflow_plan_budget(json.loads(plan_json), minutes_per_day))

    @tool
    def checkin_session(log_json: str, week: int, session_index: int, status: str) -> str:
        """Log a daily check-in (done/partial/missed) tracking recovered weeks."""
        return json.dumps(record_daily_checkin(json.loads(log_json), week, session_index, status))

    return Agent(tools=[fetch_syllabus_evidence, make_plan, make_quiz,
                        replan, get_today_view, adjust_time_budget,
                        checkin_session],
                 system_prompt="You are StudySprint: turn a verified "
                               "syllabus into a study plan a first-gen "
                               "student can trust. Never plan from a "
                               "claimed syllabus — fetch evidence first.")


def _case(request: dict, evidence_refs: list[str], material: bool) -> dict:
    return {
        "id": request["id"],
        "action": request["action"],
        "risk_tier": request.get("risk_tier", "standard"),
        "evidence_refs": evidence_refs,
        "evidence_material": material,
        "untrusted_instruction": False,
    }


def run_agent(request: dict, now: datetime | None = None,
              root: Path | None = None) -> dict:
    """Run one StudySprint request through the D0 gate + tool loop.

    request: {"id", "action", "asserted": bool,
              "artifact": {"kind": "syllabus"|"practice_set",
                           "ref": path} | absent,
              "missed_week": int | absent}
    """
    now = now or datetime.now(timezone.utc)

    asserted_refs = [f"asserted:{request['id']}"] if request.get("asserted") else []
    decision_asserted = deterministic_oracle(
        _case(request, asserted_refs, material=False))

    evidence_set = None
    decision_final = decision_asserted
    plan = quiz = replan = None
    if request.get("artifact"):
        evidence_set = fetch_study_evidence(request["artifact"], now=now,
                                            root=root)
        fetched_refs = [it["provenance"]["path"] for it in evidence_set["items"]]
        decision_final = deterministic_oracle(
            _case(request, fetched_refs, material=evidence_set["material"]))
        if decision_final == "ALLOW_RECOMMENDATION" and \
                request["artifact"]["kind"] == "syllabus":
            doc = evidence_set["document"]
            plan = build_study_plan(doc)
            first_week = (doc.get("weeks") or [{}])[0].get("week")
            if first_week is not None:
                quiz = generate_quiz(doc, first_week)
            if request.get("missed_week") is not None:
                replan = replan_on_missed(plan, request["missed_week"])
        elif decision_final == "ALLOW_RECOMMENDATION" and \
                request["artifact"]["kind"] == "practice_set":
            doc = evidence_set["document"]
            quiz = {"topic": doc.get("topic"),
                    "questions": [{"topic": doc.get("topic"),
                                   "prompt": q.get("q"),
                                   "answer": q.get("a")}
                                  for q in doc.get("questions") or []]}

    # Surface Now items: trust receipt, today view, accessible status, plain language
    trust_receipt = None
    today_view = None
    if evidence_set and evidence_set.get("artifact", {}).get("kind") == "syllabus":
        trust_receipt = format_trust_receipt(evidence_set)
    if plan:
        # If student specified minutes_per_day, re-flow budget
        if request.get("minutes_per_day"):
            plan = reflow_plan_budget(plan, request["minutes_per_day"])
        today_view = render_today_view(plan, day_index=request.get("day_index", 0))

    action_explanation = plain_language_action(
        "replan" if replan else ("syllabus_verified" if plan else ("practice_quiz" if quiz else "generic")),
        {"course": plan.get("course") if plan else None,
         "missed_week": request.get("missed_week"),
         "target_week": (request["missed_week"] + 1) if request.get("missed_week") is not None else None}
    )

    receipt = {
        "schema": RECEIPT_SCHEMA,
        "agent_version": AGENT_VERSION,
        "request_id": request["id"],
        "action": request["action"],
        "decision_on_asserted_evidence": decision_asserted,
        "decision_final": decision_final,
        "decision_accessible": format_accessible_status(decision_final),
        "plain_language_explanation": action_explanation,
        "trust_receipt": trust_receipt,
        "evidence_set": ({k: v for k, v in evidence_set.items()
                          if k != "document"} if evidence_set else None),
        "plan": plan,
        "today_view": today_view,
        "quiz": quiz,
        "replan": replan,
        "privacy": PRIVACY_STATEMENT,
        "tool_calls": {"fetch_study_evidence": 1 if evidence_set else 0},
        "strands_agent_available": build_strands_agent() is not None,
        "deployment": False,
        "generated_at": now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    receipt["receipt_sha256"] = hashlib.sha256(
        json.dumps(receipt, sort_keys=True).encode()).hexdigest()
    return receipt
