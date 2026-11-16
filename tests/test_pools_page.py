"""Pools census page contract tests (viz).

The page consumes ONLY the mirrored pools feed (byte-identical to
the MoneyBall repo's data/pools-feed.json at adoption; the mirror
refreshes on the feed owner's flags). Behaviour pins run against
the committed fixture (a frozen feed copy); live guards stay thin:
schema family, census margins, mirror byte-identity.

Discipline (Web3 brief, binding): counts render as counted; a cell
the feed names NOT_ESTABLISHED renders NE, never 0; absent classes
render as NOT_ESTABLISHED rows, never dropped.
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "apps/tribute-dashboard/pools.html"
MIRROR = ROOT / "apps/tribute-dashboard/data/pools-feed.json"
FIXTURE = ROOT / "tests/fixtures/pools-feed.fixture.json"


def _page():
    return PAGE.read_text()


def _fixture():
    return json.loads(FIXTURE.read_text())


def test_page_shape():
    html = _page()
    assert 'fetch("./data/pools-feed.json")' in html
    assert html.count("fetch(") == 1
    assert 'src="./chartkit.js"' in html
    assert 'id="matrix"' in html and 'id="necells"' in html
    assert "Paper / test wallet pools" in html
    assert "winprob" not in html.lower()


def test_mirror_byte_identical():
    assert MIRROR.read_bytes() == FIXTURE.read_bytes()


def test_census_margins():
    feed = _fixture()
    cen = feed["census"]
    cxd = cen["class_x_depth"]
    assert feed["schema"] == "moneyball-pools-feed/v1"
    assert cen["feed_pools"] == len(feed["pools"])
    assert cen["feed_pools"] == cen["ledger_pool_wallets"]
    assert cen["deltas"] == []
    for row in cxd["rows"].values():
        assert sum(row["by_depth"].values()) == row["total"]
    assert sum(r["total"] for r in cxd["rows"].values()) \
        == cen["feed_pools"]


def test_node_sim(tmp_path):
    html = _page()
    logic = html.split("// ==== pure logic (node-sim tested) ====")[1] \
        .split("// ==== end pure logic ====")[0]
    harness = tmp_path / "harness.cjs"
    harness.write_text(logic)
    out = tmp_path / "run.cjs"
    out.write_text("""
const {buildMatrix, neCellKeys} = require("./harness.cjs");
const feed = require(process.argv[2]);
const m = buildMatrix(feed.census);
const at = (c, d) => m.rows.find(r => r.cls === c).cells[m.cols.indexOf(d)];
console.log(JSON.stringify({
  grand: m.grand, rows: m.rows.length, absent: m.absent.length,
  provider3: at("provider", 3), quelane2: at("que-lane", 2),
  desk2: at("desk-lane", 2), doe2: at("doe", 2),
  doe4: at("doe", 4), spec0: at("speculator", 0),
  colTotals: m.colTotals,
  neKeys: Object.keys(neCellKeys(feed.census.class_x_depth.not_established_cells)).length
}));
""")
    res = json.loads(subprocess.run(
        ["node", str(out), str(FIXTURE)],
        capture_output=True, text=True, check=True).stdout)
    assert res["grand"] == 693 and res["rows"] == 16
    assert res["absent"] == 2
    assert res["provider3"] == "NE" and res["quelane2"] == "NE"
    assert res["desk2"] == "NE"
    assert res["doe2"] == 126 and res["doe4"] == 0
    assert res["spec0"] == 12
    assert sum(res["colTotals"]) == 693
    assert res["neKeys"] == 6
