"""Surfaces-map draft contract tests (viz).

The map is data-driven: these tests pin the data invariants -
every surface has a known plane + at least one substrate draw,
every substrate element has at least one consumer, the §12 Web3
surfaces and the desk's QUE/governor draws are present.
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "apps/tribute-dashboard/surfaces-map.html"


def _sim(tmp_path):
    html = PAGE.read_text()
    data = html.split("// ==== map data (draft of record for review) ====")[1] \
        .split("// ==== pure logic")[0]
    logic = html.split("// ==== pure logic (node-sim tested) ====")[1] \
        .split("// ==== end pure logic ====")[0]
    harness = tmp_path / "harness.cjs"
    harness.write_text(data + logic)
    out = tmp_path / "run.cjs"
    out.write_text("""
const {planeDraws, substrateConsumers} = require("./harness.cjs");
console.log(JSON.stringify({
  surfaces: SURFACES.length,
  planes: Object.keys(planeDraws(SURFACES)).length,
  substrateUsed: Object.keys(substrateConsumers(SURFACES)).length,
  substrateTotal: SUBSTRATE.length,
  deskQue: substrateConsumers(SURFACES).quefeeds.includes("desk.html"),
  poolsBoth: substrateConsumers(SURFACES).walletledger
    .filter(x => x.toLowerCase().includes("pools")).length
}));
""")
    return json.loads(subprocess.run(
        ["node", str(out)], capture_output=True, text=True,
        check=True).stdout)


def test_page_shape():
    html = PAGE.read_text()
    assert "DRAFT" in html
    assert 'id="diagram"' in html and 'id="table"' in html
    assert html.count("<body") == 1 and html.count("</head>") == 1


def test_map_invariants(tmp_path):
    res = _sim(tmp_path)
    assert res["planes"] == 8
    assert res["substrateUsed"] == 6 and res["substrateTotal"] == 7  # 6 draws + naming gate (provenance, not a draw)
    assert res["surfaces"] >= 37
    assert res["deskQue"] is True
    assert res["poolsBoth"] >= 2
