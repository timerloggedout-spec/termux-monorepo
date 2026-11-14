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
    assert budget == {"llm": 30}
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
    assert gate.parse_signals("null") == [] and gate.parse_signals("") == []
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


def test_run_defers_single_issue_on_rate_limit_and_still_updates_board(monkeypatch, tmp_path):
    """2026-10-23 board-stale finding: one 403/429 on a single RFP must defer only that
    RFP, and the results board must be regenerated before exit even when a rate limit
    happens mid-run (#1591 landed but board #1474 stayed one event behind)."""
    patched = []

    class FakeGH:
        def __init__(self, repo, token):
            self.calls = 0

        def req(self, method, path, body=None):
            self.calls += 1
            if method == "GET" and path.endswith("/rate_limit"):
                return {"resources": {"core": {"remaining": 5000}}}
            if method == "GET" and "labels=delphi:rfp" in path:
                return [{"number": 11, "title": "[delphi:rfp] turso.free", "labels": [{"name": "delphi:rfp"}],
                         "body": "### Surface id\n\nturso.free\n", "html_url": "https://github.com/x"},
                        {"number": 12, "title": "[delphi:rfp] render.free", "labels": [{"name": "delphi:rfp"}],
                         "body": "### Surface id\n\nrender.free\n", "html_url": "https://github.com/x"}]
            if method == "GET" and "labels=delphi:weights" in path:
                return []
            if method == "GET" and "labels=delphi:board" in path:
                return [{"number": 1474, "body": ""}]
            if method == "GET" and "/labels?per_page=100" in path:
                return [{"name": n} for n in gate.LABELS]
            if method == "GET" and path.startswith("/issues/11/comments"):
                return []
            if method == "POST" and path == "/issues/11/comments":
                raise gate.RateLimited("429 remaining=0 test")
            if method == "PATCH" and path == "/issues/1474":
                patched.append(body["body"])
                return {}
            return {}

    monkeypatch.setattr(gate, "GH", FakeGH)
    monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
    monkeypatch.setenv("GITHUB_TOKEN", "t")
    monkeypatch.setenv("GITHUB_REF_NAME", "master")
    monkeypatch.setenv("DELPHI_OUT", str(tmp_path / "out.jsonl"))

    class Args:
        reason = "test"
        depth = 0

    rc = gate.cmd_run(Args())
    assert rc == 0
    assert len(patched) == 1
    board_body = patched[0]
    assert board_body.startswith(gate.BOARD_MARK)
    # both open RFPs appear on the board: #11 deferred as pending, #12 still scored
    assert len([l for l in board_body.splitlines() if l.startswith("| #")]) == 2
    assert os.path.getsize(str(tmp_path / "out.jsonl")) > 0  # the non-rate-limited RFP was still scored


def test_tribute_signals_key_passthrough_and_cap():
    raw = json.dumps([{"surface": "tribute-lane", "repo": "a/b",
                       "outcome": "merged", "weight": 1,
                       "key": "https://github.com/a/b/issues/1"}])
    sigs = gate.parse_signals(raw)
    assert sigs[0]["key"] == "https://github.com/a/b/issues/1"
    many = json.dumps([{"surface": "tribute-lane", "repo": "a/b",
                        "outcome": "merged", "weight": 1}] * 250)
    assert len(gate.parse_signals(many)) == 200


def test_tribute_dedupe_is_idempotent_on_key_and_outcome():
    batch = [{"surface": "tribute-lane", "repo": "a/b", "outcome": "merged",
              "weight": 1.0, "key": "https://github.com/a/b/issues/1"},
             {"surface": "tribute-lane", "repo": "c/d", "outcome": "merged",
              "weight": 1.0}]  # unkeyed: never deduped
    kept, skipped, state = gate.dedupe_signals({"surfaces": {}}, batch)
    assert len(kept) == 2 and not skipped
    kept2, skipped2, state = gate.dedupe_signals(state, batch)
    assert len(kept2) == 1 and len(skipped2) == 1  # only the unkeyed flows again
    changed = [dict(batch[0], outcome="closed_already_assigned", weight=-0.6)]
    kept3, skipped3, _ = gate.dedupe_signals(state, changed)
    assert len(kept3) == 1 and not skipped3  # changed outcome = new signal


def test_tribute_batch_reweighting_is_damped_to_one_step():
    batch = [{"surface": "tribute-lane", "repo": "a/b", "outcome": "merged",
              "weight": 1.0}] * 9 + [
             {"surface": "tribute-lane", "repo": "a/b",
              "outcome": "hostile_spam_flag", "weight": -1.0}]
    st = gate.apply_outcomes({"surfaces": {}}, batch)
    t = st["surfaces"]["tribute-lane"]
    assert t["n"] == 10 and t["sum"] == 8.0  # tallies are per-signal facts
    # one EWMA step at the batch mean (0.8): 0.8*0 + 0.2*0.8 = 0.16,
    # NOT ten steps converging toward the weights
    assert t["ewma"] == 0.16
    assert t["repos"]["a/b"]["ewma"] == 0.16 and t["repos"]["a/b"]["n"] == 10


def test_ledger_issues_resolve_by_title_not_label_order():
    found = [{"number": 1567, "title": "[delphi:rfp] MVT-DoE/TLM: validate"},
             {"number": 1487, "title": "Delphi outcome ledger"},
             {"number": 1500, "title": "something else"}]
    assert gate.pick_ledger_issue(found, "Delphi outcome ledger") == 1487
    assert gate.pick_ledger_issue(found, "Delphi panel weights ledger") == 1567  # bootstrap fallback
    assert gate.pick_ledger_issue([], "Delphi outcome ledger") is None


def test_research_silo_parked_recheck_is_short():
    panel, reg, cat = _load()
    surf = {"id": "research.jogyo-research-lab", "title": "x", "lane": "other",
            "horizon": "H2", "registry_id": None, "sourced": False,
            "quota": {"metric": "", "limit": None, "unit": "", "window": "", "reset": "", "zone": "", "source": "x"},
            "auth": {"actions_secret": None, "present": None}, "lock_in": 1, "fit": 3, "headroom": 3,
            "failure_modes": [], "card_required": False, "overage_autobill": False}
    out = gate.score_surface(surf, panel, reg, None, "#0", "test")
    assert out["award"]["decision"] == "parked"
    import datetime as _dt
    ra = _dt.datetime.strptime(out["award"]["recheck_after"], "%Y-%m-%dT%H:%MZ")
    assert (_dt.datetime.utcnow() - ra).days >= -3  # <= ~2 days out, never ~30
    # quota surface keeps the long backlog cadence at the same score
    aw2 = gate.award({"effective_score": 6.69, "veto": False}, dict(surf, id="turso.free"), panel)
    ra2 = _dt.datetime.strptime(aw2["recheck_after"], "%Y-%m-%dT%H:%MZ")
    assert (ra2 - _dt.datetime.utcnow()).days >= 20


# ---------------------------------------------------------------- P3 (EGM-2): vote profiles, collision flags, quarantine guard

def _votes(**over):
    base = {"OPERATOR": (5, 4), "builder": (3, 5), "reviewer": (5, 3), "Scout": (5, 3), "cost_auditor": (4, 5)}
    base.update(over)
    return [{"role": r, "impact": i, "importance": j, "score": i * j, "veto": False} for r, (i, j) in base.items()]


def test_vote_profile_is_canonical_and_stable():
    v = _votes()
    p1 = gate.vote_profile(v)
    p2 = gate.vote_profile(list(reversed(v)))  # order-independent
    assert p1 == p2 and "OPERATOR=5x4" in p1 and "cost_auditor=4x5" in p1
    assert gate.vote_profile(None) is None and gate.vote_profile([]) is None
    assert gate.vote_profile(_votes(builder=(4, 5))) != p1


def test_board_flags_identical_profiles_inline():
    rows = [{"number": 101, "surface": "a.x", "effective": 12.0, "decision": "parked", "profile": gate.vote_profile(_votes())},
            {"number": 102, "surface": "b.y", "effective": 12.0, "decision": "parked", "profile": gate.vote_profile(_votes())},
            {"number": 103, "surface": "c.z", "effective": 9.0, "decision": "parked", "profile": gate.vote_profile(_votes(Scout=(4, 3)))}]
    md = gate.board_md(rows, "now")
    assert "Vote profile" in md
    assert "⚠ identical to #102" in md and "⚠ identical to #101" in md
    assert "identical vote profiles: #101 ≡ #102" in md
    line103 = [ln for ln in md.splitlines() if "#103" in ln][0]
    assert "⚠" not in line103


def test_quarantine_guard_matches_stamp_and_prefix_only():
    s = {"id": "some.surface"}
    assert gate.is_quarantined({"body": "text\nEGM instance #2 TEST filing\nmore"}, s)
    assert gate.is_quarantined({"body": "ordinary"}, {"id": "RFP-EGM2-B3"})
    assert not gate.is_quarantined({"body": "ordinary filing"}, s)
    assert not gate.is_quarantined({"body": None}, s)
    assert not gate.is_quarantined({}, s)


# ------------------------------------------------- P1+P2 (EGM-2): verification records, oracle resolution, B3 acceptance

def _fetch_from(states):
    def fetch(kind, ident):
        st = states.get((kind, ident))
        if st is None:
            raise LookupError(f"{kind} {ident}")
        if st == "INFRA":
            raise gate.InfraError("down")
        return st
    return fetch


def test_parse_verification_strict_grammar_cap_and_dedupe():
    text = ("Central claim rests on PR #4290 and run 41645713037.\n"
            "See also receipt 6603643325. Prose about PRs and runs is ignored.\n"
            "PR #4290 again (dupe). pr #4311 lower-case works.")
    cites = gate.parse_verification(text)
    assert cites == [{"kind": "pr", "id": 4290}, {"kind": "run", "id": 41645713037},
                     {"kind": "receipt", "id": 6603643325}, {"kind": "pr", "id": 4311}]
    many = " ".join(f"PR #{1000 + i}" for i in range(15))
    assert len(gate.parse_verification(many)) == gate.MAX_CITATIONS == 10
    assert gate.parse_verification("") == [] and gate.parse_verification("no refs at all") == []
    assert gate.parse_verification("run 123 too short") == []  # run ids need >= 6 digits


def test_verification_outcome_classes():
    fetch = _fetch_from({("pr", 1): {"merged": True, "state": "closed"},
                         ("pr", 2): {"merged": False, "state": "closed"},
                         ("pr", 3): {"merged": False, "state": "open"},
                         ("run", 100000): {"conclusion": "success"},
                         ("run", 200000): {"conclusion": "failure"},
                         ("receipt", 300000): {"exists": True},
                         ("pr", 4): "INFRA"})
    s = {"verification": {"citations": [{"kind": "pr", "id": 1}, {"kind": "pr", "id": 2}, {"kind": "pr", "id": 3},
                                        {"kind": "run", "id": 100000}, {"kind": "run", "id": 200000},
                                        {"kind": "receipt", "id": 300000}, {"kind": "receipt", "id": 999999},
                                        {"kind": "pr", "id": 4}]}}
    vb = gate.verification_block(s, fetch)
    assert vb["resolved"] and vb["tallies"] == {"verified": 4, "contradicted": 2, "unresolvable": 1, "unreachable": 1}


def test_unreachable_and_offline_are_neutral():
    s = {"verification": {"citations": [{"kind": "pr", "id": 4}]}}
    vb = gate.verification_block(s, _fetch_from({("pr", 4): "INFRA"}))
    assert vb["tallies"]["unreachable"] == 1 and vb["adjustment"] == 0.0
    off = gate.verification_block(s, None)
    assert off["resolved"] is False and off["adjustment"] == 0.0
    empty = gate.verification_block({"verification": {"citations": []}}, _fetch_from({}))
    assert empty["adjustment"] == 0.0


def test_b3_replica_fixture_scores_at_least_2_below_shape_only():
    """EGM-2 ACCEPTANCE (hard): a filing whose central cited claim resolves
    FALSE (its PR was closed unmerged) must score >= 2 pts below the score
    its shape alone earns."""
    panel, reg, _ = _load()
    s = {"id": "b3.replica", "title": "B3 replica fixture", "lane": "model", "horizon": "H2",
         "registry_id": None, "sourced": True,
         "quota": {"metric": "requests", "limit": 1000, "unit": "req", "window": "day",
                   "reset": "00:00 UTC", "zone": "UTC", "source": "https://example.com/limits"},
         "auth": {"actions_secret": None, "present": None},
         "lock_in": 1, "fit": 5, "headroom": 5, "failure_modes": [],
         "card_required": False, "overage_autobill": False,
         "verification": {"citations": [{"kind": "pr", "id": 777}]}}
    shape_only = gate.score_surface(dict(s), panel, reg, {}, "b3", "test")
    assert shape_only["result"]["verification"]["adjustment"] == 0.0  # offline: unresolved, neutral
    fetch = _fetch_from({("pr", 777): {"merged": False, "state": "closed"}})  # the claim resolves FALSE
    s2 = dict(s)
    s2["verification_block"] = gate.verification_block(s2, fetch)
    resolved = gate.score_surface(s2, panel, reg, {}, "b3", "test")
    assert resolved["result"]["verification"]["tallies"]["contradicted"] == 1
    assert resolved["result"]["shape_score"] == shape_only["result"]["effective_score"]
    assert resolved["result"]["effective_score"] <= shape_only["result"]["effective_score"] - 2.0


def test_verified_record_counts_for_filing_within_bounds():
    assert gate.verification_adjustment({"verified": 3, "contradicted": 0, "unresolvable": 0, "unreachable": 0}) == 2.0
    assert gate.verification_adjustment({"verified": 0, "contradicted": 1, "unresolvable": 0, "unreachable": 5}) == -4.0
    assert gate.verification_adjustment({"verified": 1, "contradicted": 1, "unresolvable": 0, "unreachable": 0}) == -1.0


# ------------------------------------------------- P4 (EGM-2): shadow substance score — reported, never merged, never governing

def _vb(v=0, c=0, u=0, r=0, resolved=True):
    return {"resolved": resolved, "citations": [],
            "tallies": {"verified": v, "contradicted": c, "unresolvable": u, "unreachable": r},
            "adjustment": gate.verification_adjustment({"verified": v, "contradicted": c, "unresolvable": u, "unreachable": r})}


def test_substance_score_deterministic_bounds_and_absence():
    assert gate.substance_score(_vb(v=3)) == 25.0
    assert gate.substance_score(_vb(c=1)) == 0.0
    assert gate.substance_score(_vb(v=1, c=1)) == 0.0
    assert gate.substance_score(_vb(v=2, u=1)) == round(25.0 * (2 - 1) / 3, 2)
    assert gate.substance_score(_vb(r=4)) is None           # all unreachable: no substance channel
    assert gate.substance_score(_vb()) is None              # no citations
    assert gate.substance_score(_vb(v=3, resolved=False)) is None  # offline unresolved
    assert gate.substance_score(None) is None


def test_substance_never_governs_the_award():
    panel, reg, _ = _load()
    s = {"id": "p4.shadow", "title": "P4 shadow fixture", "lane": "model", "horizon": "H2",
         "registry_id": None, "sourced": True,
         "quota": {"metric": "requests", "limit": 1000, "unit": "req", "window": "day",
                   "reset": "00:00 UTC", "zone": "UTC", "source": "https://example.com/limits"},
         "auth": {"actions_secret": None, "present": None},
         "lock_in": 1, "fit": 5, "headroom": 5, "failure_modes": [],
         "card_required": False, "overage_autobill": False,
         "verification": {"citations": [{"kind": "pr", "id": 42}]},
         "verification_block": _vb(v=1)}
    out = gate.score_surface(dict(s), panel, reg, {}, "p4", "test")
    assert out["result"]["substance_score"] == 25.0
    # the award is a pure function of the (P2-adjusted) effective score:
    # recomputing it from a result stripped of the substance score agrees
    stripped = {k: v for k, v in out["result"].items() if k != "substance_score"}
    assert gate.award(stripped, s, panel) == out["award"]


def test_board_renders_shadow_column_and_convergence_readout():
    prof = gate.vote_profile(_votes())
    rows = [{"number": 201, "surface": "a.x", "effective": 12.0, "decision": "parked", "profile": prof,
             "shape": 10.0, "substance": 25.0},
            {"number": 202, "surface": "b.y", "effective": 12.0, "decision": "parked", "profile": prof,
             "shape": 10.0, "substance": 0.0},
            {"number": 203, "surface": "c.z", "effective": 9.0, "decision": "parked", "profile": None,
             "shape": 11.0, "substance": 12.5}]
    md = gate.board_md(rows, "now")
    assert "Substance (shadow) /25" in md
    assert "P4 shadow convergence (last-3 cohort)" in md
    assert "median |shape−substance| = 10.0" in md  # median of 15, 10, 1.5 = 10
    assert "identical-profile rate 100.0%" in md    # both profiled rows collide
    assert "never merged" in md
    conv = gate.convergence(rows)
    assert conv["cohort"] == 3 and conv["median_gap"] == 10.0
    assert gate.convergence([{"number": 1, "surface": "x", "effective": 1.0, "decision": "pending"}]) is None
