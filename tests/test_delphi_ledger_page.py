"""Pins for delphi-ledger.html — the Delphi continuous-ledgers surface.

Render handoff (docs/ops/DELPHI-LEDGER-STORE.md, database-specialist
lane, 2026-10-28): render data/delphi-ledger-feed.json
(delphi-ledger-feed/v1) like the RFP feed — per-ledger
current.payload VERBATIM (no re-folding, no recomputed EWMA/Elo),
the events[] stream below it, excluded_noise named, living records
by version_key + snapshot_at. The page is a read-only projection;
the ledger issue comments and living bodies stay the source of
truth.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "help-wanted-dashboard"
PAGE = APP / "delphi-ledger.html"
FEED = APP / "data" / "delphi-ledger-feed.json"


def _html():
    return PAGE.read_text(encoding="utf-8")


def _feed():
    return json.loads(FEED.read_text(encoding="utf-8"))


def test_page_consumes_only_the_ledger_feed():
    html = _html()
    assert re.findall(r"fetch\(([^)]*)\)", html) == ['"./data/delphi-ledger-feed.json"']
    assert "api.github.com" not in html and "raw.githubusercontent" not in html
    assert "nothing is shown rather than anything guessed" in html
    assert "delphi-ledger-feed/v1" in html


def test_current_payload_verbatim_no_refold():
    html = _html()
    assert "JSON.stringify(cur.payload" in html or "JSON.stringify(L.current.payload" in html
    script = html.split("<script>", 1)[1]
    assert "reduce(" not in script, "no aggregation or re-folding in the render"
    assert "if(L.current)" in html  # null-safe: the generation ledger has no folded state
    assert "No folded current state" in html
    feed = _feed()
    assert feed["schema"] == "delphi-ledger-feed/v1"
    currents = [l for l in feed["ledgers"] if l["current"]]
    assert currents and all("payload" in l["current"] for l in currents)


def test_events_stream_and_excluded_noise_named():
    html = _html()
    assert "ev.headline" in html and "ev.event_key" in html and "if(ev.payload)" in html
    assert "Excluded noise" in html and "excluded_noise" in html
    feed = _feed()
    assert feed["summary"]["events"] == sum(len(l["events"]) for l in feed["ledgers"])
    assert feed["summary"]["excluded_noise"] == sum(l["excluded_noise"] for l in feed["ledgers"])


def test_living_records_by_version_key_and_snapshot():
    html = _html()
    assert "feed.living_records" in html
    assert "r.version_key" in html and "r.snapshot_at" in html and "esc(r.body" in html
    feed = _feed()
    for rec in feed["living_records"]:
        assert len(rec["version_key"]) == 64  # sha256 of the issue body
        assert rec["snapshot_at"]


def test_semantics_and_state_rule_verbatim():
    html = _html()
    assert "L.semantics" in html and "L.state_rule" in html
    assert "Semantics (verbatim)" in html and "State rule (verbatim)" in html


def test_nav_sitemap_admin():
    nav = "help-wanted/delphi-ledger.html"
    shell_pages = ["index.html", "quota.html", "admin.html", "oracle.html", "3l0.html",
                   "moneyball.html", "mvt.html", "doe.html", "ates.html", "free-tier-value.html",
                   "dispatch-tree.html", "countdowns.html", "linguist.html", "delphi-rfp.html",
                   "delphi-ledger.html"]
    for name in shell_pages:
        assert nav in (APP / name).read_text(encoding="utf-8"), name
    assert "delphi-ledger.html" in (APP / "sitemap.xml").read_text(encoding="utf-8")
    admin = (APP / "admin.html").read_text(encoding="utf-8")
    assert "<td>Delphi Ledgers</td>" in admin and "delphi-ledger-feed.json" in admin


def test_page_title_is_the_ledgers():
    html = _html()
    assert "<title>Delphi Ledgers" in html
    assert "Delphi RFP Flood" not in html.split("</head>", 1)[0]
