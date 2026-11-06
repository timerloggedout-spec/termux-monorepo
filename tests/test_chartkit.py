"""Chart standard (owner 2026-11-01): chartkit builders carry the
legibility floor (value labels, stated max, y ticks, date labels) and
the STALE stamp logic; quota.html is the reference wiring."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/tribute-dashboard"
KIT = APP / "chartkit.js"
DOC = ROOT / "docs/ops/DASHBOARD-CHART-STANDARD.md"

SIM = r"""
const CK = require(process.argv[2]);
const bars = CK.bars([{label:'a',value:10},{label:'b',value:5000}]);
const line = CK.line([{t:'2026-10-01T00:00:00Z',v:5},{t:'2026-10-03T00:00:00Z',v:9},{t:'2026-10-05T00:00:00Z',v:7}]);
const gap = CK.line([{t:'2026-10-01T00:00:00Z',v:1},{t:'2026-10-02T00:00:00Z',v:2},{t:'2026-10-03T00:00:00Z',v:null},{t:'2026-10-04T00:00:00Z',v:4}]);
console.log(JSON.stringify({
  barsMax: bars.includes('max 5,000'), barsVal: bars.includes('>10<'),
  lineTicks: line.includes('>9<') && line.includes('>5<') && line.includes('>7<'),
  lineDates: line.includes('2026-10-01') && line.includes('2026-10-05'),
  gapSegments: (gap.match(/<path /g)||[]).length === 1 && (gap.match(/<circle /g)||[]).length === 3,
  lineSize: gap.includes('width=\"640\"') && gap.includes('height=\"180\"'),
  stale: CK.stampState('2026-10-01T00:00:00Z', Date.parse('2026-10-03T00:00:01Z'), 86400000),
  fresh: CK.stampState('2026-10-03T00:00:00Z', Date.parse('2026-10-03T01:00:00Z'), 86400000),
  unknown: CK.stampState(null, Date.now(), 86400000)}));
"""


@pytest.mark.skipif(not shutil.which("node"), reason="Node required")
def test_chartkit_builders(tmp_path):
    sim = tmp_path / "sim.cjs"
    sim.write_text(SIM)
    out = subprocess.run(["node", str(sim), str(KIT)],
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    got = json.loads(out.stdout)
    assert got == {"barsMax": True, "barsVal": True, "lineTicks": True,
                   "lineDates": True, "gapSegments": True, "lineSize": True, "stale": "STALE", "fresh": "fresh",
                   "unknown": "unknown"}


def test_quota_page_chart_wiring():
    html = (APP / "quota.html").read_text()
    assert "./chartkit.js" in html
    for marker in ('id="charts"', 'id="chart-headroom"', 'id="chart-states"',
                   "CK.bars", "CK.stampState"):
        assert marker in html


def test_telemetry_history_uses_per_series_last_observed_stamp():
    html = (APP / "telemetry.html").read_text()
    assert "lastObserved=key" in html
    assert 'stampFor("receipts_total")' in html
    assert 'stampFor("workflow_runs_observed")' in html
    assert "null observations remain gaps" in html


def test_standard_doc_covers_family():
    doc = DOC.read_text()
    for page in ("quota.html", "index.html", "owner-records.html",
                 "pr-lanes.html", "versioning.html", "EXCEPTION"):
        assert page in doc


def test_index_and_owner_records_wiring():
    idx = (APP / "index.html").read_text()
    assert "./chartkit.js" in idx and 'id="chart-kinds"' in idx
    assert "CK.stampState" in idx
    orp = (APP / "owner-records.html").read_text()
    assert "./chartkit.js" in orp and 'id="chart-classes"' in orp
    assert "CK.bars" in orp
