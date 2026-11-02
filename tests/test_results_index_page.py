"""Pins for the ALL-4 results index page.

The page renders ONLY data/results-index.json (schema
results-index/v1), the Telemetry lane's aggregation feed (source:
ops/telemetry/results-index.json, regenerated every telemetry-
ingest run). Render-verbatim discipline: source values as issued -
a 0 renders as 0, an absent capability renders as its stated none;
each system card points at its record of record with the feed's
own honesty note. The fixture pins the row-building behavior
(zero rendering, workflow rows, generic forward-compatible rows);
the live guards stay thin (schema, system set, record pointers).
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "tribute-dashboard"
PAGE = APP / "results-index.html"
FEED = ROOT / "ops" / "telemetry" / "results-index.json"
MIRROR = APP / "data" / "results-index.json"
FIXTURE = ROOT / "tests" / "fixtures" / "results-index.fixture.json"


def _feed():
    return json.loads(FEED.read_text())


def _html():
    return PAGE.read_text(encoding="utf-8")


def test_mirror_is_byte_identical():
    assert MIRROR.read_bytes() == FEED.read_bytes()


def test_page_consumes_only_the_feed():
    fetches = re.findall(r"fetch\(([^)]*)\)", _html())
    assert fetches == ['"./data/results-index.json"'], fetches


def test_feed_shape():
    feed = _feed()
    assert feed["schema"] == "results-index/v1"
    assert [s["id"] for s in feed["systems"]] == \
        ["ates", "3l0", "temporal", "hindsight"]
    for s in feed["systems"]:
        assert s["record_of_record"]["kind"]
        assert s["record_of_record"].get("path") or \
            s["record_of_record"].get("ref")
        assert s["record_of_record"]["note"]
        assert isinstance(s["headline"], dict) and s["headline"]


def test_true_states_present():
    by = {s["id"]: s for s in _feed()["systems"]}
    # zeros are data, present as keys with value 0 - never dropped
    assert by["3l0"]["headline"]["confirmed_non_null"] == 0
    assert by["hindsight"]["headline"]["retained_units"] == 0
    assert by["hindsight"]["headline"]["proof_ok"] == 0
    assert by["hindsight"]["headline"]["payloads"] == 388


def test_full_script_parses(tmp_path):
    script = _html().split("<script>")[1].split("</script>")[0]
    f = tmp_path / "page.js"
    f.write_text(script)
    r = subprocess.run(["node", "--check", str(f)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_node_sim_rows(tmp_path):
    html = _html()
    logic = html.split("// ==== pure logic (node-sim tested) ====")[1] \
        .split("// ==== end pure logic ====")[0]
    harness = tmp_path / "harness.cjs"
    harness.write_text(logic)
    out = tmp_path / "run.cjs"
    out.write_text("""
const {rowsFor, fmtVal, staleOf} = require("./harness.cjs");
const feed = require(process.argv[2]);
const by = {};
for (const s of feed.systems) by[s.id] = rowsFor(s);
const kv = rs => Object.fromEntries(rs.map(r => [r.k, r.v]));
console.log(JSON.stringify({
  ids: Object.keys(by),
  zero: fmtVal(0), none: fmtVal(null),
  l0: kv(by["3l0"]), hs: kv(by["hindsight"]),
  ates_rows: by["ates"].length,
  temporal_rows: by["temporal"].length,
  stale_fresh: staleOf(feed, Date.parse("2026-11-03T00:00:00Z")),
  stale_old: staleOf(feed, Date.parse("2026-12-01T00:00:00Z")),
}));
""")
    r = subprocess.run(["node", str(out), str(FIXTURE)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    res = json.loads(r.stdout.strip())
    assert res["ids"] == ["ates", "3l0", "temporal", "hindsight"]
    assert res["zero"] == "0" and res["none"] == "none"
    assert res["l0"]["confirmed non null"] == "0"
    assert res["l0"]["staged records"] == "599"
    assert res["hs"]["retained units"] == "0"
    assert res["hs"]["proof ok"] == "0"
    assert res["hs"]["payloads"] == "388"
    assert res["ates_rows"] >= 4 and res["temporal_rows"] >= 2
    assert res["stale_fresh"] is False and res["stale_old"] is True


def test_render_hooks_present():
    html = _html()
    for hook in ['id="systems"', 'id="meta"', "results-index/v1",
                 "Record of record"]:
        assert hook in html, hook
