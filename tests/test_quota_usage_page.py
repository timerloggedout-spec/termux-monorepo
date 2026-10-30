"""Pins for the quota-usage page (burn-down + replenishment stamps).

The page renders ONLY data/quota-usage.json (schema quota-usage/v1),
the pack built from the quota-specialist data pack (owner order
2026-10-29). Integrity rules pinned here: no observation values are
hardcoded in the page; every series-1 point and series-2 snapshot
carries provenance; the composed 155-row snapshot stays flagged
landed=False until the convergence lane confirms landing; g4f has NO
replenishment stamp (established=False, cadence=None) and must never
gain one silently; series-3 daily deltas must equal the increments of
the in-repo reconstructed corpus they are derived from.
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "help-wanted-dashboard"
PAGE = APP / "quota-usage.html"
PACK = APP / "data" / "quota-usage.json"
SOURCE = ROOT / "ops" / "quota" / "quota-usage.json"
CORPUS = ROOT / "docs" / "ops" / "generated"

STATES = {"ok", "watch", "exhausted", "cap_tripped", "unknown"}


def _html():
    return PAGE.read_text(encoding="utf-8")


def _pack():
    return json.loads(PACK.read_text())


def test_mirror_is_byte_identical_to_source():
    # Web Design consumes the same file in quota.html — one series, no fork:
    # the dashboard copy is a byte-identical mirror of ops/quota/quota-usage.json.
    assert PACK.read_bytes() == SOURCE.read_bytes()


def test_page_consumes_only_the_pack():
    html = _html()
    fetches = re.findall(r"fetch\(([^)]*)\)", html)
    assert fetches == ['"./data/quota-usage.json"'], fetches
    for el in ["meta", "burndown", "states", "actions", "stamps", "origins"]:
        assert f'id="{el}"' in html


def test_no_hardcoded_observations():
    html = _html()
    # the observed remaining values from the pack must live in the pack only
    assert "2950" not in html and "2945" not in html
    assert not re.search(r"remaining\s*[:=]\s*\d", html)


def test_series1_points_carry_provenance_and_walls():
    s1 = _pack()["series1_api_core"]
    pts = s1["points"]
    assert pts == sorted(pts, key=lambda p: p["at"])
    assert all(p["provenance"] for p in pts)
    walls = [p for p in pts if p["kind"] == "wall"]
    assert len(walls) == 5 and all(p["remaining"] == 0 for p in walls)
    assert s1["limit"] == 5000 and s1["next_reset_observed"]


def test_buckets_kept_separate_and_storm_fix_recorded():
    pack = _pack()
    buckets = {b["name"]: b for b in pack["buckets"]}
    # cadence graph note: buckets are never merged into one burn line
    assert buckets["github.api PAT core (user token)"]["limit"] == 5000
    assert buckets["GitHub App installation token"]["limit"] == 1000
    assert buckets["GitHub GraphQL (user token)"]["limit"] == 5000
    spike = pack["series3_actions"]["spike"]
    assert "2341" in spike["outcome"] and "97938a583f50" in spike["outcome"]
    wall_anno = [a for a in pack["annotations"] if a["id"] == "origin-pat-wall"][0]
    assert "NOT ESTABLISHED" in wall_anno["text"]


def test_series2_snapshots_provenance_and_landing_flags():
    s2 = _pack()["series2_snapshots"]
    snaps = s2["snapshots"]
    assert [sn["landed"] for sn in snaps] == [True, True, False]
    assert [sn["rows"] for sn in snaps] == [3, 8, 155]
    for sn in snaps:
        assert sn["provenance"]
        for svc, state in sn["states"].items():
            assert svc in s2["services"] and state in STATES
    # snapshot 3 is the recovery: github token exhausted -> watch
    assert snaps[1]["states"]["github.api.github_token"] == "exhausted"
    assert snaps[2]["states"]["github.api.github_token"] == "watch"


def test_g4f_has_no_stamp():
    stamps = _pack()["stamps"]
    g4f = [s for s in stamps if s["pool"].startswith("g4f")]
    assert len(g4f) == 1
    assert g4f[0]["established"] is False and g4f[0]["cadence"] is None
    others = [s for s in stamps if not s["pool"].startswith("g4f")]
    assert others and all(s["established"] and s["cadence"] for s in others)


def test_series3_deltas_match_corpus():
    pack_days = {d["date"]: d for d in _pack()["series3_actions"]["days"]}
    files = sorted(CORPUS.glob("actions-performance-reconstructed-2026-10-*.json"))
    prev = None
    checked = 0
    for f in files:
        cur = json.loads(f.read_text())
        date = f.name[-15:-5]
        if prev is not None:
            assert date in pack_days, date
            assert pack_days[date]["runs_delta"] == cur["run_count"] - prev["run_count"]
            assert pack_days[date]["jobs_delta"] == cur["total_jobs"] - prev["total_jobs"]
            checked += 1
        prev = cur
    assert checked == len(pack_days) == 28
    spike = _pack()["series3_actions"]["spike"]
    assert spike["runs"] == 143 and spike["workflow"] == "delphi-gate"


def test_node_sim_logic(tmp_path):
    html = _html()
    logic = html.split("// ==== pure logic (node-sim tested) ====")[1].split("// ==== end pure logic ====")[0]
    harness = tmp_path / "harness.cjs"
    harness.write_text(logic)
    out = tmp_path / "run.cjs"
    out.write_text("""
const {burnGeom, stepPath, stateClass, barGeom, stampText} = require("./harness.cjs");
const pts = [
  {at: "2026-10-28T23:41:00Z", remaining: 0, kind: "wall"},
  {at: "2026-10-29T00:37:00Z", remaining: 2500, kind: "observed"},
  {at: "2026-10-30T01:36:00Z", remaining: 0, kind: "wall"},
];
const g = burnGeom(pts, 5000, 920, 300, 44);
const bars = barGeom([{date: "a", runs_delta: 40}, {date: "b", runs_delta: 0}, {date: "c", runs_delta: 20}], 920, 260, 40);
const res = {
  wall_y: g.pts[0].y, half_y: g.pts[1].y, xs_sorted: g.pts[0].x < g.pts[1].x && g.pts[1].x < g.pts[2].x,
  path_head: stepPath(g.pts).slice(0, 1),
  state_ok: stateClass("cap_tripped"), state_none: stateClass(null),
  bar_max_h: Math.max(...bars.map(b => b.h)), bar_zero_h: bars[1].h,
  stamp_ok: stampText({established: true, cadence: "daily"}),
  stamp_none: stampText({established: false, cadence: null}),
};
console.log(JSON.stringify(res));
""")
    r = subprocess.run(["node", str(out)], cwd=tmp_path, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    res = json.loads(r.stdout.strip())
    # remaining 0 sits on the axis (pad + inner height = 44 + 212), half bucket mid-way
    assert res["wall_y"] == 256 and abs(res["half_y"] - 150) < 1
    assert res["xs_sorted"] and res["path_head"] == "M"
    assert res["state_ok"] == "cap_tripped" and res["state_none"] == "none"
    assert res["bar_max_h"] == 180 and res["bar_zero_h"] == 0
    assert res["stamp_ok"] == "↻ DAILY" and res["stamp_none"].startswith("NO STAMP")
