"""Delphi Oracle RFP gate: offline, stdlib-only tests (no network, no secrets)."""
import json, os

from scripts.delphi import gate

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _load():
    return gate.load(gate.PANEL), gate.load(gate.REGISTRY), {s["id"]: s for s in gate.load(gate.SURFACES)["surfaces"]}


def test_catalog_is_sourced_or_null():
    _, _, cat = _load()
    assert len(cat) >= 17
    for s in cat.values():
        q = s["quota"]
        assert q["source"].startswith("http"), s["id"]
        if not s["sourced"]:
            # unsourced surfaces may carry a number only when the repo doc states it
            assert q["limit"] is None or "PARTNERS" in q["source"], s["id"]


def test_effective_score_is_weighted_mean():
    panel, _, _ = _load()
    votes = [{"role": r, "score": 10} for r in gate.ROLES]
    assert gate.effective(votes, panel["roles"]) == 10
    roles = json.loads(json.dumps(panel["roles"]))
    roles["OPERATOR"]["elo"] = 3000  # doubles OPERATOR weight
    votes[0]["score"] = 20
    assert gate.effective(votes, roles) > gate.effective(votes, panel["roles"])


def test_money_veto_parks():
    panel, reg, cat = _load()
    out = gate.score_surface(cat["cellcog.credits"], panel, reg, {}, "t", "test")
    assert out["result"]["veto"] and out["award"]["decision"] == "parked"
    assert "recheck_after" in out["award"]


def test_rounds_share_only_aggregates_and_stop():
    panel, reg, cat = _load()
    res = gate.delphi(cat["github.native_ledger"], panel)
    assert 1 <= len(res["rounds"]) <= panel["rounds"]["max"]
    for h in res["rounds"]:
        assert set(h) >= {"median", "iqr", "outlier_reasons"}
        assert all(isinstance(x, str) for x in h["outlier_reasons"])  # anonymous: reasons only, no roles


def test_votes_are_signed():
    panel, reg, cat = _load()
    res = gate.delphi(cat["turso.free"], panel, "#1", "s1")
    for v in res["rounds"][-1]["votes"]:
        assert v["signed"].startswith("Signed-off-by: Delphi-") and "(OPERATOR) s1 / #1#r" in v["signed"]
        assert len(v["sha256"]) == 16


def test_flywheel_reweights():
    panel, _, _ = _load()
    votes = [{"role": r, "score": 20 if r == "OPERATOR" else 5} for r in gate.ROLES]
    new = gate.feedback(panel["roles"], votes, "confirmed", panel)
    assert new["OPERATOR"]["elo"] > panel["roles"]["OPERATOR"]["elo"]
    assert new["builder"]["gate_pass_rate"] < panel["roles"]["builder"]["gate_pass_rate"]


def test_cadence_bounds():
    _, reg, _ = _load()
    assert gate.cadence(reg, {"neon": 1.8}, pending=3, depth=0)["mode"] == "accelerate"
    assert gate.cadence(reg, {"neon": 1.8}, pending=3, depth=3)["mode"] == "steady"  # chain cap
    assert gate.cadence(reg, {"vercel": 0.1}, pending=3, depth=0)["mode"] == "defer"
    assert gate.cadence(reg, {}, pending=3, depth=0)["mode"] == "steady"  # no live reading = neutral
    assert gate.cadence(reg, {}, 0, 0)["max_rfps_per_run"] >= 1


def test_parse_issue_form():
    body = "### Surface id\n\nturso.free\n\n### Lane\n\ndata\n\n### Failure modes\n\n_No response_"
    f = gate.parse_form(body)
    assert f["surface_id"] == "turso.free" and f["failure_modes"] == ""
    _, _, cat = _load()
    s = gate.surface_from_issue({"number": 9, "title": "x", "body": body, "html_url": "https://github.com/x"}, cat)
    assert s["id"] == "turso.free"
