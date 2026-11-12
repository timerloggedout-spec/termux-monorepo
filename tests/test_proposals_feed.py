"""Collector pins for the proposals index feed (proposals-feed/v2).

The collector reads the registry of record and the pass records and
carries their values verbatim. The YAML subset fallback parser is
differential-tested against PyYAML so the feed never depends on which
parser ran.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "proposals"))

import proposals_feed as pf  # noqa: E402

FIXTURE = """# fixture registry
version: 1
updated_at: "2026-10-28T00:00:00Z"
updated_by: test

proposals:
  - id: alpha-pack
    title: "Alpha: the first pack"
    author: grok
    status: posted
    priority: P1
    path: active/alpha-pack/
    proposal_type: research
    reviewers:
      - id: timerloggedout-spec
        role: operator-authorizer
        status: requested
    related_issues: [175, 772]
    related_prs: []
    gates_required: [repo-gate, termux-smoke]

  - id: beta-pack
    title: "Beta pack"
    author: ChatGPT
    status: executing
    priority: P0
    path: active/beta-pack/
    related_prs: [42]
"""


def test_subset_parser_matches_pyyaml_on_fixture():
    yaml = __import__("yaml")
    a = yaml.safe_load(FIXTURE)
    b = pf.parse_registry_subset(FIXTURE)
    assert b["updated_at"] == a["updated_at"] and b["updated_by"] == a["updated_by"]
    assert len(b["proposals"]) == len(a["proposals"]) == 2
    for pa, pb in zip(a["proposals"], b["proposals"]):
        for key in ("id", "title", "author", "status", "priority", "path", "proposal_type"):
            assert pb[key] == pa[key]
        assert pb.get("related_issues", []) == (pa.get("related_issues") or [])
        assert pb.get("related_prs", []) == (pa.get("related_prs") or [])


def test_subset_parser_matches_pyyaml_on_live_registry():
    text = (ROOT / "docs" / "proposals" / "registry.yaml").read_text()
    yaml = __import__("yaml")
    a = yaml.safe_load(text)
    b = pf.parse_registry_subset(text)
    assert len(b["proposals"]) == len(a["proposals"])
    for pa, pb in zip(a["proposals"], b["proposals"]):
        assert pb["id"] == pa["id"] and pb["title"] == pa["title"]


def test_build_feed_shape(tmp_path):
    registry = pf.parse_registry_subset(FIXTURE)
    passes = tmp_path / "passes"
    (passes / "demo-pass").mkdir(parents=True)
    (passes / "demo-pass" / "pass.json").write_text(json.dumps(
        {"schema": "oracle-method-pass/v1", "pass_id": "demo-pass",
         "status": "recorded", "candidates": [{"id": "a"}, {"id": "b"}]}))
    (passes / "broken-pass").mkdir()
    (passes / "broken-pass" / "pass.json").write_text("{not json")
    feed = pf.build_feed(registry, tmp_path, "2026-10-28T00:00:00Z")
    assert feed["schema"] == "proposals-feed/v2"
    assert feed["counts"]["total"] == 2
    assert feed["counts"]["by_status"] == {"posted": 1, "executing": 1}
    first = feed["proposals"][0]
    assert first["issues"] == [175, 772] and first["prs"] == []
    assert first["proposal_type"] == "research"
    assert feed["proposals"][1]["proposal_type"] is None
    assert feed["counts"]["by_type"] == {"research": 1}
    # no states resolved -> the ref is stamped unknown, never guessed
    assert feed["proposals"][1]["prs"] == [
        {"number": 42, "state": "unknown", "merged_at": None}]
    assert first["url"].endswith("/docs/proposals/active/alpha-pack/")
    assert feed["proposals"][1]["issues"] == []  # absent in registry -> empty, never guessed
    by_id = {p["id"]: p for p in feed["passes"]}
    assert by_id["demo-pass"]["candidates"] == 2
    assert by_id["demo-pass"]["status"] == "recorded"  # verbatim from pass.json
    assert by_id["broken-pass"]["candidates"] is None
    assert any("broken-pass" in g for g in feed["gaps"])  # named, never dropped


def test_build_feed_pass_outcome(tmp_path):
    registry = pf.parse_registry_subset(FIXTURE)
    passes = tmp_path / "passes"
    scored = passes / "scored-pass" / "cycle"
    scored.mkdir(parents=True)
    (passes / "scored-pass" / "pass.json").write_text(json.dumps(
        {"schema": "oracle-method-pass/v1", "pass_id": "scored-pass",
         "status": "round_1_recorded", "candidates": [{"id": "a"}, {"id": "b"}]}))
    (scored / "BALLOT-round1.json").write_text(json.dumps(
        {"ballots_by_class": {"HUMAN_COLLABORATOR": 0, "MODEL_PROVIDER": 0, "LOCAL_BASELINE": 5},
         "per_class": {"LOCAL_BASELINE": {"scores": {"a": 23.269, "b": 23.269}}}}))
    silent = passes / "silent-pass"
    silent.mkdir(parents=True)
    (silent / "pass.json").write_text(json.dumps(
        {"schema": "oracle-method-pass/v1", "pass_id": "silent-pass",
         "status": "stated_not_run", "candidates": []}))
    (silent / "cycle").mkdir()
    (silent / "cycle" / "BALLOT-round1.json").write_text(json.dumps(
        {"ballots_by_class": {"HUMAN_COLLABORATOR": 0, "MODEL_PROVIDER": 0, "LOCAL_BASELINE": 0},
         "per_class": {}}))
    feed = pf.build_feed(registry, tmp_path, "2026-11-01T00:00:00Z")
    by_id = {p["id"]: p for p in feed["passes"]}
    outcome = by_id["scored-pass"]["outcome"]
    assert outcome["scores"] == {"a": 23.269, "b": 23.269}  # tie carried verbatim, never ranked
    assert outcome["ballots"] == 5 and outcome["class"] == "LOCAL_BASELINE"
    assert outcome["source"] == "cycle/BALLOT-round1.json"
    assert by_id["silent-pass"]["outcome"] is None  # no ballots -> no outcome, absence named
    assert any("silent-pass" in g for g in feed["gaps"])


def test_pr_state_mapping(monkeypatch):
    """API payload -> feed state: open / merged / closed-unmerged /
    unknown-on-any-failure. State is read at collection, never guessed."""
    import io
    import urllib.request

    payloads = {
        11: {"state": "open", "merged_at": None},
        12: {"state": "closed", "merged_at": "2026-08-18T00:00:00Z"},
        13: {"state": "closed", "merged_at": None},
    }

    class Resp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def fake_urlopen(req, timeout=30):
        n = int(req.full_url.rsplit("/", 1)[1])
        if n == 14:
            raise OSError("boom")
        return Resp(json.dumps(payloads[n]).encode())

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    assert pf.fetch_pr(11, "t") == {"number": 11, "state": "open", "merged_at": None}
    assert pf.fetch_pr(12, "t") == {
        "number": 12, "state": "merged", "merged_at": "2026-08-18T00:00:00Z"}
    assert pf.fetch_pr(13, "t") == {
        "number": 13, "state": "closed-unmerged", "merged_at": None}
    assert pf.fetch_pr(14, "t") == {"number": 14, "state": "unknown", "merged_at": None}


def test_build_feed_stamps_resolved_states(tmp_path):
    registry = pf.parse_registry_subset(FIXTURE)
    states = {42: {"number": 42, "state": "merged",
                   "merged_at": "2026-08-18T00:00:00Z"}}
    feed = pf.build_feed(registry, tmp_path, "2026-11-03T00:00:00Z",
                         pr_states=states)
    assert feed["proposals"][1]["prs"] == [
        {"number": 42, "state": "merged", "merged_at": "2026-08-18T00:00:00Z"}]
    # resolution dedups: each unique number is fetched once per run
    calls = []
    pf.resolve_pr_states([42, 42, 7], "t",
                         fetch=lambda n, tok: calls.append(n) or
                         {"number": n, "state": "open", "merged_at": None})
    assert sorted(calls) == [7, 42]


def test_proposal_type_vocabulary_and_unknown_type_gap(tmp_path):
    registry = pf.parse_registry_subset(FIXTURE)
    assert "research" in pf.PROPOSAL_TYPES
    assert "scientific_experiment_system" in pf.PROPOSAL_TYPES
    registry["proposals"][0]["proposal_type"] = "unregistered_type"
    feed = pf.build_feed(registry, tmp_path, "2026-11-11T00:00:00Z")
    assert feed["proposals"][0]["proposal_type"] == "unregistered_type"
    assert any("unknown proposal_type" in gap for gap in feed["gaps"])
    assert feed["counts"]["by_type"] == {"unregistered_type": 1}
