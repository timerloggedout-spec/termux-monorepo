"""Nav-uniformity ratchet (owner order 2026-11-01).

Canonical-root rule (owner, 2026-11-01): FLEET-WIDE - every lane and
every template trigger names ONE canonical root per surface family
and points canonical links/tags at it; a migrated root is the state
of record and its former root is a legacy address, never a co-equal
twin. First application: this dashboard family - canonical root
/tribute/, /help-wanted/ is legacy.

The header drifted three times (landing froze at 5 links, previews at
27, matrix.html at 20) because every page carries its own copy of the
nav and nothing failed when one copy lagged. This test is the lock:
every page that carries the Primary nav must carry the SAME anchor
sequence, exactly, and the set of nav-carrying pages is pinned — a
page silently losing its nav, a new page shipping without one, or one
link added to one page all fail CI until the change is made
everywhere on purpose.
"""
import re
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "apps" / "tribute-dashboard"
NAV_RE = re.compile(r'<nav aria-label="Primary">(.*?)</nav>', re.S)
ANCHOR_RE = re.compile(r'<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>')

CANON = [
    ('https://timerloggedout-spec.github.io/', 'Autonomous AI Employees'),
    ('https://timerloggedout-spec.github.io/', 'Marketing'),
    ('https://timerloggedout-spec.github.io/tribute/', 'Ops · Tribute'),
    ('https://timerloggedout-spec.github.io/matrix/', 'Lane matrix'),
    ('https://timerloggedout-spec.github.io/tribute/quota.html', 'Quota'),
    ('https://timerloggedout-spec.github.io/tribute/quota-usage.html', 'Quota Usage'),
    ('https://timerloggedout-spec.github.io/tribute/quota-graphs.html', 'Quota Graphs'),
    ('https://timerloggedout-spec.github.io/tribute/quota-swarm.html', 'Swarm Quota'),
    ('https://timerloggedout-spec.github.io/tribute/admin.html', 'Admin'),
    ('https://timerloggedout-spec.github.io/tribute/oracle.html', 'Oracle'),
    ('https://timerloggedout-spec.github.io/tribute/3l0.html', '3L0'),
    ('https://timerloggedout-spec.github.io/tribute/moneyball.html', 'MoneyBall'),
    ('https://timerloggedout-spec.github.io/tribute/wagering-book.html', 'Wagering Book'),
    ('https://timerloggedout-spec.github.io/tribute/mvt.html', 'MVT'),
    ('https://timerloggedout-spec.github.io/tribute/doe.html', 'DoE'),
    ('https://timerloggedout-spec.github.io/tribute/ates.html', 'ATES'),
    ('https://timerloggedout-spec.github.io/tribute/results-index.html', 'Results Index'),
    ('https://timerloggedout-spec.github.io/tribute/free-tier-value.html', 'Free-tier value'),
    ('https://timerloggedout-spec.github.io/tribute/dispatch-tree.html', 'Dispatch Tree'),
    ('https://timerloggedout-spec.github.io/tribute/admin-graph.html', 'Admin Graph'),
    ('https://timerloggedout-spec.github.io/tribute/countdowns.html', 'Countdowns'),
    ('https://timerloggedout-spec.github.io/tribute/linguist.html', 'Linguist'),
    ('https://timerloggedout-spec.github.io/tribute/delphi-rfp.html', 'Delphi RFP'),
    ('https://timerloggedout-spec.github.io/tribute/delphi-ledger.html', 'Delphi Ledgers'),
    ('https://timerloggedout-spec.github.io/tribute/classifiers.html', 'Classifiers'),
    ('https://timerloggedout-spec.github.io/tribute/pr-lanes.html', 'PR Lanes'),
    ('https://timerloggedout-spec.github.io/tribute/proposals.html', 'Proposals'),
    ('https://timerloggedout-spec.github.io/tribute/telemetry.html', 'Telemetry'),
    ('https://timerloggedout-spec.github.io/tribute/desk.html', 'Desk'),
    ('https://timerloggedout-spec.github.io/tribute/tracking.html', 'Tracking'),
    ('https://timerloggedout-spec.github.io/tribute/family.html', 'Family'),
    ('https://Tribute-oversight.vercel.app/', 'Vercel deployment'),
    ('https://timerloggedout-spec.github.io/tribute/sitemap.xml', 'Sitemap'),
    ('https://github.com/timerloggedout-spec/termux-monorepo', 'Monorepo'),
]

# Pages carrying the shell nav. admin-graph.html (self-contained, zero
# outbound links by design), lanes-and-scopes.html and versioning.html
# carry none — that set is pinned too (see test_nav_carrier_set).
NAV_PAGES = {
    "index.html", "quota.html", "quota-usage.html", "quota-graphs.html",
    "admin.html", "oracle.html", "3l0.html", "moneyball.html", "wagering-book.html",
    "mvt.html", "doe.html", "ates.html", "results-index.html", "free-tier-value.html",
    "dispatch-tree.html", "countdowns.html", "linguist.html",
    "delphi-rfp.html", "delphi-ledger.html", "classifiers.html", "pr-lanes.html",
    "proposals.html", "telemetry.html", "desk.html", "tracking.html",
    "family.html", "quota-swarm.html",
}


def anchors(path):
    m = NAV_RE.search(path.read_text(encoding="utf-8"))
    return ANCHOR_RE.findall(m.group(1)) if m else None


def test_nav_carrier_set():
    carriers = {p.name for p in APP.glob("*.html") if NAV_RE.search(p.read_text(encoding="utf-8"))}
    assert carriers == NAV_PAGES, (
        f"nav-carrying pages changed: +{sorted(carriers - NAV_PAGES)} "
        f"-{sorted(NAV_PAGES - carriers)} — update the shell on purpose, everywhere")


def test_every_nav_identical():
    for name in sorted(NAV_PAGES):
        got = anchors(APP / name)
        assert got == CANON, (
            f"{name} nav drifted from canonical ({len(got or [])} vs {len(CANON)} links): "
            f"first diff at {next((i for i, (a, b) in enumerate(zip(got or [], CANON)) if a != b), None)}")


def test_site_nav_family_link():
    # matrix.html carries no static nav - it injects one from
    # site-nav.js at runtime (the cross-repo publisher's shared nav).
    # That list is pinned here for the family link instead.
    js = (APP / "site-nav.js").read_text(encoding="utf-8")
    assert '"tracking.html"' in js and '"family.html"' in js
    assert js.index('"tracking.html"') < js.index('"family.html"')
    assert "./site-nav.js" in (APP / "matrix.html").read_text(encoding="utf-8")
