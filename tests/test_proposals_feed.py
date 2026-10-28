"""Collector pins for the proposals index feed (proposals-feed/v1).

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
        for key in ("id", "title", "author", "status", "priority", "path"):
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
    assert feed["schema"] == "proposals-feed/v1"
    assert feed["counts"]["total"] == 2
    assert feed["counts"]["by_status"] == {"posted": 1, "executing": 1}
    first = feed["proposals"][0]
    assert first["issues"] == [175, 772] and first["prs"] == []
    assert first["url"].endswith("/docs/proposals/active/alpha-pack/")
    assert feed["proposals"][1]["issues"] == []  # absent in registry -> empty, never guessed
    by_id = {p["id"]: p for p in feed["passes"]}
    assert by_id["demo-pass"]["candidates"] == 2
    assert by_id["demo-pass"]["status"] == "recorded"  # verbatim from pass.json
    assert by_id["broken-pass"]["candidates"] is None
    assert any("broken-pass" in g for g in feed["gaps"])  # named, never dropped
