"""Pins for the telemetry page feed-history trend (chart standard).

The trend renders the committed feed-history series
(data/telemetry-feed-series.jsonl, built by
scripts/dashboards/telemetry_feed_series.py): one row per
committed snapshot of the telemetry-viz feed, golden counters
verbatim. The backfill rows are pinned against the snapshots of
record (the feed file's git history: Slice 1 generated
2026-10-30T06:22:26Z, Slice 2 = the current feed,
2026-10-30T07:47:32Z) — including the flat truth: both snapshots
carry identical counters.
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "tribute-dashboard"
PAGE = APP / "telemetry.html"
FEED = APP / "data" / "telemetry-feed.json"
SERIES = APP / "data" / "telemetry-feed-series.jsonl"
GEN = ROOT / "scripts" / "dashboards" / "telemetry_feed_series.py"


def _html():
    return PAGE.read_text(encoding="utf-8")


def _rows():
    return [json.loads(l) for l in
            SERIES.read_text().splitlines() if l.strip()]


def test_chart_hooks_present():
    html = _html()
    for hook in ['src="./chartkit.js"', 'id="historychart"',
                 'id="historystamp"', "CK.line", "CK.stampState",
                 "./data/telemetry-feed-series.jsonl"]:
        assert hook in html, hook


def test_series_matches_snapshots_of_record():
    rows = _rows()
    stamps = [r["generated_at"] for r in rows]
    assert stamps == sorted(stamps) and len(set(stamps)) == len(stamps)
    # backfill anchors (the feed's committed history)
    assert rows[0]["generated_at"] == "2026-10-30T06:22:26Z"
    assert rows[0]["receipts_total"] == 3962
    # the last series row is the current feed, verbatim
    feed = json.loads(FEED.read_text())
    golden = feed["data"]["golden"]
    assert rows[-1]["generated_at"] == feed["generated_at"]
    for f in ("receipts_total", "actioned", "skipped",
              "quota_readings_total", "workflow_runs_observed",
              "actions_failure_rate"):
        assert rows[-1][f] == golden.get(f), f


def test_generator_appends_only_new_stamps(tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("tfs", GEN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    series = tmp_path / "s.jsonl"
    series.write_text(SERIES.read_text())
    rows = mod.build(FEED, series)
    assert len(rows) == len(_rows())  # current stamp already in
    feed2 = json.loads(FEED.read_text())
    feed2["generated_at"] = "2026-11-03T00:00:00Z"
    f2 = tmp_path / "feed2.json"
    f2.write_text(json.dumps(feed2))
    rows2 = mod.build(f2, series)
    assert len(rows2) == len(rows) + 1
    assert rows2[-1]["generated_at"] == "2026-11-03T00:00:00Z"


def test_scripts_parse(tmp_path):
    blocks = re.findall(r"<script>(.*?)</script>", _html(), re.S)
    assert blocks
    for b in blocks:
        f = tmp_path / "block.js"
        f.write_text(b)
        r = subprocess.run(["node", "--check", str(f)],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr


def test_node_sim_trend(tmp_path):
    blocks = re.findall(r"<script>(.*?)</script>", _html(), re.S)
    chart = [b for b in blocks if "parseFeedSeries" in b]
    assert len(chart) == 1
    logic = chart[0].split(
        "// ==== pure logic (node-sim tested) ====")[1].split(
        "// ==== end pure logic ====")[0]
    harness = tmp_path / "harness.cjs"
    harness.write_text(logic)
    out = tmp_path / "run.cjs"
    out.write_text("""
const {parseFeedSeries, seriesPoints} = require("./harness.cjs");
const fs = require("fs");
const rows = parseFeedSeries(fs.readFileSync(process.argv[2], "utf8"));
console.log(JSON.stringify({
  n: rows.length,
  receipts: seriesPoints(rows, "receipts_total").map(p => p.v),
}));
""")
    r = subprocess.run(["node", str(out), str(SERIES)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    res = json.loads(r.stdout.strip())
    assert res["n"] == len(_rows())
    assert res["receipts"] == [r["receipts_total"] for r in _rows()]
