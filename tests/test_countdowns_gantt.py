"""Pins for the Gantt + swimlane views on countdowns.html.

Owner ruling (2026-10-27): Gantt is the primary timeline view,
swimlane an additional view on the same page. Both draw ONLY the
instants recorded in the countdowns feed — bars need both an opens
and a closes instant; a deadline-only entry renders as a milestone,
never as an invented span.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "help-wanted-dashboard"
PAGE = APP / "countdowns.html"


def _html():
    return PAGE.read_text(encoding="utf-8")


def test_gantt_and_swimlane_sections_present():
    html = _html()
    assert 'id="gantt"' in html and 'id="gantt-note"' in html
    assert 'id="lanes"' in html
    assert "Programme timeline — Gantt" in html
    assert "Swimlanes — by state" in html
    for lane in ("Upcoming", "In window", "Ended"):
        assert f'"{lane}"' in html or f">{lane}" in html or lane in html


def test_gantt_draws_only_recorded_instants():
    html = _html()
    assert "function renderGantt()" in html
    # no hardcoded calendar dates anywhere in the page source
    assert not re.search(r"20\d\d-\d\d-\d\d", html), "page must not bake dates"
    # milestone path exists for opens==null entries (polygon diamond)
    assert "<polygon" in html
    # bars require both instants
    assert "o!==null && c!==null" in html


def test_views_refresh_with_the_tick():
    html = _html()
    assert "renderLanes();" in html
    assert "renderGantt();" in html
    assert "%30===0" in html  # gantt re-renders throttled, lanes every tick


def test_no_new_data_sources():
    html = _html()
    fetches = re.findall(r"fetch\(([^)]*)\)", html)
    assert fetches == ['"./data/challenge-countdowns-feed.json"'], fetches
