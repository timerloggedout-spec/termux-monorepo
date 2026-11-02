"""Pins for the wagering-book Gantt page.

The page renders ONLY data/wagering-book.json (schema
moneyball.wagering-book/v1): the join of the challenges book
(MoneyBall) with its calendar anchors (deadline-reminders/v1,
Tracking), built by scripts/moneyball/wagering_book_feed.py.
Integrity rules pinned here: 23 subjects; bars open -> knowable;
rule knowables stay undated (open-ended, never an invented date);
wall = FINAL + 30 min wherever a FINAL anchor exists; AMD-17/18
carry no anchors; the book's expectation_record never reaches the
feed or the page; forecast is an OUTPUT class - a scoring tick,
never a row.
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
BOOK = ROOT / "ops" / "agentic-gambling" / "book" / "challenges-book.json"


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
    assert feed["schema"] == "moneyball.wagering-book/v1"
    subs = feed["subjects"]
    assert len(subs) == feed["book"]["subjects"] == 23
    fams = {}
    for s in subs:
        fams[s["family"]] = fams.get(s["family"], 0) + 1
    assert fams == {"D1": 2, "D2": 3, "D3": 4, "D4": 4, "D5": 3,
                    "AMD": 6, "FCC": 1}
    assert all("forecast" not in s["id"] for s in subs)
    assert "OUTPUT" in feed["forecast_layer"]
    assert "expectation" not in FEED.read_text()


def test_feed_matches_book_subjects():
    book = json.loads(BOOK.read_text())
    feed = _feed()
    assert [s["id"] for s in feed["subjects"]] == \
        [s["id"] for s in book["subjects"]]
    by = {s["id"]: s for s in feed["subjects"]}
    for bs in book["subjects"]:
        assert by[bs["id"]]["settles_by"] == bs["settle"]["source"]


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
    html = _html().lower()
    assert "winprob" not in html and "expectation_record" not in html


def test_full_script_parses(tmp_path):
    script = _html().split("<script>")[1].split("</script>")[0]
    f = tmp_path / "page.js"
    f.write_text(script)
    r = subprocess.run(["node", "--check", str(f)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_node_sim_gantt(tmp_path):
    html = _html()
    logic = html.split("// ==== pure logic (node-sim tested) ====")[1] \
        .split("// ==== end pure logic ====")[0]
    harness = tmp_path / "harness.cjs"
    harness.write_text(logic)
    out = tmp_path / "run.cjs"
    out.write_text("""
const {ganttGeom, staleOf} = require("./harness.cjs");
const feed = require(process.argv[2]);
const g = ganttGeom(feed, 1120);
const by = {}; g.rows.forEach(r => by[r.id] = r);
console.log(JSON.stringify({
  n: g.rows.length, ticks: g.ticks.length,
  d1_order: by["D1-1-submission-landed"].openX < by["D1-1-submission-landed"].landingX
    && by["D1-1-submission-landed"].landingX < by["D1-1-submission-landed"].wallX,
  d1_settle_is_wall: by["D1-1-submission-landed"].settleX === by["D1-1-submission-landed"].wallX,
  placement_open_ended: by["D1-2-placement-winner"].openEnded && by["D1-2-placement-winner"].settleX === null,
  kickoff_no_wall: by["D2-3-nocard-account-live"].wallX === null,
  d5_settle_after_wall: by["D5-16-placement-winner"].settleX > by["D5-16-placement-winner"].wallX,
  fcc_soft: by["FCC-23-relational-db-cert"].soft === true,
  amd17_no_landing: by["AMD-17-gpu100-claim"].landingX === null,
  stale_fresh: staleOf(feed, Date.parse("2026-11-03T00:00:00Z")),
  stale_old: staleOf(feed, Date.parse("2026-12-01T00:00:00Z")),
}));
""")
    r = subprocess.run(["node", str(out), str(FIXTURE)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    res = json.loads(r.stdout.strip())
    assert res["n"] == 23 and res["ticks"] == 7
    assert res["d1_order"] and res["d1_settle_is_wall"]
    assert res["placement_open_ended"] and res["kickoff_no_wall"]
    assert res["d5_settle_after_wall"] and res["fcc_soft"]
    assert res["amd17_no_landing"]
    assert res["stale_fresh"] is False and res["stale_old"] is True


def test_render_hooks_present():
    html = _html()
    for hook in ['class="bar"', 'class="landingmark"', 'class="wallmark"',
                 'class="settlemark"', 'class="fctick"', 'id="hatch"',
                 "moneyball.wagering-book/v1"]:
        assert hook in html, hook
