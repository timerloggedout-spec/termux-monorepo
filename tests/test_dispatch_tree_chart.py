"""Pins for the dispatch-tree lane-state distribution chart.

Chart-standard adoption (owner standard 2026-11-01): the chart
renders inside the page's existing single fetch of
data/dispatch-tree-feed.json (the page contract pins exactly one
fetch) using chartkit CK.bars / CK.stampState. Distributions are
computed from the feed's lane records as issued: lanes by
latest-run state (conclusion, else status, else "no runs") and by
due_at_read. This page's tests pin contract shape rather than a
snapshot fixture, so the sims assert invariants against the live
feed file: every lane counted exactly once in each distribution.
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "tribute-dashboard"
PAGE = APP / "dispatch-tree.html"
FEED = APP / "data" / "dispatch-tree-feed.json"


def _html():
    return PAGE.read_text(encoding="utf-8")


def test_single_fetch_preserved():
    fetches = re.findall(r"""fetch\(\s*["']([^"']+)["']""", _html())
    assert fetches == ["./data/dispatch-tree-feed.json"]


def test_chart_hooks_present():
    html = _html()
    for hook in ['src="./chartkit.js"', 'id="statedist"',
                 'id="statestamp"', "CK.bars", "CK.stampState",
                 "laneStateDist", "dueDist"]:
        assert hook in html, hook


def test_feed_shape_for_chart():
    feed = json.loads(FEED.read_text())
    assert feed["schema"] == "dispatch-tree-feed/v1"
    lanes = feed["data"]["lanes"]
    assert lanes and all("lane" in l for l in lanes)
    assert len(lanes) == feed["data"]["lane_count"]


def test_main_script_parses(tmp_path):
    html = _html()
    blocks = re.findall(r"<script>(.*?)</script>", html, re.S)
    assert blocks
    for b in blocks:
        f = tmp_path / "block.js"
        f.write_text(b)
        r = subprocess.run(["node", "--check", str(f)],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr


def test_node_sim_invariants(tmp_path):
    logic = _html().split(
        "// ==== pure logic (node-sim tested) ====")[1].split(
        "// ==== end pure logic ====")[0]
    harness = tmp_path / "harness.cjs"
    harness.write_text(logic)
    out = tmp_path / "run.cjs"
    out.write_text("""
const {laneStateDist, dueDist} = require("./harness.cjs");
const feed = require(process.argv[2]);
const lanes = feed.data.lanes;
console.log(JSON.stringify({
  state: laneStateDist(lanes), due: dueDist(lanes), n: lanes.length,
}));
""")
    r = subprocess.run(["node", str(out), str(FEED)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    res = json.loads(r.stdout.strip())
    assert sum(x["value"] for x in res["state"]) == res["n"]
    assert sum(x["value"] for x in res["due"]) == res["n"]
    assert [x["label"] for x in res["due"]] == \
        ["due", "not due", "not measured"]
    known = {"success", "failure", "cancelled", "in_progress",
             "queued", "no runs"}
    assert res["state"][0]["label"] in known  # canonical order leads
