"""Pins for the PR-lanes page (phase 1: distribution + per-lane table).

The page renders ONLY data/pr-lane-feed.json — the byte-identical
mirror of ops/ml/pr-lane-feed.json that ml-pr-lane-classify.yml commits
alongside the source feed. No lane counts are hardcoded in the page;
the trend/burn-down views are phase 2 and must stay data-fed too.
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "help-wanted-dashboard"
PAGE = APP / "pr-lanes.html"
MIRROR = APP / "data" / "pr-lane-feed.json"
SOURCE = ROOT / "ops" / "ml" / "pr-lane-feed.json"
WORKFLOW = ROOT / ".github" / "workflows" / "ml-pr-lane-classify.yml"

FIXTURE = {
    "schema": "pr-lane-feed/v1",
    "generated_at": "2026-10-28T23:02:34Z",
    "open_prs": 4,
    "counts": {"CANDIDATE": 2, "EXTRACT": 1, "NEED_EVIDENCE": 1, "SUPERSEDE": 0},
    "fetch_warnings": 0,
    "error": None,
    "prs": [
        {"number": 11, "title": "Alpha", "author": "a", "draft": False,
         "age_days": 3, "changed_files": 5,
         "gates": {"repo-gate": True, "termux-smoke": False}, "lane": "CANDIDATE"},
        {"number": 12, "title": "Beta", "author": "b", "draft": True,
         "age_days": 9, "changed_files": 2,
         "gates": {"repo-gate": False, "termux-smoke": False}, "lane": "CANDIDATE"},
        {"number": 13, "title": "Gamma", "author": "c", "draft": False,
         "age_days": 1, "changed_files": 40,
         "gates": {"repo-gate": True, "termux-smoke": True}, "lane": "EXTRACT"},
        {"number": 14, "title": "Delta", "author": "d", "draft": False,
         "age_days": 2, "changed_files": 1,
         "gates": {"repo-gate": False, "termux-smoke": True}, "lane": "NEED_EVIDENCE"},
    ],
}


def _html():
    return PAGE.read_text(encoding="utf-8")


def test_page_consumes_only_the_mirror_feed():
    html = _html()
    fetches = re.findall(r"fetch\(([^)]*)\)", html)
    assert fetches == ['"./data/pr-lane-feed.json"'], fetches
    assert 'id="dist"' in html and 'id="tables"' in html and 'id="meta"' in html


def test_mirror_matches_source_feed():
    assert json.loads(MIRROR.read_text()) == json.loads(SOURCE.read_text())


def test_workflow_keeps_mirror_fresh():
    wf = WORKFLOW.read_text()
    assert "cp ops/ml/pr-lane-feed.json apps/help-wanted-dashboard/data/pr-lane-feed.json" in wf
    assert "apps/help-wanted-dashboard/data/pr-lane-feed.json" in wf.split("git add -A")[1].split("\n")[0]


def test_no_hardcoded_lane_counts():
    html = _html()
    assert not re.search(r'counts\s*[:=]\s*\{', html)


def test_node_sim_distribution_and_groups(tmp_path):
    html = _html()
    logic = html.split("// ==== pure logic (node-sim tested) ====")[1].split("// ==== end pure logic ====")[0]
    harness = tmp_path / "harness.cjs"
    harness.write_text(f"""
global.LANES=["CANDIDATE","EXTRACT","NEED_EVIDENCE","SUPERSEDE"];
const FEED={json.dumps(FIXTURE)};
{logic}
module.exports={{distRows, laneGroups}};
""")
    out = tmp_path / "run.cjs"
    out.write_text("""
const {distRows, laneGroups} = require("./harness.cjs");
const FEED = JSON.parse(process.argv[2]);
const d = Object.fromEntries(distRows(FEED).map(r => [r.lane, r]));
const g = laneGroups(FEED);
const res = {
  cand_n: d.CANDIDATE.n, cand_pct: d.CANDIDATE.pct, cand_width: d.CANDIDATE.width,
  sup_n: d.SUPERSEDE.n, sup_width: d.SUPERSEDE.width,
  cand_order: g.CANDIDATE.map(r => r.number),
  ext_numbers: g.EXTRACT.map(r => r.number),
  empty_lane: g.SUPERSEDE.length,
};
console.log(JSON.stringify(res));
""")
    r = subprocess.run(["node", str(out), json.dumps(FIXTURE)],
                       cwd=tmp_path, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    res = json.loads(r.stdout.strip())
    assert res["cand_n"] == 2 and res["cand_pct"] == 50.0 and res["cand_width"] == 100
    assert res["sup_n"] == 0 and res["sup_width"] == 0
    # groups sort oldest first within a lane
    assert res["cand_order"] == [12, 11]
    assert res["ext_numbers"] == [13]
    assert res["empty_lane"] == 0
