"""Pins for the quota-usage page (burn-down + replenishment stamps).

The page renders ONLY data/quota-usage.json (schema quota-usage/v1),
the pack built from the quota-specialist data pack (owner order
2026-10-29). Integrity rules pinned here: no observation values are
hardcoded in the page; every series-1 point and series-2 snapshot
carries provenance; the 155-row snapshot's landed flag flipped to True
only when convergence PR #2362 landed and viz verified the pair blob
on master; g4f has NO
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
    # burn shape is a sustained ramp, not a spike (convergence correction):
    # the new window's first reads drain 4999 -> 4645 -> 3230
    by_at = {p["at"]: p["remaining"] for p in pts}
    assert by_at["2026-10-30T01:43:00Z"] == 4999
    assert by_at["2026-10-30T01:45:00Z"] == 4645
    assert by_at["2026-10-30T01:54:00Z"] == 3230
    assert "30–40 min ramp" in s1["note"]


def test_buckets_kept_separate_and_storm_fix_recorded():
    pack = _pack()
    buckets = {b["name"]: b for b in pack["buckets"]}
    # cadence graph note: buckets are never merged into one burn line
    assert buckets["github.api.user_token (PAT user bucket)"]["limit"] == 5000
    assert buckets["github.api.github_token (installation, per-repo)"]["limit"] == 1000
    assert buckets["GitHub GraphQL (user token)"]["limit"] == 5000
    spike = pack["series3_actions"]["spike"]
    assert "2341" in spike["outcome"] and "97938a583f50" in spike["outcome"]
    wall_anno = [a for a in pack["annotations"] if a["id"] == "origin-pat-wall"][0]
    assert "NOT ESTABLISHED" in wall_anno["text"]


def test_flow_line_model():
    # Owner principle (via cadence lane): the target line is the
    # replenishment flow line, phased to reset epochs — not a ceiling.
    s1 = _pack()["series1_api_core"]
    m = s1["model"]
    assert m["window_ms"] == 3600000 and "NOT a survival ceiling" in m["principle"]
    assert set(m["faults"]) == {"below_line", "above_line"}
    anchor = 1793324529000  # 2026-10-30T01:42:09Z in ms
    assert m["anchor_reset"] == "2026-10-30T01:42:09Z"
    for w in m["worked"]:
        t = __import__("datetime").datetime.fromisoformat(w["at"].replace("Z", "+00:00"))
        ms = int(t.timestamp() * 1000)
        ideal = 5000 * (((anchor - ms) % 3600000) / 3600000)
        assert abs(ideal - w["ideal_remaining"]) <= 3, (w, ideal)


def test_node_sim_flow_line(tmp_path):
    html = _html()
    logic = html.split("// ==== pure logic (node-sim tested) ====")[1].split("// ==== end pure logic ====")[0]
    harness = tmp_path / "harness.cjs"
    harness.write_text(logic)
    out = tmp_path / "run.cjs"
    out.write_text("""
const {idealRemaining, parseT} = require("./harness.cjs");
const A = parseT("2026-10-30T01:42:09Z"), W = 3600000;
const res = {
  at_reset: idealRemaining(A, 5000, A, W),
  half_window: idealRemaining(A - 1800000, 5000, A, W),
  just_after_reset: Math.round(idealRemaining(A + 60000, 5000, A, W)),
  prev_window_same_phase: idealRemaining(A - W - 1800000, 5000, A, W),
};
console.log(JSON.stringify(res));
""")
    r = subprocess.run(["node", str(out)], cwd=tmp_path, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    res = json.loads(r.stdout.strip())
    assert res["at_reset"] == 0 and res["half_window"] == 2500
    # one minute into a fresh window the ideal is nearly the full bucket
    assert res["just_after_reset"] == 4917
    assert res["prev_window_same_phase"] == 2500


def test_gearbox_concept_block():
    gb = _pack()["gearbox"]
    assert gb["doc"] == "docs/ops/QUOTA-GEARBOX-CONCEPT.md"
    assert "INTERNAL" in gb["admin_designation"]
    assert [g["focus"] for g in gb["gears"]] == [
        "winning", "repo-development", "research", "boinc-donations"]
    # the mock is flagged as a mock, and the honesty flags are explicit
    assert gb["mock"]["flag"].startswith("MOCK")
    assert any("NOT ESTABLISHED" in h for h in gb["honesty"])
    assert gb["shift_log_type"]["shape"]["cites"] == "#1884"
    # no fake shift events leak into the real annotation stream
    assert all(a.get("type") != "shift" for a in _pack()["annotations"])
    # owner refinement: sliders + presets, checkbox subsets, extended audit
    ui = gb["admin_ui"]
    assert [p["name"] for p in ui["sliders"]["presets"]] == [
        "Winning 100", "leftover-only", "excluded / reserve-100", "equal-split"]
    assert {"issue", "rfp"} <= set(ui["subset_selection"]["tags"])
    shape = gb["shift_log_type"]["shape"]
    assert "subset_filter" in shape and "input_source" in shape
    assert ui["guardrail_ruling"]["over_100"].startswith("BLOCK")


def test_series2_snapshots_provenance_and_landing_flags():
    s2 = _pack()["series2_snapshots"]
    snaps = s2["snapshots"]
    assert [sn["landed"] for sn in snaps] == [True, True, True]
    assert [sn["rows"] for sn in snaps] == [3, 8, 155]
    for sn in snaps:
        assert sn["provenance"]
        for svc, state in sn["states"].items():
            assert svc in s2["services"] and state in STATES
    # snapshot 3 is the recovery: github token exhausted -> watch
    assert snaps[1]["states"]["github.api.github_token"] == "exhausted"
    assert snaps[2]["states"]["github.api.github_token"] == "watch"
    # landed 155-row truth (PR #2362, pair blob 5d5238c9): minutes unknown
    assert snaps[2]["states"]["github.actions.minutes"] == "unknown"
    assert "2362" in snaps[2]["provenance"]


def test_g4f_has_no_stamp():
    stamps = _pack()["stamps"]
    g4f = [s for s in stamps if s["pool"].startswith("g4f (")]
    assert len(g4f) == 1
    assert g4f[0]["established"] is False and g4f[0]["cadence"] is None
    # the only other unstamped group: registry records whose window is unknown
    unstamped = [s for s in stamps if not s["established"]]
    assert {s["pool"] for s in unstamped} == {"g4f (43 records)", "48 of 155 registry records"}
    others = [s for s in stamps if s["established"]]
    assert others and all(s["cadence"] for s in others)


def test_stamp_cadence_precision():
    # convergence-lane corrections vs the registry, pinned so they cannot regress
    stamps = {s["pool"]: s for s in _pack()["stamps"]}
    assert "UTC midnight" in stamps["openrouter.free_models"]["detail"]
    assert "NOT pinned" in stamps["daily free tiers (groq, cerebras, airforce, g4f.established)"]["detail"]
    assert stamps["render.pipeline_minutes"]["cadence"] == "monthly — calendar"
    assert stamps["neon.compute (CU-hours)"]["cadence"] == "monthly — billing"
    assert "x-ratelimit-reset" in stamps["github.api (PAT core)"]["detail"]
    assert "2032" in stamps["g4f.elevenlabs (10,000 credits)"]["detail"]


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


def test_full_script_parses(tmp_path):
    # Regression pin: PR #2360 shipped a missing ')' in renderBurn that
    # made the whole <script> unparseable (page stuck on "Loading pack")
    # while every pure-logic test stayed green. Parse the full script.
    script = _html().split("<script>")[1].split("</script>")[0]
    f = tmp_path / "page.js"
    f.write_text(script)
    r = subprocess.run(["node", "--check", str(f)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


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


def test_quota_page_links_usage_graphs_and_sitemap():
    # web-design chrome wiring: the usage page is a quota sub-page, so the
    # parent panel links it and the sitemap lists it; it is not a shell page.
    quota = (APP / "quota.html").read_text()
    assert 'href="./quota-usage.html"' in quota
    sitemap = (APP / "sitemap.xml").read_text()
    assert "https://timerloggedout-spec.github.io/help-wanted/quota-usage.html" in sitemap
