"""HYBRID E - B-lite part 2 (web-design): independent rendered-value
assertions against the viz V1/V2 landed shapes (PR #3594 hooks).
Graphs: the actual seriesSvg OUTPUT is parsed - ytick texts must be
the fixture's min/mid/max, xtick texts its first/last dates.
Usage: the axis helpers must generalize beyond the pinned fixture -
quarter ticks at another scale, three-way label placement, a
three-wall stagger, and the bar scale's mid tick."""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/tribute-dashboard"

GRAPHS_SIM = r"""
const f = require(process.argv[2]);
const svg = f.seriesSvg({title:'t', kind:'measured', points:[
  {t:'2026-10-01T00:00:00Z', v:1}, {t:'2026-10-03T00:00:00Z', v:3}]});
const grab = cls => [...svg.matchAll(new RegExp('<text[^>]*class="' + cls + '"[^>]*>([^<]*)</text>', 'g'))].map(m => m[1]);
console.log(JSON.stringify({yticks: grab('ytick'), xticks: grab('xtick'),
  fmtMin: f.fmtV(1), fmtMid: f.fmtV(2), fmtMax: f.fmtV(3)}));
"""

USAGE_SIM = r"""
const {yTicks, labelPlace, wallLabels, barScale} = require(process.argv[2]);
console.log(JSON.stringify({
  ticks100: yTicks(100),
  placeMid: labelPlace(460, '2500 · 2026-10-29T00:37:00Z · single wall episode, three independent observations', 920, 44).anchor,
  wallYs: wallLabels([{x:800, y:256, at:'a'}, {x:815, y:256, at:'b'}, {x:830, y:256, at:'c'}], 920, 44).map(w => w.y),
  scale30: barScale([{runs_delta: 30}, {runs_delta: 10}])}));
"""


def _logic(page, tmp_path, name, exports=None):
    html = (APP / page).read_text()
    logic = html.split("// ==== pure logic (node-sim tested) ====")[1].split("// ==== end pure logic ====")[0]
    p = tmp_path / name
    p.write_text(logic + (exports or ""))
    return p


@pytest.mark.skipif(not shutil.which("node"), reason="Node required")
def test_graphs_rendered_tick_texts(tmp_path):
    harness = _logic("quota-graphs.html", tmp_path, "graphs.cjs",
                     ";module.exports={chartGeom,kindLabel,seriesSvg,axisTicks,fmtV};")
    sim = tmp_path / "sim.cjs"
    sim.write_text(GRAPHS_SIM)
    out = subprocess.run(["node", str(sim), str(harness)], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    got = json.loads(out.stdout)
    assert got["yticks"] == [got["fmtMax"], got["fmtMid"], got["fmtMin"]] or \
        sorted(got["yticks"]) == sorted([got["fmtMin"], got["fmtMid"], got["fmtMax"]])
    assert len(got["yticks"]) == 3 and all(got["yticks"])
    assert got["xticks"] == ["2026-10-01", "2026-10-03"]


@pytest.mark.skipif(not shutil.which("node"), reason="Node required")
def test_usage_axis_helpers_generalize(tmp_path):
    harness = _logic("quota-usage.html", tmp_path, "usage.cjs")
    sim = tmp_path / "sim.cjs"
    sim.write_text(USAGE_SIM)
    out = subprocess.run(["node", str(sim), str(harness)], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    got = json.loads(out.stdout)
    assert got["ticks100"] == [0, 25, 50, 75, 100]
    assert got["placeMid"] == "middle"
    assert len(set(got["wallYs"])) == 3
    assert got["scale30"] == {"max": 30, "ticks": [0, 15, 30]}


def test_screenshot_workflow_still_covers_both_pages():
    wf = (ROOT / ".github/workflows/quota-pages-visual.yml").read_text()
    assert "quota-usage.html" in wf and "quota-graphs.html" in wf
