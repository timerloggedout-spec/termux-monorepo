"""Pins for the tracking board state x domain chart (chart standard).

The chart renders from the page's already-loaded tracking feed
(no new fetch; the consumes-feed-only law stands) using chartkit
CK.bars / CK.stampState: rows by state, rows by domain, and the
full domain x state matrix with zero cells shown. Behavior is
pinned against the committed tracking fixture; the sim asserts
the matrix margins equal the feed's own summary (by_state /
by_domain) and the cell sum equals the row count, on both the
fixture and the live feed file.
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "tribute-dashboard"
PAGE = APP / "tracking.html"
FEED = APP / "data" / "tracking-feed.json"
FIXTURE = ROOT / "tests" / "fixtures" / "tracking-feed.fixture.json"


def _html():
    return PAGE.read_text(encoding="utf-8")


def _logic():
    page = _html()
    i = page.find("function summaryRows")
    assert i > 0
    start = page.rfind("// ==== pure logic (node-sim tested) ====",
                       0, i)
    end = page.find("// ==== end pure logic ====", i)
    assert start > 0 and end > i
    return page[start:end]


def test_no_new_fetch_and_hooks():
    html = _html()
    assert "./data/tracking-feed.json" in html
    assert "ops/tracking" not in html
    for hook in ['src="./chartkit.js"', 'id="matrixchart"',
                 'id="matrixstamp"', "CK.bars", "CK.stampState",
                 "matrixRows", "renderMatrix();"]:
        assert hook in html, hook


def test_feed_shape_for_chart():
    feed = json.loads(FEED.read_text())
    assert feed["schema"] == "repo-tracking/v1"
    assert feed["summary"]["by_state"] and feed["summary"]["by_domain"]
    assert feed["rows"]


def test_scripts_parse(tmp_path):
    blocks = re.findall(r"<script>(.*?)</script>", _html(), re.S)
    assert blocks
    for b in blocks:
        f = tmp_path / "block.js"
        f.write_text(b)
        r = subprocess.run(["node", "--check", str(f)],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr


def _sim(tmp_path, feed_path):
    harness = tmp_path / "harness.cjs"
    harness.write_text(_logic())
    out = tmp_path / "run.cjs"
    out.write_text("""
const {matrixRows, summaryRows} = require("./harness.cjs");
const feed = require(process.argv[2]);
const m = matrixRows(feed);
const col = {}, row = {};
for (const c of m) {
  const parts = c.label.split(" \u00b7 ");
  col[parts[1]] = (col[parts[1]] || 0) + c.value;
  row[parts[0]] = (row[parts[0]] || 0) + c.value;
}
console.log(JSON.stringify({
  cells: m.length, sum: m.reduce((a, c) => a + c.value, 0),
  n: feed.rows.length, col, row,
  byState: feed.summary.by_state, byDomain: feed.summary.by_domain,
}));
""")
    r = subprocess.run(["node", str(out), str(feed_path)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip())


def test_node_sim_matrix_fixture(tmp_path):
    res = _sim(tmp_path, FIXTURE)
    assert res["sum"] == res["n"]
    assert res["col"] == res["byState"]
    assert res["row"] == res["byDomain"]


def test_node_sim_matrix_live(tmp_path):
    res = _sim(tmp_path, FEED)
    assert res["sum"] == res["n"]
    assert res["col"] == res["byState"]
    assert res["row"] == res["byDomain"]
