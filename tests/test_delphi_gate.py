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
        assert v["signed"].startswith("Signed-off-
by: Delphi-") and "(OPERATOR) s1 / #1#r" in v["signed"]
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


def test_model_ballots_disabled_even_with_keys_and_legacy_opt_in(monkeypatch):
    monkeypatch.setenv("DELPHI_PANEL", "llm")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-not-a-key")
    monkeypatch.setenv("GEMINI_API_KEY", "test-not-a-key")
    monkeypatch.setenv("DELPHI_LLM_MAX", "30")
    def forbidden(*args, **kwargs):
        raise AssertionError("No provider request is authorized by a role or key")
    monkeypatch.setattr(gate.urllib.request, "urlopen", forbidden)
    panel, reg, cat = _load()
    budget = {"llm": 30}
    assert gate.llm_vote("Scout", cat["openrouter.free"], "", budget) is None
    assert budget == {"
llm": 30}
    result = gate.delphi(cat["openrouter.free"], panel, budget=budget)
    assert all(v["via"] == "rubric" for r in result["rounds"] for v in r["votes"])


def test_workflow_never_passes_provider_credentials_to_delphi():
    from pathlib import Path
    text = (Path(ROOT) / ".github/workflows/delphi-gate.yml").read_text()
    assert "DELPHI_PANEL: rubric" in text
    assert 'DELPHI_LLM_MAX: "0"' in text
    assert "secrets.OPENROUTER_API_KEY" not in text
    assert "secrets.GEMINI_API_KEY" not in text


def test_cadence_reads_live_shared_token_budget():
    _, reg, _ = _load()
    assert gate.cadence(reg, {}, 3, 0, api_remaining=50)["mode"] == "defer_api"
    tight = gate.cadence(reg, {}, 3, 0, api_remaining=130)
    assert tight["mode"] == "steady" and tight["max_rfps_per_run"] == 5
    assert gate.cadence(reg, {"neon": 1.8}, 3, 0, api_remaining=200)["mode"] == "steady"  # no chaining below half budget
    assert gate.cadence(reg, {"neon": 1.8}, 3, 0, api_remaining=900)["mode"] == "accelerate"
    assert gate.cadence(reg, {}, 3, 0, api_remaining=None)["mode"] == "steady"  # unreadable = neutral


def test_results_board_orders_and_counts():
    rows = [{"number": 2, "surface": "b", "effective": 9.0, "decision": "parked", "band": "Medium", "recheck": "x"},
            {"number": 1, "surface": "a", "effective": 18.5, "decision": "shadow", "band": "High", "recheck": None},
            {"number": 3, "surface": "c", "effective": None, "decision": "pending"}]
    md = gate.board_md(rows, "t")
    assert md.startswith(gate.BOARD_MARK)
    body = md.splitlines()
    assert body.index(next(l for l in body if "`a`" in l)) < body.index(next(l for l in body if "`b`" in l))
    assert "1 shadow · 1 parked · 1 pending" in md


def test_radar_lists_only_uncovered_surfaces(tmp_path):
    _, reg, cat = _load()
    fs = tmp_path / "fs.jsonl"
    fs.write_text(json.dumps({"resource_id": "new-thing", "category": "data", "canonical_source": "https://example.com"}) + "\n")
    
radar = gate.radar_candidates(cat, reg, set(cat), str(fs))
    ids = {c["id"] for c in radar}
    assert "new-thing" in ids
    covered = {s["registry_id"] for s in cat.values() if s.get("registry_id")}
    assert not ids & covered and not ids & set(cat)
    assert "Radar:" in gate.board_md([], "t", radar)


def test_shadow_outcome_decisions():
    from scripts.delphi import signals
    sh = {"delphi:shadow"}
    assert signals.decide(["success"] * 3, sh) == "confirmed"
    assert signals.decide(["success"] * 3, sh | {"delphi:promoted"}) is None
    assert signals.decide(["failure", "success", "success"], sh) == "miss"
    assert signals.decide(["failure", "failure", "success"], sh) is None  # only on the transition
    assert signals.decide(["success"] * 3, {"delphi:parked"}) is None
    lanes = gate.load(signals.LANES)
    assert signals.lanes_for("delphi-gate", lanes) == ["1424"]
    assert signals.lanes_for("anything-else", lanes) == []


def test_bridge_is_event_driven_and_keyless():
    from pathlib import Path
    text = (Path(ROOT) / ".github/workflows/delphi-signal-bridge.yml").read_text()
    assert "schedule:" not in text and "${{ secrets" not in text
    assert "./.github/workflows/delphi-signal.yml" in text


def test_tribute_signals_parse_and_ewma():
    raw = json.dumps([{"surface": "tribute-lane", "repo": "a/b", "outcome": "merged", "weight": 1},
                      {"surface": "tribute-lane", "repo": "a/b", "outcome": "hostile_spam_flag", "weight": -1},
                      {"surface": "Bad Surface", "repo": "a/b", "outcome": "merged", "weight": 1},
                      {"surface": "tribute-lane", "repo": "not a repo", "outcome": "merged", "weight": 1},
                      {"surface": "tribute-lane", "repo": "c/d", "outcome": "merged", "weight": 3}])
    sigs = gate.parse_signals(raw)
    assert len(sigs) == 2
    assert gate.parse_signals(json.dumps({"surface": "tribute-lane", "repo": "x/y", "outcome": "approved"}))[0]["weight"] == 0.5
    as
sert gate.parse_signals("null") == [] and gate.parse_signals("") == []
    st = gate.apply_outcomes({"surfaces": {}}, sigs)
    t = st["surfaces"]["tribute-lane"]
    assert t["n"] == 2 and t["sum"] == 0 and t["repos"]["a/b"]["n"] == 2 and t["repos"]["a/b"]["last"] == "hostile_spam_flag"


def test_graded_feedback_and_quantized_hash():
    panel, reg, cat = _load()
    votes = [{"role": r, "score": 20 if r == "OPERATOR" else 5} for r in gate.ROLES]
    up = gate.feedback_graded(panel["roles"], votes, 1.0, panel)
    assert up["OPERATOR"]["elo"] > 1500 and up["builder"]["elo"] < 1500
    down = gate.feedback_graded(panel["roles"], votes, -1.0, panel)
    assert down["OPERATOR"]["elo"] < 1500 and down["builder"]["elo"] > 1500
    assert gate.feedback_graded(panel["roles"], votes, 0.0, panel) == panel["roles"]
    tiny = gate.feedback_graded(panel["roles"], votes, 0.1, panel)  # one small signal does not re-score the queue
    s = cat["turso.free"]
    assert gate.input_hash(s, tiny, reg, {}) == gate.input_hash(s, panel["roles"], reg, {})
    assert "tribute-lane" in cat
