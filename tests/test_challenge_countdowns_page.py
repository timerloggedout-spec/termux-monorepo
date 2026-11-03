"""Contract tests for countdowns.html (issue #1880, dashboard surface).

The page consumes only its own feed, computes state and remaining
time client-side from the stored instants on a 1s tick, and never
renders a baked remaining-seconds value.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "tribute-dashboard"
PAGE = APP / "countdowns.html"
FEED = APP / "data" / "challenge-countdowns-feed.json"
PAGES = ["index.html", "quota.html", "matrix.html", "admin.html",
         "oracle.html", "moneyball.html", "3l0.html", "mvt.html",
         "doe.html", "ates.html", "free-tier-value.html",
         "dispatch-tree.html", "countdowns.html"]
LINK = "https://timerloggedout-spec.github.io/help-wanted/countdowns.html"


def _page():
    return PAGE.read_text(encoding="utf-8")


def test_page_fetches_only_its_feed():
    html = _page()
    fetches = re.findall(r"fetch\(([^)]*)\)", html)
    assert fetches == ['"./data/challenge-countdowns-feed.json"'], fetches
    assert "api.github.com" not in html
    assert "raw.githubusercontent" not in html


def test_countdown_computed_client_side_from_instants():
    html = _page()
    assert "setInterval(tick,1000)" in html
    assert "Date.parse(e.opens)" in html and "Date.parse(e.closes)" in html
    assert "seconds_to" not in html, "page must never consume a baked remaining-seconds value"
    assert "Date.now()" in html


def test_honest_states_present():
    html = _page()
    for s in ("not recorded", "nothing is shown rather than anything guessed",
              "Overdue", "Completed"):
        assert s in html, s


def test_no_credential_markers():
    html = _page()
    for marker in ("ghp_", "github_pat_", "Bearer ", "api_key", "access_token"):
        assert marker not in html, marker


def test_nav_and_sitemap_wiring():
    for name in PAGES:
        text = (APP / name).read_text(encoding="utf-8")
        assert f'href="{LINK}"' in text, f"countdowns nav link missing in {name}"
    own = _page()
    assert f'href="{LINK}" aria-current="page"' in own
    sitemap = (APP / "sitemap.xml").read_text(encoding="utf-8")
    assert f"<loc>{LINK}</loc>" in sitemap


def test_feed_entries_renderable_shape():
    feed = json.loads(FEED.read_text(encoding="utf-8"))
    assert feed["schema"] == "challenge-countdowns-feed/v1.1"
    for e in feed["entries"]:
        assert e["title"] and e["id"].startswith("D")


def test_prizes_block_rendered_never_omitted():
    """Feed v1.1 (PR #2192): prizes are REQUIRED on this HITL page
    (contract honesty rule 5). Every card renders its entry's prizes
    block: tier lines (place \u2014 award), the pool line when present,
    and an unpublished prize set as the literal NOT_ESTABLISHED \u2014
    never blank, never omitted."""
    html = _page()
    assert "prizesHTML(e)" in html and "e.prizes" in html
    assert "NOT_ESTABLISHED" in html and "p.pool" in html
    assert "p.tiers" in html and "t.place" in html and "t.award" in html
    feed = json.loads(FEED.read_text(encoding="utf-8"))
    for e in feed["entries"]:
        pz = e["prizes"]
        assert pz["status"] in ("ESTABLISHED", "NOT_ESTABLISHED")
        if pz["status"] == "ESTABLISHED":
            assert pz["tiers"] or pz["pool"]
        for tier in pz["tiers"]:
            assert tier["place"] and tier["award"]

def test_submission_render_v12():
    """Feed v1.2: a non-null submission renders state + instant + confirmation
    link on the entry card; null (or absent) renders nothing."""
    import subprocess
    import tempfile
    html = _page()
    assert "function submissionHTML(e)" in html
    assert "submissionHTML(e)+" in html, "render() must append the submission block"
    def grab(pat):
        m = re.search(pat, html)
        assert m, pat
        return m.group(0)
    esc_line = grab(r"const esc=[^\n]*")
    pt_line = grab(r"const PT=[^\n]*")
    fmt_line = grab(r"function fmtInstant[^\n]*")
    fn = grab(r"function submissionHTML\(e\)\{[\s\S]*?\n\}")
    harness = esc_line + "\n" + pt_line + "\n" + fmt_line + "\n" + fn + """
const d1 = {submission: {state: "SUBMITTED", at: "2026-11-03T18:01:00Z",
  confirmation_ref: "https://builder.aws.com/project/3LRJu2KZOWsFqd5oGHyt52lcR5P/studysprint"}};
process.stdout.write(JSON.stringify({
  d1: submissionHTML(d1),
  nul: submissionHTML({submission: null}),
  absent: submissionHTML({}),
}));"""
    with tempfile.NamedTemporaryFile("w", suffix=".cjs", delete=False) as fh:
        fh.write(harness)
        path = fh.name
    out = subprocess.run(["node", path], capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    res = json.loads(out.stdout)
    assert "SUBMITTED" in res["d1"] and "badge ok" in res["d1"]
    assert "Nov 3" in res["d1"], res["d1"]  # the recorded instant, PT-formatted
    assert "https://builder.aws.com/project/3LRJu2KZOWsFqd5oGHyt52lcR5P/studysprint" in res["d1"]
    assert res["nul"] == "" and res["absent"] == ""

