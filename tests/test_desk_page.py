"""Pins for the Contribution Desk page (traversal board + dispatch).

The page renders ONLY data/desk-feed.json (schema desk-feed/v1), seeded
by the viz lane from firsthand audits of the live record (2026-10-30)
and refreshed by the Contribution Desk lane as traversals move.
Integrity rules pinned here: the dashboard copy is a byte-identical
mirror of ops/challenge/desk-feed.json; no PR numbers or merge SHAs are
hardcoded in the page (evidence lives in the feed only); every
traversal carries all seven pipeline stages with states from the fixed
enum; a stage may read "done" only with evidence behind it; the page
mutates nothing (dispatch is a link to the GitHub intake issue).
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "help-wanted-dashboard"
PAGE = APP / "desk.html"
PACK = APP / "data" / "desk-feed.json"
SOURCE = ROOT / "ops" / "challenge" / "desk-feed.json"

PIPELINE = ["spec", "desk", "builder", "pr", "ci", "merge", "sync"]
STATES = {"done", "active", "pending", "gated", "na"}


def _html():
    return PAGE.read_text(encoding="utf-8")


def _pack():
    return json.loads(PACK.read_text())


def test_mirror_is_byte_identical_to_source():
    assert PACK.read_bytes() == SOURCE.read_bytes()


def test_page_consumes_only_the_feed():
    html = _html()
    fetches = re.findall(r"fetch\(([^)]*)\)", html)
    assert fetches == ['"./data/desk-feed.json"'], fetches
    for el in ["meta", "model", "roles", "dispatchhow", "intake", "board", "prov"]:
        assert f'id="{el}"' in html


def test_no_hardcoded_evidence_in_page():
    html = _html()
    for token in ["2606", "2615", "2616", "2619",
                  "cd381db0e824", "6ea0e52b0d95", "59c6c3b0427d"]:
        assert token not in html, token


def test_feed_schema_and_stage_states():
    pack = _pack()
    assert pack["schema"] == "desk-feed/v1"
    assert pack["desk"]["pipeline"] == PIPELINE
    assert pack["traversals"], "board must not be empty"
    for t in pack["traversals"]:
        assert set(t["stages"].keys()) == set(PIPELINE), t["entry"]
        for stage, state in t["stages"].items():
            assert state in STATES, (t["entry"], stage, state)
        if t["stages"]["pr"] == "done":
            assert "pr" in t["evidence"] or "prs" in t["evidence"], t["entry"]
        if t["stages"]["merge"] == "done":
            assert "merge_sha" in t["evidence"] or "merge_shas" in t["evidence"], t["entry"]


def test_dispatch_is_a_link_not_a_mutation():
    pack = _pack()
    assert pack["dispatch"]["intake_url"].startswith(
        "https://github.com/timerloggedout-spec/termux-monorepo/issues/new?")
    html = _html()
    assert 'method="post"' not in html.lower()
    assert "XMLHttpRequest" not in html


def test_full_script_parses(tmp_path):
    html = _html()
    scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
    assert len(scripts) == 1
    f = tmp_path / "desk-script.js"
    f.write_text(scripts[0], encoding="utf-8")
    r = subprocess.run(["node", "--check", str(f)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_node_sim_logic(tmp_path):
    html = _html()
    script = re.findall(r"<script>(.*?)</script>", html, re.S)[0]
    esc_line = re.search(r"const esc=.*;", script).group(0)
    m = re.search(
        r"// ==== pure logic \(node-sim tested\) ====(.*?)// ==== end pure logic ====",
        script, re.S)
    assert m, "pure-logic markers missing"
    pack = _pack()
    sim = esc_line + "\n" + m.group(1) + """
const t = %s;
const row = boardRow(t);
if (!row.chips.includes("chip done")) throw new Error("chips");
if (stageClass("bogus") !== "pending") throw new Error("stageClass");
console.log("ok");
""" % json.dumps(pack["traversals"][1])
    f = tmp_path / "sim.cjs"
    f.write_text(sim, encoding="utf-8")
    r = subprocess.run(["node", str(f)], capture_output=True, text=True)
    assert r.returncode == 0 and "ok" in r.stdout, r.stderr
