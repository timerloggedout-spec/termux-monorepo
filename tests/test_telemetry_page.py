"""Telemetry page contract (Web Design lane).

telemetry.html is the 19th shell page, rendering ONLY
data/telemetry-feed.json (telemetry-viz-feed/v1) per recon §4 grammar:
golden top-row → executions → outcomes → quota. Honesty is pinned here:
a null quota_saturation renders as NOT OBSERVED, never 0; executions
carry their committed-projection proxy label; gaps surface verbatim.
"""
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/help-wanted-dashboard"

SHELL_PAGES = [
    "index", "quota", "admin", "oracle", "3l0", "moneyball", "mvt", "doe",
    "ates", "free-tier-value", "dispatch-tree", "countdowns", "linguist",
    "delphi-rfp", "delphi-ledger", "pr-lanes", "proposals", "quota-usage",
    "telemetry",
]
TEL_ANCHOR = ('<a href="https://timerloggedout-spec.github.io/help-wanted/'
              'telemetry.html">Telemetry</a>')
TEL_CURRENT = ('<a href="https://timerloggedout-spec.github.io/help-wanted/'
               'telemetry.html" aria-current="page">Telemetry</a>')


def _page():
    return (APP / "telemetry.html").read_text(encoding="utf-8")


def _script():
    html = _page()
    m = re.search(r"<script>(.*?)</script>", html, re.S)
    assert m, "inline script missing"
    return m.group(1)


def _nav(page: str) -> str:
    raw = (APP / f"{page}.html").read_text(encoding="utf-8")
    m = re.search(r'<nav aria-label="Primary">(.*?)</nav>', raw, re.S)
    assert m, f"{page}: primary nav missing"
    return m.group(1)


def test_telemetry_page_fetches_only_its_own_feed():
    script = _script()
    assert script.count("fetch(") == 1
    assert "fetch('./data/telemetry-feed.json'" in script
    assert "api.github.com" not in script and "raw.githubusercontent" not in script


def test_telemetry_anchor_in_every_shell_nav():
    for page in SHELL_PAGES:
        nav = _nav(page)
        assert nav.count("telemetry.html") == 1, page
        if page == "telemetry":
            assert TEL_CURRENT in nav
        else:
            assert TEL_CURRENT not in nav, page
            assert TEL_ANCHOR in nav, page


def test_telemetry_render_honors_null_saturation_and_proxy_label():
    script = _script()
    assert "quota_saturation==null" in script
    assert "NOT OBSERVED" in script
    assert "committed_projection_proxy" not in script  # label comes from feed, not code
    assert "ex.kind" in script and "ex.read_at" in script
    assert "gaps" in script and "honesty_rules" in script


def test_telemetry_in_admin_inventory_and_sitemap():
    admin = (APP / "admin.html").read_text(encoding="utf-8")
    assert "<td>Telemetry</td>" in admin
    assert '<a href="./telemetry.html">telemetry.html</a>' in admin
    sitemap = (APP / "sitemap.xml").read_text(encoding="utf-8")
    assert "help-wanted/telemetry.html" in sitemap


def test_telemetry_inline_script_parses():
    if not shutil.which("node"):
        return
    Path("/tmp/telemetry-script.js").write_text(_script(), encoding="utf-8")
    r = subprocess.run(["node", "--check", "/tmp/telemetry-script.js"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
