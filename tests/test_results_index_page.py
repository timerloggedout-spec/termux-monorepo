"""Pins for the ALL-4 results index page.

The page renders ONLY data/results-index-feed.json (schema
results-index-feed/v1), the dashboard twin of the Telemetry
lane's aggregation (canonical ops/telemetry/results-index.json,
results-index/v1 - one builder, one value source, two
presentations). Render-verbatim: row states as issued (0 renders
as 0; an absent capability renders as its stated none); every row
points at its record of record; section notes ride verbatim.
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "tribute-dashboard"
PAGE = APP / "results-index.html"
TWIN = APP / "data" / "results-index-feed.json"
CANON = ROOT / "ops" / "telemetry" / "results-index.json"
FIXTURE = ROOT / "tests" / "fixtures" / "results-index.fixture.json"


def _twin():
    return json.loads(TWIN.read_text())


def _html():
    return PAGE.read_text(encoding="utf-8")


def test_page_consumes_only_the_twin():
    fetches = re.findall(r"fetch\(([^)]*)\)", _html())
    assert fetches == ['"./data/results-index-feed.json"'], fetches


def test_twin_shape_and_pointers():
    twin = _twin()
    assert twin["schema"] == "results-index-feed/v1"
    assert [s["id"] for s in twin["sections"]] == \
        ["ates", "3l0", "temporal", "hindsight"]
    for s in twin["sections"]:
        assert s["generated_at"] and s["note"] and s["rows"]
        for r in s["rows"]:
            assert r["label"] and r["record_of_record"]
            assert "state" in r  # 0 and "none" are states, kept


def test_twin_matches_canonical_values():
    twin = _twin()
    canon = {s["id"]: s for s in json.loads(CANON.read_text())["systems"]}
    rows = {s["id"]: {r["label"]: r["state"] for r in s["rows"]}
            for s in twin["sections"]}
    assert rows["3l0"]["staged intake records"] == \
        canon["3l0"]["headline"]["staged_records"]
    assert rows["3l0"]["confirmed (weights-eligible)"] == \
        canon["3l0"]["headline"]["confirmed_non_null"] == 0
    assert rows["hindsight"]["retained population"] == \
        canon["hindsight"]["headline"]["retained_units"] == 0
    assert rows["temporal"]["persistent instance"] == "none"
    assert rows["temporal"]["engagement runs"] == \
        canon["temporal"]["headline"]["engagement"]["total_count"]
    wf = {w["file"].split("/")[-1]: w["total_runs"]
          for w in canon["ates"]["headline"]["workflows"]}
    assert rows["ates"]["receipt runs"] == \
        wf["ates-phase-b-run-receipt.yml"]
    assert rows["ates"]["benchmark runs"] == \
        wf["ates-orchestrator-benchmark.yml"]


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
const {fmtState, staleOf} = require("./harness.cjs");
const feed = require(process.argv[2]);
const by = {};
for (const s of feed.sections) {
  by[s.id] = Object.fromEntries(s.rows.map(r => [r.label, fmtState(r.state)]));
}
console.log(JSON.stringify({
  ids: Object.keys(by), by,
  stale_fresh: staleOf(feed.generated_at, Date.parse("2026-11-03T00:00:00Z")),
  stale_old: staleOf(feed.generated_at, Date.parse("2026-12-01T00:00:00Z")),
}));
""")
    r = subprocess.run(["node", str(out), str(FIXTURE)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    res = json.loads(r.stdout.strip())
    assert res["ids"] == ["ates", "3l0", "temporal", "hindsight"]
    assert res["by"]["3l0"]["confirmed (weights-eligible)"] == "0"
    assert res["by"]["3l0"]["routed-dispatch stamp corpus"] == "614"
    assert res["by"]["temporal"]["persistent instance"] == "none"
    assert res["by"]["hindsight"]["retained population"] == "0"
    assert res["by"]["ates"]["receipt runs"] == "9"
    assert res["stale_fresh"] is False and res["stale_old"] is True


def test_render_hooks_present():
    html = _html()
    for hook in ['id="systems"', 'id="meta"', "results-index-feed/v1",
                 "Record of record"]:
        assert hook in html, hook
