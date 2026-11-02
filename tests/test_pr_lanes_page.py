"""Pins for the PR-lanes page (phase 1: distribution + per-lane table).

The page renders ONLY data/pr-lane-feed.json — the byte-identical
mirror of ops/ml/pr-lane-feed.json that ml-pr-lane-classify.yml commits
alongside the source feed. No lane counts are hardcoded in the page;
Phase 2 (landed): the trend views render from the committed series mirror (data/pr-lane-series.jsonl) via chartkit, data-fed like everything else.
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "tribute-dashboard"
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
    assert fetches == ['"./data/pr-lane-feed.json"', '"./data/pr-lane-series.jsonl"'], fetches
    assert 'id="dist"' in html and 'id="tables"' in html and 'id="meta"' in html


def test_mirror_matches_source_feed():
    assert json.loads(MIRROR.read_text()) == json.loads(SOURCE.read_text())


def test_workflow_keeps_mirror_fresh():
    wf = WORKFLOW.read_text()
    assert "cp ops/ml/pr-lane-feed.json apps/tribute-dashboard/data/pr-lane-feed.json" in wf
    assert "apps/tribute-dashboard/data/pr-lane-feed.json" in wf.split("git add -A")[1].split("\n")[0]


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


SERIES_SOURCE = ROOT / "ops" / "ml" / "pr-lane-series.jsonl"
SERIES_MIRROR = APP / "data" / "pr-lane-series.jsonl"


def _series_records(text):
    # The seed line was committed without a trailing newline, so records
    # can be concatenated; decode the object stream rather than lines.
    dec, out, i = json.JSONDecoder(), [], 0
    while i < len(text):
        while i < len(text) and text[i] in " \n\r\t":
            i += 1
        if i >= len(text):
            break
        obj, j = dec.raw_decode(text, i)
        out.append(obj)
        i = j
    return out


def test_series_mirror_matches_source():
    assert SERIES_MIRROR.read_bytes() == SERIES_SOURCE.read_bytes()
    records = _series_records(SERIES_SOURCE.read_text())
    assert records and all("counts" in x and "generated_at" in x for x in records)


def test_workflow_mirrors_series_too():
    wf = WORKFLOW.read_text()
    # both commit paths mirror (initial + regenerate-on-conflict)
    assert wf.count("cp ops/ml/pr-lane-series.jsonl apps/tribute-dashboard/data/pr-lane-series.jsonl") == 2
    assert wf.count("cp ops/ml/pr-lane-feed.json apps/tribute-dashboard/data/pr-lane-feed.json") == 2


def test_chrome_wiring():
    """Web Design chrome (post-landing follow-up): the page is linked
    from every shell page's unified nav, marks itself current, is in
    the sitemap, and has an Admin inventory row."""
    link = 'href="https://timerloggedout-spec.github.io/help-wanted/pr-lanes.html"'
    for other in ("index.html", "quota.html", "admin.html", "oracle.html", "3l0.html",
                  "moneyball.html", "mvt.html", "doe.html", "ates.html",
                  "free-tier-value.html", "dispatch-tree.html", "countdowns.html",
                  "linguist.html", "delphi-rfp.html", "delphi-ledger.html"):
        assert link in (APP / other).read_text(), f"{other} nav missing pr-lanes"
    assert f'{link} aria-current="page"' in _html()
    assert "https://timerloggedout-spec.github.io/help-wanted/pr-lanes.html" in (APP / "sitemap.xml").read_text()
    assert "<td>PR Lanes</td>" in (APP / "admin.html").read_text()


# ---- phase 2: trend chart (chart standard) ----

SERIES = APP / "data" / "pr-lane-series.jsonl"


def _trend_js():
    blocks = re.findall(r"<script>(.*?)</script>", _html(), re.S)
    trend = [b for b in blocks if "parseSeries" in b]
    assert len(trend) == 1
    return trend[0]


def test_trend_hooks_present():
    html = _html()
    for hook in ['src="./chartkit.js"', 'id="trendchart"',
                 'id="trendstamp"', "CK.line", "CK.stampState"]:
        assert hook in html, hook


def test_trend_script_parses(tmp_path):
    f = tmp_path / "trend.js"
    f.write_text(_trend_js())
    r = subprocess.run(["node", "--check", str(f)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_node_sim_trend_points(tmp_path):
    logic = _trend_js().split(
        "// ==== pure logic (node-sim tested) ====")[1].split(
        "// ==== end pure logic ====")[0]
    harness = tmp_path / "harness.cjs"
    harness.write_text(logic)
    out = tmp_path / "run.cjs"
    out.write_text("""
const {parseSeries, pointsFor} = require("./harness.cjs");
const fs = require("fs");
const rows = parseSeries(fs.readFileSync(process.argv[2], "utf8"));
const feed = JSON.parse(fs.readFileSync(process.argv[3], "utf8"));
const last = rows[rows.length - 1];
console.log(JSON.stringify({
  n: rows.length,
  open: pointsFor(rows, "open_prs").map(p => p.v),
  last_counts: last.counts, last_open: last.open_prs,
  feed_counts: feed.counts, feed_open: feed.open_prs,
  sorted: rows.every((r, i) => i === 0 ||
    rows[i - 1].generated_at <= r.generated_at),
}));
""")
    r = subprocess.run(["node", str(out), str(SERIES), str(MIRROR)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    res = json.loads(r.stdout.strip())
    assert res["n"] >= 2 and res["sorted"]
    assert len(res["open"]) == res["n"]
    # the series' last snapshot is the current feed state
    assert res["last_counts"] == res["feed_counts"]
    assert res["last_open"] == res["feed_open"]
