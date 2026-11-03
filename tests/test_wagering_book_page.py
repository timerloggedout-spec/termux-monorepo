"""Pins for the wagering-book Gantt + public book page.

The page renders ONLY data/wagering-book.json (schema
moneyball.wagering-book/v2), built by
scripts/moneyball/wagering_book_feed.py from MoneyBall's
publication feed (book-feed.json, agentic-gambling-book-feed/v1)
at ledger truth. Owner publication ruling 2026-11-02: public
read-only view; published values equal ledger values by
construction; expectation nulls render INTAKE (no estimate),
never 0; the ledger's bookkeeping notes do NOT render (flag 4) -
the ledger rides by reference only; forecast is an OUTPUT class.
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "tribute-dashboard"
PAGE = APP / "wagering-book.html"
FEED = ROOT / "ops" / "moneyball" / "wagering-book.json"
MIRROR = APP / "data" / "wagering-book.json"
FIXTURE = ROOT / "tests" / "fixtures" / "wagering-book.fixture.json"
BOOKFEED = ROOT / "ops" / "agentic-gambling" / "book" / "book-feed.json"
LEDGER = ROOT / "ops" / "agentic-gambling" / "book" / "ledger.jsonl"


def _feed():
    return json.loads(FEED.read_text())


def _html():
    return PAGE.read_text(encoding="utf-8")


def test_mirror_is_byte_identical():
    assert MIRROR.read_bytes() == FEED.read_bytes()


def test_page_consumes_only_the_feed():
    fetches = re.findall(r"fetch\(([^)]*)\)", _html())
    assert fetches == ['"./data/wagering-book.json"'], fetches


def test_feed_shape_and_counts():
    feed = _feed()
    assert feed["schema"] == "moneyball.wagering-book/v2"
    subs = feed["subjects"]
    assert len(subs) == feed["book"]["subjects"] == 26
    fams = {}
    for s in subs:
        fams[s["family"]] = fams.get(s["family"], 0) + 1
    assert fams == {"D1": 2, "D2": 3, "D3": 4, "D4": 4, "D5": 3,
                    "AMD": 6, "FCC": 1}
    assert all("forecast" not in s["id"] for s in subs)
    assert "OUTPUT" in feed["forecast_layer"]
    assert "no external participation" in feed["publication"]


def test_bookfeed_parity_by_construction():
    bf = json.loads(BOOKFEED.read_text())
    feed = _feed()
    assert feed["positions"] == bf["positions"]
    assert feed["feed_settlements"] == bf["settlements"]
    assert feed["publishability_flags"] == bf["publishability_flags"]
    assert [s["id"] for s in feed["subjects"]] == \
        [s["id"] for s in bf["subjects"]]
    by = {s["id"]: s for s in feed["subjects"]}
    for bs in bf["subjects"]:
        exp = by[bs["id"]]["expectation"]
        be = bs["expectation_record"]
        assert exp["prior_value"] == be["prior"]["value"]
        assert exp["posterior_value"] == be["posterior"]["value"]
        assert exp["n_evidence"] == be["posterior"]["n_evidence"]
        assert by[bs["id"]]["settles_by"] == bs["settle"]["source"]
        assert by[bs["id"]]["settlement"]["value"] == bs["settle"]["value"]
        assert by[bs["id"]]["record_of_record"] == bs["record_of_record"]


def test_ledger_by_reference_only():
    feed = _feed()
    n = sum(1 for l in LEDGER.read_text().splitlines() if l.strip())
    assert feed["ledger_ref"]["entries"] == n
    assert "book_opened" not in FEED.read_text()
    assert 'id="ledger"' not in _html()


def test_anchor_derivations():
    from datetime import datetime, timedelta
    for s in _feed()["subjects"]:
        if s["final_at"]:
            wall = datetime.fromisoformat(s["wall_at"])
            fin = datetime.fromisoformat(s["final_at"])
            assert wall - fin == timedelta(minutes=30), s["id"]
        if s["knowable"]["kind"] == "rule":
            assert s["knowable"]["at"] is None
        else:
            assert s["knowable"]["at"]
    by = {s["id"]: s for s in _feed()["subjects"]}
    assert by["D2-3-nocard-account-live"]["wall_at"] is None
    assert by["D5-14-spot-confirmation"]["wall_at"] is None
    assert by["AMD-17-gpu100-claim"]["landing_at"] is None
    assert by["AMD-18-m4-submitted"]["wall_at"] is None
    assert by["FCC-23-relational-db-cert"]["wall_soft"] is True
    assert by["D5-16-placement-winner"]["knowable"]["at"] == \
        "2026-11-20T11:30:00-08:00"
    assert by["D5-16-placement-winner"]["wall_at"] == \
        "2026-11-19T12:00:00-08:00"


def test_no_winprob_rendered():
    assert "winprob" not in _html().lower()


def test_full_script_parses(tmp_path):
    script = _html().split("<script>")[1].split("</script>")[0]
    f = tmp_path / "page.js"
    f.write_text(script)
    r = subprocess.run(["node", "--check", str(f)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_node_sim(tmp_path):
    html = _html()
    logic = html.split("// ==== pure logic (node-sim tested) ====")[1] \
        .split("// ==== end pure logic ====")[0]
    harness = tmp_path / "harness.cjs"
    harness.write_text(logic)
    out = tmp_path / "run.cjs"
    out.write_text("""
const {ganttGeom, staleOf, expectationState, expectationText} = require("./harness.cjs");
const feed = require(process.argv[2]);
const g = ganttGeom(feed, 1120);
const by = {}; g.rows.forEach(r => by[r.id] = r);
console.log(JSON.stringify({
  n: g.rows.length, ticks: g.ticks.length,
  d1_settle_is_wall: by["D1-1-submission-landed"].settleX === by["D1-1-submission-landed"].wallX,
  placement_open_ended: by["D1-2-placement-winner"].openEnded && by["D1-2-placement-winner"].settleX === null,
  kickoff_no_wall: by["D2-3-nocard-account-live"].wallX === null,
  d5_settle_after_wall: by["D5-16-placement-winner"].settleX > by["D5-16-placement-winner"].wallX,
  fcc_soft: by["FCC-23-relational-db-cert"].soft === true,
  intake_state: expectationState(feed.subjects[0].expectation),
  intake_text: expectationText(feed.subjects[0].expectation),
  set_text: expectationText({prior_value: 0.4, posterior_value: 0.55, n_evidence: 3}),
  stale_fresh: staleOf(feed, Date.parse("2026-11-03T00:00:00Z")),
  stale_old: staleOf(feed, Date.parse("2026-12-01T00:00:00Z")),
}));
""")
    r = subprocess.run(["node", str(out), str(FIXTURE)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    res = json.loads(r.stdout.strip())
    assert res["n"] == 26 and res["ticks"] == 7
    assert res["d1_settle_is_wall"] and res["placement_open_ended"]
    assert res["kickoff_no_wall"] and res["d5_settle_after_wall"]
    assert res["fcc_soft"] and res["intake_state"] == "INTAKE"
    assert res["intake_text"] == "INTAKE \u2014 no estimate"
    assert "0.55" in res["set_text"]
    assert res["stale_fresh"] is False and res["stale_old"] is True


def test_render_hooks_present():
    html = _html()
    for hook in ['class="bar"', 'class="landingmark"', 'class="wallmark"',
                 'class="settlemark"', 'class="fctick"', 'id="hatch"',
                 'class="chip intake"', 'id="booktable"', 'id="positions"',
                 'id="settlements"', "moneyball.wagering-book/v2"]:
        assert hook in html, hook
