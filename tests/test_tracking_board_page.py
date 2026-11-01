"""Tracking board prototype: renders ONLY data/tracking-feed.json.
Fixture-pinned render logic (node-sim) + thin live guards (the feed is
workflow-owned and refreshes daily; guards check schema family + shape,
never exact values)."""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "apps/help-wanted-dashboard/tracking.html"
FEED = ROOT / "apps/help-wanted-dashboard/data/tracking-feed.json"
FIXTURE = ROOT / "tests/fixtures/tracking-feed.fixture.json"
ESC_LINE = ("const esc=v=>String(v??'').replace(/[&<>\"']/g,"
            "c=>'&#'+c.charCodeAt(0)+';');")


def pure_block():
    html = PAGE.read_text()
    m = re.search(r"// ==== pure logic \(node-sim tested\) ====([\s\S]*?)"
                  r"// ==== end pure logic ====", html)
    assert m, "pure-logic markers missing from tracking.html"
    return m.group(1)


SIM = r"""
const fx=JSON.parse(require('fs').readFileSync(process.argv[2],'utf8'));
const unk=fx.rows.find(r=>r.state==='unknown');
const merged=fx.rows.find(r=>r.last_merge);
const unkHtml=f.trackRow(unk), mergedHtml=f.trackRow(merged);
console.log(JSON.stringify({
  unknownLabel:f.stateLabel('unknown'),
  nullMerge:f.fmtMerge(null),
  mergeText:f.fmtMerge(merged.last_merge),
  unkHasNE:unkHtml.includes('NOT ESTABLISHED'),
  mergedHasPR:mergedHtml.includes('PR #'+merged.last_merge.pr),
  counts:f.countsLine(fx.summary)}));
"""


@pytest.mark.skipif(not shutil.which("node"), reason="Node required")
def test_tracking_render_on_fixture(tmp_path):
    sim = tmp_path / "sim.cjs"
    sim.write_text(ESC_LINE + pure_block()
                   + ";module.exports={stateLabel,statePill,fmtMerge,"
                     "countsLine,trackRow};const f=module.exports;\n" + SIM)
    out = subprocess.run(["node", str(sim), str(FIXTURE)],
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    got = json.loads(out.stdout)
    # Degraded state stays visible, never blanked or synthesized.
    assert got["unknownLabel"] == "NOT ESTABLISHED"
    assert got["nullMerge"] == "NOT ESTABLISHED"
    assert got["unkHasNE"] is True
    assert got["mergedHasPR"] is True
    assert got["mergeText"].startswith("PR #")
    assert "by state:" in got["counts"] and "by domain:" in got["counts"]


def test_fixture_summary_crosscheck():
    fx = json.loads(FIXTURE.read_text())
    rows = fx["rows"]
    assert fx["summary"]["rows"] == len(rows)
    assert sum(fx["summary"]["by_state"].values()) == len(rows)
    assert sum(fx["summary"]["by_domain"].values()) == len(rows)
    states = {}
    for r in rows:
        states[r["state"]] = states.get(r["state"], 0) + 1
    assert states == fx["summary"]["by_state"]


def test_live_feed_thin_guards():
    feed = json.loads(FEED.read_text())
    assert feed["schema"] == "repo-tracking/v1"
    assert feed["generated_at"] and feed["generated_by"]
    assert isinstance(feed["rows"], list) and len(feed["rows"]) >= 1
    for r in feed["rows"]:
        for k in ("lane", "project", "domain", "state", "next"):
            assert k in r
        assert "last_merge" in r  # may be null - renders NOT ESTABLISHED
    assert feed["sources"]["pr_feed"] and feed["sources"]["lane_events"]
    assert isinstance(feed["gaps"], list)


def test_page_consumes_feed_only():
    html = PAGE.read_text()
    assert "./data/tracking-feed.json" in html
    script = re.search(r"<script>([\s\S]*?)</script>", html).group(1)
    # Surface-feeds law: the page fetches the dashboard feed and nothing else.
    assert "ops/tracking" not in script
    assert "raw.githubusercontent" not in script
    for col in ("<th>Lane</th>", "<th>Project</th>", "<th>State</th>",
                "<th>Last merge</th>", "<th>Next</th>"):
        assert col in html
