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


def test_admin_renders_internal_win_probability():
    """Owner correction 2026-10-28 (contract docs/ops/ADMIN-INTERNAL-
    METRICS.md): win_probability renders on the Admin panel ONLY, from
    the challenge-admin-metrics/v1 feed, verbatim — the panel computes
    nothing. Null estimate renders as the words "not established"
    (never 0 or blank); an unsourced field size renders OPEN TASK,
    a state distinct from the estimate null."""
    html = _admin()
    assert "./data/challenge-admin-metrics.json" in html
    assert "win_probability" in html and "metrics" in html
    assert "not established" in html and "OPEN TASK" in html
    assert "PARTIAL" in html  # amendment 2: partial field size carries the chip
    assert "INTERNAL" in html
    assert "computes nothing" in html


def test_win_probability_stays_off_public_surfaces():
    """Forbidden-surface scan (contract acceptance b): the metric must
    appear in NO public page and NO data feed except admin.html and
    its designated internal feed."""
    for page in APP.glob("*.html"):
        if page.name == "admin.html":
            continue
        text = page.read_text()
        assert "win_probability" not in text, page.name
        assert "metrics_internal" not in text, page.name
    for feed_file in (APP / "data").glob("*.json"):
        if feed_file.name == "challenge-admin-metrics.json":
            continue
        text = feed_file.read_text()
        assert "win_probability" not in text, feed_file.name
        assert "metrics_internal" not in text, feed_file.name


def test_admin_renders_winprob_v2_range_and_confidence():
    """winprob/v2 (feed PR #2251): the estimate now carries a range and
    a confidence; realized events read a recorded 0 (never confused
    with the null "not established"). The v1 history block
    (superseded_v1) is NOT rendered — it stays in the feed/record.
    Field-size states (amendment 2) are unchanged."""
    html = _admin()
    assert "w.range" in html and "w.confidence" in html
    assert "w.prior" in html and "w.unknowns" in html and "w.fit" in html
    assert "superseded_v1" not in html
    assert "0% — realized" in html  # amendment 3: realized events, never bare 0%
    # acceptance (e): the v2 renderer reads no v1 field for headline values
    fn = html.split("async function loadChallenge(){")[1].split("async function load(){")[0]
    assert ".inputs" not in fn and "superseded_v1" not in fn


def test_admin_renders_gearbox_consumer_controls():
    """Gearbox consumer controls (owner order 2026-10-29): the pack schema
    renders on the Admin panel only — design-only, inert, honesty verbatim."""
    html = _admin()
    assert 'data-feed="gearbox"' in html
    assert 'id="gearbox-controls"' in html and 'id="gearbox-meta"' in html
    assert "async function loadGearbox(){" in html
    assert "jget('./data/quota-usage.json')" in html
    fn = html.split("async function loadGearbox(){")[1].split("async function load(){")[0]
    for marker in ("consumer_controls", "diagnose_dependency", "guardrail_ruling",
                   "subset_selection", "settings_example", "shift_log_type",
                   "honesty", "audit_event", "admin_designation"):
        assert marker in fn, marker
    # controls render as inert designs (disabled), never live inputs
    assert 'type="button" disabled' in fn
    assert 'type="range"' in fn and "disabled" in fn
    assert 'type="checkbox" disabled' in fn
