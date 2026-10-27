"""Admin control panel contract (Web Design lane, 2026-10-27).

The panel is a read-only projection over the web inventory: it must use the
shared design system, be reachable from every page's primary nav, be listed
in the sitemap, feed live from the Delphi panel config and the public
GitHub API, and never embed credentials or mutate state from the browser.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/help-wanted-dashboard"


def _admin():
    return (APP / "admin.html").read_text()


def test_admin_uses_shared_design_system_and_nav():
    html = _admin()
    assert "./dashboard.css" in html
    assert 'href="https://timerloggedout-spec.github.io/help-wanted/admin.html" aria-current="page"' in html


def test_admin_linked_from_every_dashboard_page():
    link = 'href="https://timerloggedout-spec.github.io/help-wanted/admin.html"'
    for page in ("index.html", "quota.html", "matrix.html"):
        assert link in (APP / page).read_text(), page


def test_admin_in_sitemap():
    assert "https://timerloggedout-spec.github.io/help-wanted/admin.html" in (APP / "sitemap.xml").read_text()


def test_admin_feeds_live_delphi_and_review_queue():
    html = _admin()
    assert "ops/delphi/panel.json" in html
    assert "api.github.com/repos/timerloggedout-spec/termux-monorepo" in html
    assert "issues/1489" in html and "issues/1487" in html
    assert "UNVERIFIED" in html  # honest fallback, never a guessed state


def test_admin_embeds_no_credentials_and_posts_nothing():
    html = _admin().lower()
    for forbidden in ("ghp_", "github_pat_", "bearer ", "authorization", "method:'post'", 'method:"post"', "method: 'post'"):
        assert forbidden not in html, forbidden
