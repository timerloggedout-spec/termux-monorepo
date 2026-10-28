"""Integration pins for linguist.html in the unified dashboard shell.

Stage-3 deploy (Web Design lane; pipeline: substrate -> viz prototype
PR #1863, re-pin PR #1891 -> this integration). The panel lane's
pre-merge checklist: chrome only — renderer script and element ids
unchanged; unified nav cross-linked on every published page;
sitemap entry; Admin inventory row. Renderer behavior itself is
pinned by tests/test_linguist_page.py.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "help-wanted-dashboard"
PAGE = APP / "linguist.html"
BASE = "https://timerloggedout-spec.github.io/help-wanted/"
PAGES = ["index.html", "quota.html", "matrix.html", "admin.html",
         "oracle.html", "moneyball.html", "3l0.html", "mvt.html",
         "doe.html", "ates.html", "free-tier-value.html",
         "dispatch-tree.html", "countdowns.html", "linguist.html"]
IDS = ["admin", "admin-count", "feed-absent", "gaps", "intext", "layers",
       "meta", "mode-cols", "mode-intext", "panel", "q", "sample-note",
       "span-detail", "text", "view-cols", "view-intext"]


def _html():
    return PAGE.read_text(encoding="utf-8")


def test_shared_shell_present():
    html = _html()
    assert '<link rel="stylesheet" href="./dashboard.css">' in html
    assert '<p class="eyebrow">Linguist · Mapping Panel</p>' in html
    assert f'href="{BASE}linguist.html" aria-current="page"' in html


def test_renderer_untouched_markers():
    html = _html()
    script = re.search(r"<script>(.*)</script>", html, re.S).group(1)
    assert "/* ---- page wiring ---- */" in script
    assert '"./data/linguist-panel-feed.json"' in script
    for element_id in IDS:
        assert f'id="{element_id}"' in html, element_id


def test_nav_cross_links_all_pages():
    linguist_link = f'href="{BASE}linguist.html"'
    for name in PAGES:
        text = (APP / name).read_text(encoding="utf-8")
        assert linguist_link in text, f"linguist nav link missing in {name}"
    own = _html()
    for name in PAGES:
        if name == "linguist.html":
            continue
        assert f'href="{BASE}{name}"' in own or (
            name == "index.html" and 'href="https://timerloggedout-spec.github.io/help-wanted/"' in own
        ) or (
            name == "matrix.html" and 'href="https://timerloggedout-spec.github.io/matrix/"' in own
        ), f"outbound nav link to {name} missing in linguist.html"


def test_sitemap_and_admin_row():
    sitemap = (APP / "sitemap.xml").read_text(encoding="utf-8")
    assert f"<loc>{BASE}linguist.html</loc>" in sitemap
    admin = (APP / "admin.html").read_text(encoding="utf-8")
    assert "<td>Linguist Panel</td>" in admin
    assert 'href="./linguist.html"' in admin
