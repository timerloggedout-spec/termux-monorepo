"""Pins for the desk page traversal-distribution chart (chart standard).

The chart block in desk.html renders ONLY data/desk-feed.json via
chartkit (CK.bars / CK.stampState): entries-by-status and
stage-completion distributions computed from the feed's traversal
records as issued. Behavior is pinned against the committed desk
fixture; live guards stay thin (hooks + feed shape).
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "tribute-dashboard"
PAGE = APP / "desk.html"
FEED = APP / "data" / "desk-feed.json"
FIXTURE = ROOT / "tests" / "fixtures" / "desk-feed.fixture.json"


def _html():
    return PAGE.read_text(encoding="utf-8")


def _chart_js():
    html = _html()
    blocks = re.findall(r"<script>(.*?)</script>", html, re.S)
    chart = [b for b in blocks if "statusDist" in b]
    assert len(chart) == 1
    return chart[0]


def test_page_fetches_only_the_desk_feed():
    fetches = re.findall(r"fetch\(([^)]*)\)", _html())
    assert fetches and all(f == '"./data/desk-feed.json"' for f in fetches)


def test_chart_hooks_present():
    html = _html()
    for hook in ['src="./chartkit.js"', 'id="distchart"', 'id="diststamp"',
                 "CK.bars", "CK.stampState"]:
        assert hook in html, hook


def test_feed_shape_for_chart():
    feed = json.loads(FEED.read_text())
    assert feed["schema"].startswith("desk-feed/")
    assert feed["generated_at"]
    assert feed["traversals"] and all(
        "status" in t and "stages" in t for t in feed["traversals"])


def test_chart_script_parses(tmp_path):
    f = tmp_path / "chart.js"
    f.write_text(_chart_js())
    r = subprocess.run(["node", "--check", str(f)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_node_sim_distributions(tmp_path):
    logic = _chart_js().split(
        "// ==== pure logic (node-sim tested) ====")[1].split(
        "// ==== end pure logic ====")[0]
    harness = tmp_path / "harness.cjs"
    harness.write_text(logic)
    out = tmp_path / "run.cjs"
    out.write_text("""
const {statusDist, stageDist} = require("./harness.cjs");
const feed = require(process.argv[2]);
console.log(JSON.stringify({
  status: statusDist(feed.traversals),
  stage: stageDist(feed.traversals),
  n: feed.traversals.length,
}));
""")
    r = subprocess.run(["node", str(out), str(FIXTURE)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    res = json.loads(r.stdout.strip())
    status = {x["label"]: x["value"] for x in res["status"]}
    assert sum(status.values()) == res["n"]
    assert status == {"queued": 1, "in-progress": 1, "gated": 2,
                      "landed": 3}
    labels = [x["label"] for x in res["status"]]
    assert labels == ["queued", "in-progress", "gated", "landed"]
    stage = {x["label"]: x["value"] for x in res["stage"]}
    assert list(stage) == ["spec", "desk", "builder", "pr", "ci",
                           "merge", "sync"]
    assert all(0 <= v <= res["n"] for v in stage.values())
    assert stage["spec"] >= stage["sync"]
