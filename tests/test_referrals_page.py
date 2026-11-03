"""Pins for the referrals board page (referral-feed/1).

The page renders ONLY data/referral-feed.json, built by
scripts/referral/build_feed.py from config/referral_programs.json.
Honesty rules: pool_health null renders the pool absent (never 0/0),
accrued_value absent renders absent (never estimated), an empty
rotation log renders as an empty timeline, and a programme state the
chip map does not know renders as a neutral chip carrying the state
string verbatim (e.g. a future no_public_programme state).
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "tribute-dashboard"
PAGE = APP / "referrals.html"
FEED = APP / "data" / "referral-feed.json"
BASE = "https://timerloggedout-spec.github.io/tribute/"


def _html():
    return PAGE.read_text(encoding="utf-8")


def test_page_consumes_only_the_referral_feed():
    html = _html()
    assert "./dashboard.css" in html
    fetches = re.findall(r"fetch\(([^)]*)\)", html)
    assert fetches == ["'./data/referral-feed.json'"], fetches
    assert "api.github.com" not in html and "raw.githubusercontent" not in html
    assert "nothing is shown rather than anything guessed" in html
    assert "sk-" not in html and "ghp_" not in html


def test_feed_shape():
    feed = json.loads(FEED.read_text())
    assert feed["schema"] == "referral-feed/1"
    assert feed["generated_at"]
    assert feed["items"], "board must not be empty"
    for it in feed["items"]:
        assert it["id"] and it["name"] and it["state"]
        assert "pool_health" in it and "rotation_events" in it
        if it["pool_health"] is not None:
            assert set(it["pool_health"]) == {"live", "reserve", "exhausted"}
    assert isinstance(feed["rotation_log"], list)


def test_chrome_wiring():
    link = f'href="{BASE}referrals.html"'
    for other in ("index.html", "quota.html", "admin.html", "oracle.html",
                  "3l0.html", "moneyball.html", "wagering-book.html", "mvt.html",
                  "doe.html", "ates.html", "results-index.html",
                  "free-tier-value.html", "dispatch-tree.html", "countdowns.html",
                  "linguist.html", "delphi-rfp.html", "delphi-ledger.html",
                  "classifiers.html", "pr-lanes.html", "proposals.html",
                  "telemetry.html", "desk.html", "tracking.html", "family.html",
                  "quota-swarm.html", "quota-usage.html", "quota-graphs.html"):
        assert link in (APP / other).read_text(), f"{other} nav missing referrals"
    assert f'{link} aria-current="page"' in _html()
    assert f"{BASE}referrals.html" in (APP / "sitemap.xml").read_text()
    assert "<td>Referrals</td>" in (APP / "admin.html").read_text()
    assert '"referrals.html"' in (APP / "site-nav.js").read_text()
    manifest = json.loads((APP / "version-manifest.json").read_text())
    entry = [p for p in manifest["pages"] if p["file"] == "referrals.html"]
    assert entry and entry[0]["content_sha256"] is None
    assert '"referrals"' in (APP / "versioning.js").read_text()


def test_node_sim_against_live_feed(tmp_path):
    import shutil
    if not shutil.which("node"):
        import pytest
        pytest.skip("Node required")
    html = _html()
    esc_line = re.search(r"const esc=[^\n]*", html).group(0)
    logic = html.split("// ==== pure logic (node-sim tested) ====")[1].split(
        "// ==== end pure logic ====")[0]
    harness = tmp_path / "harness.cjs"
    harness.write_text(esc_line + "\n" + logic)
    out = tmp_path / "run.cjs"
    out.write_text("""
const {refStateDist, refChip, refPoolModel, refAccess, refValueLines} = require("./harness.cjs");
const feed = require(process.argv[2]);
const items = feed.items;
console.log(JSON.stringify({
  dist: refStateDist(items),
  n: items.length,
  poolsNull: items.filter(i => refPoolModel(i.pool_health) === null).length,
  poolsNullFeed: items.filter(i => i.pool_health === null).length,
  futureChip: refChip("no_public_programme"),
  harkChip: refChip(items.find(i => i.id === "hark").state),
  valueLines: Object.fromEntries(items.map(i => [i.id, refValueLines(i)])),
}));
""")
    r = subprocess.run(["node", str(out), str(FEED)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    res = json.loads(r.stdout.strip())
    # chart distribution sums to the programme count
    assert sum(x["value"] for x in res["dist"]) == res["n"]
    # null pools stay absent in the model exactly where the feed is null
    assert res["poolsNull"] == res["poolsNullFeed"] > 0
    # an unmapped state renders verbatim on a neutral chip, never dropped
    assert "no_public_programme" in res["futureChip"]
    assert 'class="ref-chip other"' in res["futureChip"]
    # hark renders whatever state the feed carries (pending today; the
    # no_public_programme form once the registry delta lands)
    feed = json.loads(FEED.read_text())
    hark = [i for i in feed["items"] if i["id"] == "hark"][0]
    assert hark["state"] in res["harkChip"]
    assert hark["state_detail"] == "no_public_programme"
    # value lines (accrued + redemptions counter) render present-only:
    # exactly the programmes whose feed items carry the fields
    for it in feed["items"]:
        lines = res["valueLines"][it["id"]]
        if "accrued_value" in it and it["accrued_value"] is not None:
            assert "Accrued: " in lines and it["accrued_value"] in lines
        else:
            assert "Accrued:" not in lines
        if "redemptions" in it and it["redemptions"] is not None:
            assert 'class="ref-count"' in lines
            assert ">" + str(it["redemptions"]) + "<" in lines
        else:
            assert "ref-count" not in lines
