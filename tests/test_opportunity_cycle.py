"""Tests for scripts/opportunities/opportunity_cycle.py (#5096 / #5103).

Stdlib + pytest only; fixtures are tiny synthetic repo roots in tmp dirs.
Each test maps to a done-evidence case in docs/ops/OPPORTUNITY-CYCLE.md.
"""
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "opportunities" / "opportunity_cycle.py"
spec = importlib.util.spec_from_file_location("opportunity_cycle", SCRIPT)
oc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oc)

NOW = datetime(2026, 11, 10, 0, 0, 0, tzinfo=timezone.utc)
WALL = "2026-11-20T23:59:00-08:00"


def _write(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(obj, str):
        path.write_text(obj, encoding="utf-8")
    else:
        path.write_text(json.dumps(obj), encoding="utf-8")


def build_root(tmp: Path) -> Path:
    """A minimal repo root: E1 (live, fully prepped), E2 (closed),
    C1 (screened out), C2 (live candidate, mid gate), C3 (live candidate,
    no dates)."""
    root = tmp / "repo"
    ev1 = {
        "id": "E1", "name": "Test Event One", "status": "active",
        "dates": {"deadline": {"at": WALL, "tz": "America/Los_Angeles"}},
        "prizes": {"status": "ESTABLISHED", "pool": "$1,000"},
    }
    ev2 = {"id": "E2", "name": "Closed Event", "status": "closed",
           "dates": {}, "prizes": {}}
    cand1 = {"id": "C1", "name": "Screened", "status": "SCREENED OUT this cycle — FAIL eligibility",
             "dates": {"proposal_due": "2026-11-12T23:59:00-08:00"}}
    cand2 = {"id": "C2", "name": "Candidate Two", "status": "candidate — VIABLE",
             "dates": {"proposal_due": "2026-11-25T23:59:00-08:00"},
             "prizes": {"per_project": "$10"}}
    cand3 = {"id": "C3", "name": "Dateless Watch", "status": "watch"}
    _write(root / "ops/challenge/coordinator.json",
           {"events": [ev1, ev2], "candidate_events": [cand1, cand2, cand3]})
    _write(root / "ops/challenge/opportunity_ledger.json",
           {"entries": [{"id": "OC-100", "event": "E1 — Test Event One", "status": "AT_RISK"}]})
    _write(root / "ops/challenge/osint/coverage.json",
           {"events": {"E1": {"organizers": {"populated": True}}}})
    _write(root / "ops/challenge/osint/snapshots.json",
           {"snapshots": [{"event": "E1", "fetched_at": "2026-11-09", "sha256": "ab12"}]})
    _write(root / "ops/challenge-recruitment/podium-dataset--2026-11-01.v1.json",
           {"version": "2026-11-01.v1", "schema": "challenge-recruitment/podium-dataset-of-record/v1"})
    _write(root / "ops/agentic-gambling/book/challenges-book.json",
           {"subjects": [{"id": "E1-1-submission", "subject": "E1 submission lands",
                          "knowable": "2026-11-20", "settle": {"state": "INTAKE"},
                          "expectation_record": {"posterior": {"value": None}}}],
            "settlements": []})
    _write(root / "experiments/doe/panel-judge-mirror/forecasts/2026-11-01-e1-test.json",
           {"forecast_id": "pjm-test-e1", "filed_at": "2026-11-01",
            "stamp": {"grade": "venue-archetype"},
            "forecast": {"expected_panel_score": 50.0,
                         "outcome_probabilities": {"podium": 0.1}}})
    # E1 prep artifacts
    _write(root / "entries/e1/spec.md", "spec")
    _write(root / "docs/tak.md", "tak tracks")
    _write(root / "docs/swot.md", "swot")
    _write(root / "entries/e1/prep-manifest.json", {
        "schema": "opportunity-prep-manifest/v1", "entry": "E1", "slug": "e1",
        "stages": {
            "0": {"artifact": "entries/e1/spec.md", "receipt_ref": "test spec"},
            "1": {"artifact": "ops/challenge/osint/coverage.json", "receipt_ref": "osint"},
            "2": {"artifact": "ops/challenge-recruitment/podium-dataset--2026-11-01.v1.json",
                  "receipt_ref": "dataset"},
            "3": {"artifact": "docs/tak.md", "receipt_ref": "tak"},
            "4": {"artifact": "docs/swot.md", "receipt_ref": "swot"},
        }})
    _write(root / "entries/e1/submission-requirements.json", valid_census())
    return root


def valid_census():
    return {"schema": "opportunity-submission-requirements/v1", "entry": "E1",
            "requirements": [
                {"id": "auto-form", "requirement": "Submit the form", "class": "automatable",
                 "landing_time": "2026-11-19T00:00:00-08:00", "submit_once": False,
                 "route_around": {"sought": False, "alternative": None}},
                {"id": "fleet-upload", "requirement": "Upload the artifact",
                 "class": "fleet-executable", "landing_time": "2026-11-19T12:00:00-08:00",
                 "submit_once": True, "discharged": True, "first_send_verified": True,
                 "route_around": {"sought": True, "alternative": "channel route"}},
            ]}


def run(root: Path, tmp: Path):
    out = tmp / "out"
    return oc.run_cycle(root, cycles_dir=out / "cycles",
                        cycle_ledger=out / "ledger.jsonl",
                        feed_out=out / "feed.json", now=NOW, run_id="testrun")


def opp(receipt, opp_id):
    return next(o for o in receipt["opportunities"] if o["id"] == opp_id)


# (a) complete prep -> COMPLETE, tier ts > prep ts
def test_a_complete_prep_completes_with_ordering(tmp_path):
    root = build_root(tmp_path)
    receipt = run(root, tmp_path)
    e1 = opp(receipt, "E1")
    assert e1["verdict"] == "COMPLETE"
    assert e1["prep_gate"]["state"] == "PASS"
    verified_at = e1["prep_gate"]["verified_at"]
    assert verified_at is not None
    assert e1["tier_actions"], "expected tier actions"
    assert all(a["ts"] > verified_at for a in e1["tier_actions"])
    assert e1["stages"]["5"]["state"] == "RECEIPTED"
    assert e1["stages"]["6"]["state"] == "RECEIPTED"
    assert e1["stages"]["7"]["state"] == "PENDING"  # no settlements yet
    assert e1["selection"]["selected"] in oc.COMPLETION_LEGS
    # outputs landed
    assert Path(receipt["_paths"]["receipt"]).is_file()
    feed = json.loads(Path(receipt["_paths"]["feed"]).read_text())
    assert feed["schema"] == "que.opportunity-priority/v1"


# (b) census missing -> PREP_INCOMPLETE + tier_actions []
def test_b_missing_census_blocks(tmp_path):
    root = build_root(tmp_path)
    (root / "entries/e1/submission-requirements.json").unlink()
    receipt = run(root, tmp_path)
    e1 = opp(receipt, "E1")
    assert e1["verdict"] == "PREP_INCOMPLETE"
    assert e1["prep_gate"]["census"]["state"] == "MISSING"
    assert e1["tier_actions"] == []
    assert e1["stages"]["5"]["state"] == "blocked_prep_incomplete"


# (c) owner-hand without capacity_verified blocks
def test_c_owner_hand_unverified_blocks(tmp_path):
    root = build_root(tmp_path)
    census = valid_census()
    census["requirements"].append(
        {"id": "owner-click", "requirement": "Owner clicks", "class": "owner-hand",
         "capacity_verified": False, "landing_time": "2026-11-19T00:00:00-08:00",
         "submit_once": False, "route_around": {"sought": True, "alternative": "none_found"}})
    _write(root / "entries/e1/submission-requirements.json", census)
    e1 = opp(run(root, tmp_path), "E1")
    assert e1["verdict"] == "PREP_INCOMPLETE"
    assert any("capacity_verified" in v for v in e1["prep_gate"]["census"]["violations"])


# (d) non-automatable without route_around.sought blocks
def test_d_missing_route_around_blocks(tmp_path):
    root = build_root(tmp_path)
    census = valid_census()
    census["requirements"][1]["route_around"] = {"sought": False, "alternative": None}
    _write(root / "entries/e1/submission-requirements.json", census)
    e1 = opp(run(root, tmp_path), "E1")
    assert e1["verdict"] == "PREP_INCOMPLETE"
    assert any("route_around" in v for v in e1["prep_gate"]["census"]["violations"])


# (e) landing_time after the wall blocks
def test_e_landing_after_wall_blocks(tmp_path):
    root = build_root(tmp_path)
    census = valid_census()
    census["requirements"][0]["landing_time"] = "2026-11-21T00:00:00-08:00"
    _write(root / "entries/e1/submission-requirements.json", census)
    e1 = opp(run(root, tmp_path), "E1")
    assert e1["verdict"] == "PREP_INCOMPLETE"
    assert any("after wall" in v for v in e1["prep_gate"]["census"]["violations"])


# (f) screened-out candidates and closed events are excluded from ingest
def test_f_exclusions(tmp_path):
    root = build_root(tmp_path)
    receipt = run(root, tmp_path)
    ids = [i["id"] for i in receipt["ingest"]]
    assert "E2" not in ids and "C1" not in ids
    assert set(ids) == {"E1", "C2", "C3"}


# (g) priority order = ascending next_gate; NOT_ESTABLISHED gates last
def test_g_priority_order(tmp_path):
    root = build_root(tmp_path)
    receipt = run(root, tmp_path)
    order = [o["id"] for o in sorted(receipt["opportunities"],
                                     key=lambda o: o["priority_stamp"]["rank"])]
    assert order == ["E1", "C2", "C3"]  # Nov 20 < Nov 25 < NOT_ESTABLISHED
    c3 = opp(receipt, "C3")
    assert c3["priority_stamp"]["next_gate"] == "NOT_ESTABLISHED"


# (h) missing manifest artifact -> stage NOT_ESTABLISHED, gap named
def test_h_missing_artifact_is_named_not_fabricated(tmp_path):
    root = build_root(tmp_path)
    manifest = json.loads((root / "entries/e1/prep-manifest.json").read_text())
    manifest["stages"]["3"]["artifact"] = "docs/does-not-exist.md"
    _write(root / "entries/e1/prep-manifest.json", manifest)
    e1 = opp(run(root, tmp_path), "E1")
    stage3 = e1["prep_gate"]["stages"]["3"]
    assert stage3["state"] == "NOT_ESTABLISHED"
    assert "docs/does-not-exist.md" in stage3["gap"]
    assert e1["verdict"] == "PREP_INCOMPLETE"
    assert e1["tier_actions"] == []
