"""Pins for the proposals index page (proposals-feed/v2).

The page renders ONLY data/proposals-feed.json, collected from the
registry of record. Filter facets are built from the feed's own
values; no proposal id, status, priority or author is hardcoded.
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "tribute-dashboard"
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
    assert feed["schema"] == "proposals-feed/v2"
    assert feed["counts"]["total"] == len(feed["proposals"])
    for p in feed["proposals"]:
        assert p["url"] == ("https://github.com/timerloggedout-spec/termux-monorepo"
                            "/tree/master/docs/proposals/" + p["path"])
    assert feed["counts"]["passes"] == len(feed["passes"])
    by_id = {p["id"]: p for p in feed["passes"]}
    # each pass's own status, verbatim from its pass.json
    assert by_id["temporal-durable-execution"]["status"] == "recorded"
    assert by_id["strands-rfp-response"]["status"] == "recorded"
    assert by_id["kiroween-delphi-concept"]["status"] == "debate_recorded"
    assert by_id["marketing-strategy-tactics"]["status"] == "round_1_recorded"
    # an unreadable pass.json ⇒ null fields + a gap naming the pass
    assert by_id["ai-studio-delphi-panel"]["status"] is None
    assert any("ai-studio-delphi-panel" in g for g in feed["gaps"])
    assert all(g.startswith("pass ") for g in feed["gaps"])


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


def test_pass_outcome_renders_ties_without_ordinals(tmp_path):
    """Tie law: equal scores render as one TIED group; the page never
    ranks tied candidates 1st/2nd. Sim uses the marketing pass ballot
    of record (BALLOT-round1.json: 23.269 = 23.269, 16.462)."""
    import shutil
    if not shutil.which("node"):
        import pytest
        pytest.skip("Node required")
    html = _html()
    m = re.search(r"// ==== pure logic \(node-sim tested\) ====([\s\S]*?)"
                  r"// ==== end pure logic ====", html)
    assert m, "pure-logic markers missing"
    esc_line = re.search(r"const esc=[^\n]*", html).group(0)
    sim = tmp_path / "sim.cjs"
    sim.write_text(esc_line + m.group(1)
                   + ";module.exports={outcomeCell};\n"
                   + "const pass={id:'marketing-strategy-tactics',outcome:"
                     "{scores:{'marketing-strategy-tactics-strict-"
                     "separation':23.269,'marketing-strategy-tactics-"
                     "attributed-tiered':23.269,'marketing-strategy-"
                     "tactics-partner-forward-blend':16.462}}};\n"
                   + "console.log(JSON.stringify({cell:outcomeCell(pass),"
                     "none:outcomeCell({id:'x'})}));\n")
    out = subprocess.run(["node", str(sim)], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    got = json.loads(out.stdout)
    assert "23.269 — TIED" in got["cell"]
    assert "attributed-tiered · strict-separation" in got["cell"]
    assert "16.462 — partner-forward-blend" in got["cell"]
    for ordinal in ("1st", "2nd", "#1", "rank"):
        assert ordinal not in got["cell"]
    assert got["none"] == "—"


def test_pass_table_has_outcome_column():
    html = _html()
    assert "<th>Outcome</th>" in html
    assert "outcomeCell(p)" in html


def test_feed_outcome_shape_when_present():
    feed = json.loads(FEED.read_text())
    for p in feed.get("passes", []):
        outcome = p.get("outcome")
        if outcome is None:
            continue
        assert isinstance(outcome.get("scores"), dict)
        for v in outcome["scores"].values():
            assert isinstance(v, (int, float))

def test_pr_state_chips_shape_tolerant(tmp_path):
    """proposals-feed/v2: prs entries are {number, state, merged_at}.
    merged = purple chip, open = green, closed-unmerged = red,
    unknown = NO chip; a v1 bare number renders the link alone."""
    import shutil
    if not shutil.which("node"):
        import pytest
        pytest.skip("Node required")
    html = _html()
    for cls in ("pr-chip merged", "pr-chip open", "pr-chip closed"):
        assert cls in html
    m = re.search(r"// ==== pure logic \(node-sim tested\) ====([\s\S]*?)"
                  r"// ==== end pure logic ====", html)
    assert m, "pure-logic markers missing"
    esc_line = re.search(r"const esc=[^\n]*", html).group(0)
    sim = tmp_path / "sim_pr.cjs"
    sim.write_text(esc_line + m.group(1)
                   + ";module.exports={prLink};\n"
                   + "const GH='https://github.com/timerloggedout-spec/termux-monorepo';\n"
                   + "console.log(JSON.stringify({"
                     "bare: prLink(123, GH),"
                     "merged: prLink({number:5,state:'merged',merged_at:'2026-11-01T00:00:00Z'}, GH),"
                     "open: prLink({number:6,state:'open',merged_at:null}, GH),"
                     "closed: prLink({number:7,state:'closed-unmerged',merged_at:null}, GH),"
                     "unknown: prLink({number:8,state:'unknown',merged_at:null}, GH)}));\n")
    out = subprocess.run(["node", str(sim)], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    got = json.loads(out.stdout)
    assert got["bare"].endswith('PR #123</a>') and "pr-chip" not in got["bare"]
    assert 'class="pr-chip merged"' in got["merged"]
    assert 'title="merged 2026-11-01T00:00:00Z"' in got["merged"]
    assert 'class="pr-chip open"' in got["open"]
    assert 'class="pr-chip closed"' in got["closed"]
    assert "pr-chip" not in got["unknown"] and 'PR #8</a>' in got["unknown"]

def test_feed_prs_shape_v2():
    """proposals-feed/v2 contract: every prs entry is an object whose
    state was resolved at collection; merged_at is set iff merged."""
    feed = json.loads(FEED.read_text())
    seen = 0
    for p in feed["proposals"]:
        for e in p.get("prs") or []:
            seen += 1
            assert isinstance(e, dict), (p["id"], e)
            assert isinstance(e["number"], int)
            assert e["state"] in ("open", "merged", "closed-unmerged", "unknown")
            if e["state"] == "merged":
                assert isinstance(e["merged_at"], str) and e["merged_at"]
            else:
                assert e["merged_at"] is None
    assert seen > 0

