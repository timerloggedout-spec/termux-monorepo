"""Usage-graphs sibling view: fixture-pinned chart logic (node-sim), the
generator contract, and thin live guards on the usage-series pack."""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "apps/help-wanted-dashboard/quota-graphs.html"
QUOTA_PAGE = ROOT / "apps/help-wanted-dashboard/quota.html"
PACK = ROOT / "ops/quota/usage-series.json"
MIRROR = ROOT / "apps/help-wanted-dashboard/data/usage-series.json"
FIXTURE = ROOT / "tests/fixtures/usage-series.fixture.json"
GENERATOR = ROOT / "scripts/quota_usage_series.py"
ESC_LINE = ("const esc=v=>String(v??'').replace(/[&<>\"']/g,"
            "c=>'&#'+c.charCodeAt(0)+';');")
KINDS = {"measured", "usage-exact", "activity-proxy", "reconstructed",
         "estimated"}


def pure_block():
    html = PAGE.read_text()
    m = re.search(r"// ==== pure logic \(node-sim tested\) ====([\s\S]*?)"
                  r"// ==== end pure logic ====", html)
    assert m, "pure-logic markers missing from quota-graphs.html"
    return m.group(1)


SIM = r"""
const even=f.chartGeom([{t:'2026-10-01T00:00:00Z',v:1},{t:'2026-10-02T00:00:00Z',v:2},{t:'2026-10-03T00:00:00Z',v:3}],640,180);
const gapped=f.chartGeom([{t:'2026-10-01T00:00:00Z',v:1},{t:'2026-10-02T00:00:00Z',v:2},{t:'2026-10-20T00:00:00Z',v:3}],640,180);
const single=f.chartGeom([{t:'2026-10-01T00:00:00Z',v:5}],640,180);
const withNull=f.chartGeom([{t:'2026-10-01T00:00:00Z',v:1},{t:'2026-10-02T00:00:00Z',v:null},{t:'2026-10-03T00:00:00Z',v:3}],640,180);
const evGeom=f.chartGeom([{t:'2026-10-01T00:00:00Z',v:1,class:'core-exhaustion'}],640,180);
const fx=JSON.parse(require('fs').readFileSync(process.argv[2],'utf8'));
const gh=fx.axes.provider.find(s=>s.key==='github');
const ghGeom=f.chartGeom(gh.points,640,180);
console.log(JSON.stringify({even:{d:even.dots.length,s:even.segs.length,g:even.segs.map(x=>x.gap)},
  gapped:{s:gapped.segs.length,g:gapped.segs.map(x=>x.gap)},
  single:{d:single.dots.length,s:single.segs.length},
  withNull:{d:withNull.dots.length},
  gh:{d:ghGeom.dots.length,s:ghGeom.segs.length},
  ev:{d:evGeom.dots.length,c:evGeom.dots[0].cls},
  labels:{ap:f.kindLabel('activity-proxy'),m:f.kindLabel('measured'),ue:f.kindLabel('usage-exact')}}));
"""


@pytest.mark.skipif(not shutil.which("node"), reason="Node required")
def test_chart_logic_on_fixture(tmp_path):
    sim = tmp_path / "sim.cjs"
    sim.write_text(ESC_LINE + pure_block()
                   + ";module.exports={chartGeom,kindLabel,seriesSvg};"
                     "const f=module.exports;\n" + SIM)
    out = subprocess.run(["node", str(sim), str(FIXTURE)],
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    got = json.loads(out.stdout)
    assert got["even"] == {"d": 3, "s": 2, "g": [False, False]}
    # A step >3x the median step renders as a gap segment, not a trend line.
    assert got["gapped"] == {"s": 2, "g": [False, True]}
    assert got["single"] == {"d": 1, "s": 0}
    # Null values are dropped (gap), never zero-filled.
    assert got["withNull"] == {"d": 2}
    assert got["gh"] == {"d": 11, "s": 10}
    # Event points keep their class through the geometry (marker label).
    assert got["ev"] == {"d": 1, "c": "core-exhaustion"}
    assert "NOT consumption" in got["labels"]["ap"]
    assert got["labels"]["m"] == "measured"
    assert got["labels"]["ue"] == "usage-exact"


def test_generator_contract(tmp_path):
    out = tmp_path / "usage-series.json"
    run = subprocess.run(["python3", str(GENERATOR), "--root", str(ROOT),
                          "--out", str(out)], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    pack = json.loads(out.read_text())
    assert pack["schema"] == "quota.usage-series/v1"
    prov = {(s["key"], s["kind"]) for s in pack["axes"]["provider"]}
    assert ("github", "measured") in prov
    assert ("jules", "activity-proxy") in prov
    # Model axis: no stamped model carries a usage value yet - honestly empty.
    assert pack["axes"]["model"] == []
    assert "NOT ESTABLISHED" in pack["notes"]["model"]
    gh = next(s for s in pack["axes"]["provider"] if s["key"] == "github")
    assert gh["context"]["target_flow_per_min"] > 0
    # Owner directive 2026-11-01: the 403 must be visible on the graph -
    # the generator emits an events axis (per-bucket, class-carrying).
    ev = pack["axes"]["events"]
    assert ev and all(s["kind"] == "event" for s in ev)
    assert all(p["v"] == 1 and p["class"] for s in ev for p in s["points"])


def test_pack_live_guards_and_mirror():
    pack = json.loads(PACK.read_text())
    assert pack["schema"] == "quota.usage-series/v1"
    for axis in ("provider", "service", "model"):
        for s in pack["axes"][axis]:
            assert s["kind"] in KINDS
            for p in s["points"]:
                assert p["t"] and isinstance(p["v"], (int, float))
    assert MIRROR.read_bytes() == PACK.read_bytes()


def test_page_contract():
    html = PAGE.read_text()
    assert "ops/quota/usage-series.json" in html
    assert "./data/usage-series.json" in html
    for axis in ("provider", "model", "service", "events"):
        assert 'data-axis="' + axis + '"' in html
    assert "rate-limit-events.json" in html
    assert "rate-limit event" in html
    assert "activity-proxy — NOT consumption" in html
    assert "quota-graphs.html" in QUOTA_PAGE.read_text()


def test_pack_freshness_stamps():
    # Owner staleness flag (2026-11-02): the pack must carry its build
    # stamp + per-series last point, and the page must surface staleness.
    pack = json.loads(PACK.read_text())
    assert pack["generated_at"].endswith("Z")
    assert pack["inputs_generated_at"]["ops/quota/quota-usage.json"]
    for axis in ("provider", "service", "model", "events"):
        for s in pack["axes"][axis]:
            assert s["last_point_at"] == max(p["t"] for p in s["points"])
    html = PAGE.read_text()
    assert "STALE" in html and "last_point_at" in html
    # Viz condition (2026-11-02): staleness keys PER-SERIES (a STALE chip
    # on the series' own card, from its own last_point_at - a fresh series
    # must not mask a stale one); the header line keys on the OLDEST
    # last-point, never the newest.
    assert "sStale" in html and 'chip">STALE' in html
    assert "oldest observation" in html and "oldest point" in html
