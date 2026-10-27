"""The surface pages consume their feed and nothing else.

Per page: the only data fetch is its own feed JSON in data/, the honesty
renderers are present, the page is wired into the unified nav and the
sitemap, and no credentials or other endpoints appear anywhere.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "help-wanted-dashboard"
BASE = "https://timerloggedout-spec.github.io/help-wanted/"


def _html(page: str) -> str:
    return (APP / page).read_text()


def _feed(name: str) -> dict:
    return json.loads((APP / "data" / name).read_text())


def _check_page(page: str, feed_name: str) -> str:
    html = _html(page)
    assert "./dashboard.css" in html
    assert f"./data/{feed_name}" in html, "page must fetch its own feed"
    assert "api.github.com" not in html and "raw.githubusercontent" not in html
    fetches = re.findall(r'fetch\("([^"]+)"\)', html)
    assert fetches == [f"./data/{feed_name}"], fetches
    assert "nothing is shown rather than anything guessed" in html
    assert "sk-" not in html and "ghp_" not in html and "BEGIN" not in html
    link = f'href="{BASE}{page}"'
    for other in ("index.html", "quota.html", "matrix.html", "admin.html", "oracle.html", "moneyball.html", "3l0.html", "mvt.html", "doe.html", "ates.html", "free-tier-value.html"):
        assert link in _html(other), f"{other} nav missing {page}"
    assert f"{BASE}{page}" in (APP / "sitemap.xml").read_text()
    return html


def test_moneyball_page():
    html = _check_page("moneyball.html", "moneyball-feed.json")
    feed = _feed("moneyball-feed.json")
    # the page renders the weights table from the feed, never hardcoded values
    for signal in feed["data"]["weights"]:
        assert signal not in html or signal in ("fresh", "draft", "dirty"), signal
    assert 'aria-current="page"' in html
    assert "gaps" in html  # honest-gap block is rendered


def test_3l0_page():
    html = _check_page("3l0.html", "3l0-feed.json")
    feed = _feed("3l0-feed.json")
    ranked = feed["data"]["response_history"]["providers_ranked"]
    assert ranked  # the feed carries a ranked provider record
    # record values are rendered from the feed at runtime, never hardcoded
    for p in ranked:
        if p["delivery_rate"] is not None:
            assert str(p["delivery_rate"]) not in html, p["provider"]
    for tail in feed["data"]["response_history"]["history_tail"].values():
        for h in tail:
            assert h["cycle_id"] not in html
    assert feed["gaps"]  # the no-rankings-table gap must be named in the feed


def test_mvt_page():
    html = _check_page("mvt.html", "mvt-feed.json")
    feed = _feed("mvt-feed.json")
    assert feed["data"]["experiment_loop"]["state"] == "defined_not_run"
    assert "Defined — not run" in html  # the not-run state is rendered, not hidden
    assert feed["gaps"]  # no committed experiment records — named in the feed
    # separation (PR #1756): the harness and fixtures moved to the ATES page
    assert "d.harness" not in html and "d.fixtures" not in html
    assert "invariants" not in feed["data"] and "fixtures" not in feed["data"]
    assert {c["surface"] for c in feed["data"]["citations"]} == {"ates", "doe"}


def test_ates_page():
    html = _check_page("ates.html", "ates-feed.json")
    feed = _feed("ates-feed.json")
    assert len(feed["data"]["invariants"]) == 7
    runs = {w["name"]: w["observed_runs"]["total_runs"] for w in feed["data"]["workflows"]}
    assert runs["ATES Orchestrator Benchmark"] > 0
    assert runs["Agent MVT experiment loop"] == 0  # defined, not run — rendered as such
    assert "Defined — not run" in html
    assert {c["surface"] for c in feed["data"]["citations"]} == {"mvt", "doe"}


def test_doe_page():
    html = _check_page("doe.html", "doe-feed.json")
    feed = _feed("doe-feed.json")
    assert feed["data"]["dspy_lane"]["state"] == "design_only"
    assert "Design only — not run" in html
    fns = feed["data"]["methods_library"]["functions"]
    assert [f["name"] for f in fns] == ["full_factorial", "taguchi_l9", "mvt_shuffle"]
    # separation (PR #1756): executed comparisons are a citation, never a payload
    assert "executed_comparisons" not in html and "executed_comparisons" not in feed["data"]
    assert "DoE results: none" in html
    assert feed["data"]["citations"][0]["surface"] == "delphi"
