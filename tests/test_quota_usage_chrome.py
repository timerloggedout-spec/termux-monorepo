"""Chrome wiring for the Quota Usage shell page (web-design).

quota-usage.html shipped as a quota sub-page (PR #2360) and was promoted to
a full shell page by the nav-consistency pass: every shell page's primary
nav carries the Quota Usage anchor immediately after Quota, and the Admin
inventory lists the page. These tests pin that wiring only — the page's
own render/data contract lives in tests/test_quota_usage_page.py.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASH = ROOT / "apps" / "help-wanted-dashboard"

SHELL_PAGES = [
    "index", "quota", "admin", "oracle", "3l0", "moneyball", "mvt", "doe",
    "ates", "free-tier-value", "dispatch-tree", "countdowns", "linguist",
    "delphi-rfp", "delphi-ledger", "pr-lanes", "proposals", "quota-usage",
]
QUOTA_ANCHOR = ('<a href="https://timerloggedout-spec.github.io/help-wanted/'
                'quota.html">Quota</a>')
USAGE_ANCHOR = ('<a href="https://timerloggedout-spec.github.io/help-wanted/'
                'quota-usage.html">Quota Usage</a>')
USAGE_CURRENT = ('<a href="https://timerloggedout-spec.github.io/help-wanted/'
                 'quota-usage.html" aria-current="page">Quota Usage</a>')


def _nav(page: str) -> str:
    raw = (DASH / f"{page}.html").read_text(encoding="utf-8")
    m = re.search(r'<nav aria-label="Primary">(.*?)</nav>', raw, re.S)
    assert m, f"{page}: primary nav missing"
    return m.group(1)


def test_quota_usage_anchor_in_every_shell_nav_after_quota():
    for page in SHELL_PAGES:
        nav = _nav(page)
        assert nav.count("quota-usage.html") == 1, page
        if page == "quota":
            # quota.html marks its own anchor current; the Usage anchor
            # still follows it immediately.
            assert 'quota.html" aria-current="page">Quota</a>' + USAGE_ANCHOR in nav, page
        elif page == "quota-usage":
            assert USAGE_CURRENT in nav, page
        else:
            assert QUOTA_ANCHOR + USAGE_ANCHOR in nav, page


def test_only_quota_usage_marks_itself_current():
    for page in SHELL_PAGES:
        nav = _nav(page)
        if page == "quota-usage":
            assert USAGE_CURRENT in nav
        else:
            assert USAGE_CURRENT not in nav, page


def test_admin_inventory_lists_quota_usage():
    admin = (DASH / "admin.html").read_text(encoding="utf-8")
    assert "<td>Quota Usage</td>" in admin
    assert '<a href="./quota-usage.html">quota-usage.html</a>' in admin
