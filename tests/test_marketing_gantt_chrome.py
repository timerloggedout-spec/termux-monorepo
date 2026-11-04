"""Chrome contract for the Marketing Gantt page (canon 38)."""
import re
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "apps" / "tribute-dashboard"
PAGE = (APP / "marketing-gantt.html").read_text(encoding="utf-8")
BASE = "https://timerloggedout-spec.github.io/tribute/"


def anchors(html):
    nav = re.search(r'<nav aria-label="Primary">(.*?)</nav>', html, re.S).group(1)
    return re.findall(r'href="([^"]+)"', nav)


def test_nav_canon_38_with_gantt_after_referrals():
    a = anchors(PAGE)
    assert len(a) == 38, len(a)
    assert a[a.index(BASE + "referrals.html") + 1] == BASE + "marketing-gantt.html"


def test_own_anchor_marked_current():
    assert PAGE.count('aria-current="page"') == 1
    assert BASE + 'marketing-gantt.html" aria-current="page"' in PAGE


def test_feed_driven_scaffold():
    assert 'fetch("./data/marketing-gantt.json",{cache:"no-store"})' in PAGE
    for el in ('id="gconstraint"', 'id="gmiles"', 'id="gaccounts"', 'id="gchart"'):
        assert el in PAGE, el
    assert "marketing-gantt/1" in PAGE
