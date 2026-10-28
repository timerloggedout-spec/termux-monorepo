"""Pins for the proposals index page (proposals-feed/v1).

The page renders ONLY data/proposals-feed.json, collected from the
registry of record. Filter facets are built from the feed's own
values; no proposal id, status, priority or author is hardcoded.
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "help-wanted-dashboard"
PAGE = APP / "proposals.html"
FEED = APP / "data" / "proposals-feed.json"
BASE = "https://timerloggedout-spec.github.io/help-wanted/"


def _html():
    return PAGE.read_text(encoding="utf-8")


def test_page_consumes_only_the_proposals_feed():
    html = _html()
    assert "./dashboard.css" in html
    fetches = re.findall(r"fetch\(([^)]*)\)", html)
    assert fetches == ["'./data/proposals-feed.json'"], fetches
    assert "api.github.com" not in html and "raw.githubusercontent" not in html
    assert "nothing is shown rather than anything guessed" in html
    assert "sk-" not in html and "ghp_" not in html


def test_filters_built_from_feed_values():
    html = _html()
    for fid in ('id="f-status"', 'id="f-priority"', 'id="f-author"', 'id="f-text"'):
        assert fid in html
    assert "facetValues" in html  # options come from the feed at runtime
    feed = json.loads(FEED.read_text())
    # no registry value is hardcoded into the page
    for p in feed["proposals"][:10]:
        assert p["id"] not in html and p["title"] not in html


def test_feed_matches_registry_of_record():
    feed = json.loads(FEED.read_text())
    assert feed["schema"] == "proposals-feed/v1"
    assert feed["counts"]["total"] == len(feed["proposals"])
    for p in feed["proposals"]:
        assert p["url"] == ("https://github.com/timerloggedout-spec/termux-monorepo"
                            "/tree/master/docs/proposals/" + p["path"])
    assert feed["counts"]["passes"] == len(feed["passes"]) == 3
    by_id = {p["id"]: p for p in feed["passes"]}
    # each pass's own status, verbatim from its pass.json
    assert by_id["temporal-durable-execution"]["status"] == "recorded"
    assert by_id["strands-rfp-response"]["status"] == "recorded"
    assert by_id["kiroween-delphi-concept"]["status"] == "stated_not_run"
    assert feed["gaps"] == []


def test_chrome_wiring():
    link = f'href="{BASE}proposals.html"'
    for other in ("index.html", "quota.html", "admin.html", "oracle.html", "3l0.html",
                  "moneyball.html", "mvt.html", "doe.html", "ates.html",
                  "free-tier-value.html", "dispatch-tree.html", "countdowns.html",
                  "linguist.html", "delphi-rfp.html", "delphi-ledger.html", "pr-lanes.html"):
        assert link in (APP / other).read_text(), f"{other} nav missing proposals"
    assert f'{link} aria-current="page"' in _html()
    assert f"{BASE}proposals.html" in (APP / "sitemap.xml").read_text()
    assert "<td>Proposals</td>" in (APP / "admin.html").read_text()


def test_node_sim_filters(tmp_path):
    html = _html()
    logic = html.split("// ==== pure logic (node-sim tested) ====")[1].split("// ==== end pure logic ====")[0]
    fixture = {"proposals": [
        {"id": "a", "title": "Alpha", "status": "posted", "priority": "P1", "author": "grok"},
        {"id": "b", "title": "Beta", "status": "executing", "priority": "P0", "author": "grok"},
        {"id": "c", "title": "Gamma", "status": "posted", "priority": "P0", "author": "Claude"},
    ]}
    harness = tmp_path / "harness.cjs"
    harness.write_text(f"const FEED={json.dumps(fixture)};\n{logic}\nmodule.exports={{filterProposals, facetValues}};\n")
    out = tmp_path / "run.cjs"
    out.write_text("""
const {filterProposals, facetValues} = require("./harness.cjs");
const FEED = JSON.parse(process.argv[2]);
const ids = f => filterProposals(FEED, f).map(p => p.id);
console.log(JSON.stringify({
  all: ids({}), byStatus: ids({status: "posted"}),
  byAuthorPrio: ids({author: "grok", priority: "P0"}),
  byText: ids({text: "amm"}), facets: facetValues(FEED, "status"),
}));
""")
    r = subprocess.run(["node", str(out), json.dumps(fixture)],
                       cwd=tmp_path, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    res = json.loads(r.stdout.strip())
    assert res["all"] == ["a", "b", "c"]
    assert res["byStatus"] == ["a", "c"]
    assert res["byAuthorPrio"] == ["b"]
    assert res["byText"] == ["c"]
    assert res["facets"] == ["executing", "posted"]
