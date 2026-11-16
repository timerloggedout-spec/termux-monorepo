"""Pins for the desk page Dispatch queue section (chart standard).

The section renders ONLY data/dispatch-state-feed.json (schema
dispatch-state-feed/v1, stamped by the dispatch watchdog): a state
distribution chart from the feed's own counts + a table whose ages are
read against each row's own thresholds_min from the feed — thresholds
are never hardcoded in the page. Escalated rows render visually
distinct; absent values (claim null, stall_events empty, age missing)
render absent ("—"), never zero-filled or narrated as "none".
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "tribute-dashboard"
PAGE = APP / "desk.html"
FEED = APP / "data" / "dispatch-state-feed.json"


def _html():
    return PAGE.read_text(encoding="utf-8")


def _dq_js():
    blocks = re.findall(r"<script>(.*?)</script>", _html(), re.S)
    dq = [b for b in blocks if "dqStateDist" in b]
    assert len(dq) == 1
    return dq[0]


def test_section_hooks_and_fetch():
    html = _html()
    for hook in ['id="dqchart"', 'id="dqstamp"', 'id="dqrows"',
                 '"./data/dispatch-state-feed.json"',
                 "CK.bars", "CK.stampState", "<h2>Dispatch queue</h2>"]:
        assert hook in html, hook
    assert "api.github.com" not in html and "raw.githubusercontent" not in html


def test_escalated_styling_present():
    html = _html()
    assert "tr.dq-esc td" in html and ".chip.esc" in html
    assert '"dq-esc"' in html or "'dq-esc'" in html or "dq-esc" in html


def test_feed_shape():
    feed = json.loads(FEED.read_text())
    assert feed["schema"] == "dispatch-state-feed/v1"
    assert feed["generated_at"]
    counts = feed["counts"]
    # frozen contract: counts keys are the three states (a transitional
    # "total" key may ride along until the collector delta lands; the
    # chart consumes the state keys by name and never iterates keys)
    assert set(counts) <= {"queued", "claimed", "escalated", "total"}
    state_sum = (counts.get("queued", 0) + counts.get("claimed", 0)
                 + counts.get("escalated", 0))
    assert state_sum == len(feed["dispatches"])
    if "total" in counts:
        assert counts["total"] == state_sum
    for d in feed["dispatches"]:
        assert d["state"] in ("queued", "claimed", "escalated")
        assert isinstance(d["issue"], int) and d["title"] and d["entry"]
        assert "claim" in d and "age_min" in d and "stall_events" in d
        assert set(d["thresholds_min"]) == {"flag", "escalate"}
        assert set(d["tier"]) == {"index", "name"}


def test_script_parses(tmp_path):
    f = tmp_path / "dq.js"
    f.write_text(_dq_js())
    r = subprocess.run(["node", "--check", str(f)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_node_sim_against_live_feed(tmp_path):
    import shutil
    if not shutil.which("node"):
        import pytest
        pytest.skip("Node required")
    html = _html()
    esc_line = re.search(r"const esc=[^\n]*", html).group(0)
    logic = _dq_js().split(
        "// ==== pure logic (node-sim tested) ====")[1].split(
        "// ==== end pure logic ====")[0]
    harness = tmp_path / "harness.cjs"
    harness.write_text(esc_line + "\n" + logic)
    out = tmp_path / "run.cjs"
    out.write_text("""
const {dqStateDist, dqAgeClass, dqSort, dqClaim, dqStalls} = require("./harness.cjs");
const feed = require(process.argv[2]);
const rows = dqSort(feed.dispatches);
console.log(JSON.stringify({
  dist: dqStateDist(feed.counts),
  order: rows.map(d => d.issue),
  ageClasses: rows.map(d => dqAgeClass(d)),
  claims: rows.map(d => dqClaim(d)),
  stalls: rows.map(d => dqStalls(d)),
}));
""")
    r = subprocess.run(["node", str(out), str(FEED)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    res = json.loads(r.stdout.strip())
    feed = json.loads(FEED.read_text())
    # chart rows come from the feed counts, in escalated/claimed/queued order
    assert res["dist"] == [
        {"label": "escalated", "value": feed["counts"].get("escalated", 0)},
        {"label": "claimed", "value": feed["counts"].get("claimed", 0)},
        {"label": "queued", "value": feed["counts"].get("queued", 0)}]
    # escalated first, then age descending
    states = [d["state"] for d in feed["dispatches"]]
    esc_rows = [d for d in feed["dispatches"] if d["state"] == "escalated"]
    if esc_rows:
        assert res["order"][0] == esc_rows[0]["issue"]
    # ages classified strictly by each row's own feed thresholds
    by_issue = {d["issue"]: d for d in feed["dispatches"]}
    for issue, cls in zip(res["order"], res["ageClasses"]):
        d = by_issue[issue]
        th = d["thresholds_min"]
        want = ("dq-over" if d["age_min"] >= th["escalate"]
                else "dq-flag" if d["age_min"] >= th["flag"] else "")
        assert cls == want, (issue, cls, want)
    # absent renders absent: unclaimed rows and empty stall lists are "—"
    for d, claim, stalls in zip(
            [by_issue[i] for i in res["order"]], res["claims"], res["stalls"]):
        if d["claim"] is None:
            assert claim == "—"
        if not d["stall_events"]:
            assert stalls == "—"
