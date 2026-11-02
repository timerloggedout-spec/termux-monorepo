"""Pins for the linguist page panel-distribution chart.

Chart-standard adoption (owner standard 2026-11-01): the chart
renders inside the page's existing single fetch of
data/linguist-panel-feed.json (the page contract pins exactly one
fetch) using chartkit CK.bars / CK.stampState. Distributions are
computed from the feed as issued: entries per family from
counts.per_family (families[] order) and enumerated entries by
direction_panel. Sims assert invariants against the live feed
file: family counts sum to counts.entries_total and panel counts
sum to the enumerated entry count.
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "tribute-dashboard"
PAGE = APP / "linguist.html"
FEED = APP / "data" / "linguist-panel-feed.json"


def _html():
    return PAGE.read_text(encoding="utf-8")


def test_single_fetch_preserved():
    fetches = re.findall(r"""fetch\(\s*["']([^"']+)["']""", _html())
    assert fetches == ["./data/linguist-panel-feed.json"]


def test_chart_hooks_present():
    html = _html()
    for hook in ['src="./chartkit.js"', 'id="paneldist"',
                 'id="panelstamp"', "CK.bars", "CK.stampState",
                 "familyDist", "panelDist"]:
        assert hook in html, hook


def test_feed_shape_for_chart():
    feed = json.loads(FEED.read_text())
    assert feed["schema"] == "linguist-panel-feed/v1"
    assert feed["counts"]["per_family"] and feed["families"]
    assert feed["entries"]


def test_scripts_parse(tmp_path):
    blocks = re.findall(r"<script>(.*?)</script>", _html(), re.S)
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
const {familyDist, panelDist} = require("./harness.cjs");
const feed = require(process.argv[2]);
console.log(JSON.stringify({
  fam: familyDist(feed), panel: panelDist(feed.entries),
  total: feed.counts.entries_total, inc: feed.entries.length,
  famN: feed.families.length,
}));
""")
    r = subprocess.run(["node", str(out), str(FEED)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    res = json.loads(r.stdout.strip())
    assert len(res["fam"]) == res["famN"]
    assert sum(x["value"] for x in res["fam"]) == res["total"]
    assert sum(x["value"] for x in res["panel"]) == res["inc"]
