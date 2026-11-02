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
PAGE = ROOT / "apps/tribute-dashboard/tracking.html"
FEED = ROOT / "apps/tribute-dashboard/data/tracking-feed.json"
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


SIM_JOIN = r"""
const fx=JSON.parse(require('fs').readFileSync(process.argv[2],'utf8'));
const lab=fx.doe_join.campaigns.find(x=>x.join_state==='joined');
const donly=fx.doe_join.campaigns.find(x=>x.join_state==='design_only');
const labBlock=f.campaignBlock(lab);
const nullRow=f.joinInstanceRow(lab,{provider:'p',model_at_version:null,
  role:'r',moniker:null,context:'c',prompt:'x',
  instance_key:'abcdef0123456789',occurrences:{plan:1}});
console.log(JSON.stringify({
  labRows:(labBlock.match(/<tr>/g)||[]).length-1,
  labModel:labBlock.includes(lab.instances[0].model_at_version),
  donlyNE:f.campaignBlock(donly).includes('NOT ESTABLISHED'),
  nullNE:nullRow.includes('NOT ESTABLISHED'),
  summary:fx.doe_join.summary}));
"""


@pytest.mark.skipif(not shutil.which("node"), reason="Node required")
def test_doe_join_render_on_fixture(tmp_path):
    sim = tmp_path / "simj.cjs"
    sim.write_text(ESC_LINE + pure_block()
                   + ";module.exports={stateLabel,statePill,fmtMerge,"
                     "countsLine,trackRow,ne,joinInstanceRow,campaignBlock};"
                     "const f=module.exports;\n" + SIM_JOIN)
    out = subprocess.run(["node", str(sim), str(FIXTURE)],
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    got = json.loads(out.stdout)
    assert got["labRows"] == 8  # lab-1: 8 joined instances at fixture gen
    assert got["labModel"] is True
    # design_only campaigns and null tuple fields stay NOT ESTABLISHED.
    assert got["donlyNE"] is True and got["nullNE"] is True
    assert got["summary"]["campaigns"] == 10
    assert got["summary"]["campaigns_joined"] == 1


def test_doe_join_live_thin_guards():
    feed = json.loads(FEED.read_text())
    dj = feed["doe_join"]
    assert dj["summary"]["campaigns"] == len(dj["campaigns"])
    for camp in dj["campaigns"]:
        assert camp["join_state"] in ("joined", "design_only")
        for inst in camp["instances"]:
            for k in ("provider", "model_at_version", "role", "instance_key"):
                assert k in inst  # values may be null -> NOT ESTABLISHED
