"""Pins for delphi-rfp.html — the Delphi RFP flood surface.

Owner requirement (2026-10-27): the page shows the flood's progress
& status + criteria + questions + outcomes, and RENDERS THE
RESPONSES (the panel's signed votes) in the page. Feed:
data/delphi-rfp-feed.json (delphi-rfp-feed/v1, contract
docs/ops/DELPHI-RFP-FEED.md, Delphi lane owns the data). Render
discipline: votes/outcomes verbatim — nothing re-scored or averaged;
status is the gate's award (feed status), converged is its own
field; unscored filings render their recorded gap text.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "help-wanted-dashboard"
PAGE = APP / "delphi-rfp.html"
FEED = APP / "data" / "delphi-rfp-feed.json"


def _html():
    return PAGE.read_text(encoding="utf-8")


def _feed():
    return json.loads(FEED.read_text(encoding="utf-8"))


def test_page_consumes_only_the_rfp_feed():
    html = _html()
    assert re.findall(r"fetch\(([^)]*)\)", html) == ['"./data/delphi-rfp-feed.json"']
    assert "api.github.com" not in html and "raw.githubusercontent" not in html
    assert "nothing is shown rather than anything guessed" in html


def test_progress_criteria_honesty_rendered_from_feed():
    html = _html()
    assert 'id="summary"' in html and "feed.summary" in html
    assert 'id="criteria"' in html and "feed.criteria" in html
    assert "shadow bar" in html and "money_veto" in html
    assert 'id="honesty"' in html and "feed.honesty_rules" in html


def test_responses_rendered_verbatim_no_rescoring():
    html = _html()
    assert "esc(v.reason)" in html and "esc(v.signed)" in html and "esc(v.role)" in html and "esc(v.via||" in html
    script = html.split("<script>", 1)[1]
    assert "reduce(" not in script, "no aggregation over votes in the render"
    feed = _feed()
    assert feed["schema"] == "delphi-rfp-feed/v1"
    assert feed["summary"]["total_open"] == len(feed["rfps"]) == 70


def test_status_is_award_converged_is_separate_unscored_shows_gap():
    html = _html()
    assert "aw.decision" in html  # chip text from the gate award when present
    assert 'data-conv' in html and "converged only" in html
    assert "r.gaps" in html and "Recorded gaps" in html
    assert "if(r.responses)" in html and "if(oc)" in html  # null-safe unscored path
    assert "comparison_axes" in html  # research axes rendered when present


def test_questions_and_outcome_blocks():
    html = _html()
    assert "responses as filed" in html and "q.question" in html and "q.response" in html
    assert "oc.award_line" in html and "roundsTable(oc.rounds)" in html


def test_nav_sitemap_admin_and_oracle_link():
    nav = "help-wanted/delphi-rfp.html"
    shell_pages = ["index.html", "quota.html", "admin.html", "oracle.html", "3l0.html",
                   "moneyball.html", "mvt.html", "doe.html", "ates.html", "free-tier-value.html",
                   "dispatch-tree.html", "countdowns.html", "linguist.html", "delphi-rfp.html"]
    for name in shell_pages:
        assert nav in (APP / name).read_text(encoding="utf-8"), name
    assert "delphi-rfp.html" in (APP / "sitemap.xml").read_text(encoding="utf-8")
    admin = (APP / "admin.html").read_text(encoding="utf-8")
    assert "<td>Delphi RFP</td>" in admin and "delphi-rfp-feed.json" in admin
    oracle = (APP / "oracle.html").read_text(encoding="utf-8")
    assert 'href="./delphi-rfp.html"' in oracle
    assert "oracle-panel-feed.json" in oracle
    # the strip names the flood feed once but never fetches it
    assert oracle.count("delphi-rfp-feed.json") == 1
    assert 'fetch("./data/delphi-rfp-feed.json"' not in oracle


def test_v11_progress_parent_and_criteria_items():
    """Feed v1.1 (PR #1952): per-RFP progress{} raw counts, variant
    parent{} refs, criteria.items[] — all consumed by the render."""
    html = _html()
    assert "r.progress" in html and "pg.rounds_run" in html and "pg.votes_cast" in html
    assert "r.parent" in html and 'id="rfp-' in html
    assert "c.items" in html


def test_page_title_is_the_rfp_flood_not_the_shell_donor():
    html = _html()
    assert "<title>Delphi RFP Flood" in html
    assert "Challenge Countdowns" not in html.split("<script>", 1)[0].split("</head>", 1)[0]
