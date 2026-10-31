"""Pins for the Contribution Desk page (traversal board + dispatch).

The page renders ONLY data/desk-feed.json (schema desk-feed/v1.2), seeded
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
FIXTURE = ROOT / "tests" / "fixtures" / "desk-feed.fixture.json"

PIPELINE = ["spec", "desk", "builder", "pr", "ci", "merge", "sync"]
STATES = {"done", "active", "pending", "gated", "na"}


def _html():
    return PAGE.read_text(encoding="utf-8")


def _pack():
    # Renderer pins run against the committed FIXTURE (the feed snapshot
    # the renderer was built against), NOT the live feed: desk refreshes
    # change live values/shape on their own cadence and must not red
    # renderer PRs (the refresh-chase class, Web Design ruling 2026-10-31).
    # The live feed keeps only the thin guard below + the mirror test.
    # Updating the fixture = a deliberate renderer-adoption change (viz).
    return json.loads(FIXTURE.read_text())


def _live_pack():
    return json.loads(PACK.read_text())


def test_mirror_is_byte_identical_to_source():
    assert PACK.read_bytes() == SOURCE.read_bytes()


def test_page_consumes_only_the_feed():
    html = _html()
    fetches = re.findall(r"fetch\(([^)]*)\)", html)
    assert fetches == ['"./data/desk-feed.json"'], fetches
    for el in ["meta", "model", "roles", "dispatchhow", "intake", "board", "provroll", "prov"]:
        assert f'id="{el}"' in html


def test_no_hardcoded_evidence_in_page():
    html = _html()
    for token in ["2606", "2615", "2616", "2619",
                  "cd381db0e824", "6ea0e52b0d95", "59c6c3b0427d"]:
        assert token not in html, token


def test_feed_schema_and_stage_states():
    pack = _pack()
    assert pack["schema"] == "desk-feed/v1.2"
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


def test_provider_usage_shape_and_d0():
    pack = _pack()
    by_entry = {t["entry"]: t for t in pack["traversals"]}
    assert by_entry["D0"]["evidence"]["pr"] == 1702
    allowed = {"provider", "scope", "via", "session_id", "state", "usage",
               "model", "moniker", "role", "context", "instance_key",
               "instance_refs", "phrases"}
    for t in pack["traversals"]:
        assert isinstance(t.get("provider_usage"), list), t["entry"]
        for p in t["provider_usage"]:
            assert set(p.keys()) <= allowed, (t["entry"], p)
            if p["usage"] is None:
                assert p["usage_note"], (t["entry"], p)
    providers = [p["provider"] for t in pack["traversals"] for p in t["provider_usage"]]
    assert "Jules" in providers
    assert sum(1 for x in providers if x and x.startswith("Muse — desk-spawned")) == 2
    assert "Muse (in-house, pre-correction)" in providers


def test_duplicate_instances_are_distinguished():
    # The two "Muse - desk-spawned subagents" rows share provider+model:
    # they are duplicates on the model axis alone and must stay distinct
    # configured instances (DoE identity, PR #2656) - entry-scoped context
    # plus an instance stamp each, with different system_prompt_refs.
    pack = _pack()
    dupes = [p for t in pack["traversals"] for p in t["provider_usage"]
             if p["provider"].startswith("Muse \u2014 desk-spawned")]
    assert len(dupes) == 2
    assert len({p["context"] for p in dupes}) == 2
    refs = [p["instance_refs"]["system_prompt_ref"] for p in dupes]
    assert len(set(refs)) == 2 and all(r.startswith("prompt:") for r in refs)
    for p in dupes:
        assert p["instance_refs"]["tools_ref"].startswith("tools:")
        assert "NOT ESTABLISHED" in p["instance_refs"]["note"]  # hashes never fabricated
        assert p["instance_key"] is None  # tuple incomplete => no key yet
    # Every stamped row (moniker+role present) carries an instance stamp;
    # the Jules pilot stamp carries its content hash in compact form.
    for t in pack["traversals"]:
        for p in t["provider_usage"]:
            if "moniker" in p:
                assert "instance_refs" in p, (t["entry"], p["provider"])
    jules = [p for t in pack["traversals"] for p in t["provider_usage"]
             if p["provider"] == "Jules"][0]
    assert "#" in jules["instance_refs"]["system_prompt_ref"]


def test_dispatch_intake_carries_instance_stamp_fields():
    pack = _pack()
    assert "Instance stamp" in pack["dispatch"]["how"]
    url = pack["dispatch"]["intake_url"]
    for field in ["system_prompt_ref", "tools_ref", "Model%40version"]:
        assert field in url, field


def test_live_feed_thin_guard():
    # Live feed: schema family + stage discipline only. NO provider_usage
    # key pins here - key-level shape is pinned on the fixture, so a desk
    # refresh that renames/adds stamp keys cannot red this suite.
    pack = _live_pack()
    assert pack["schema"].startswith("desk-feed/")
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
    scripts = re.findall(r"<script>(.*?)</script>", html, re.S | re.I)
    assert len(scripts) == 1
    f = tmp_path / "desk-script.js"
    f.write_text(scripts[0], encoding="utf-8")
    r = subprocess.run(["node", "--check", str(f)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_node_sim_logic(tmp_path):
    html = _html()
    script = re.findall(r"<script>(.*?)</script>", html, re.S | re.I)[0]
    esc_line = re.search(r"const esc=.*;", script).group(0)
    m = re.search(
        r"// ==== pure logic \(node-sim tested\) ====(.*?)// ==== end pure logic ====",
        script, re.S)
    assert m, "pure-logic markers missing"
    pack = _pack()
    travs_json = json.dumps(pack["traversals"])
    sim = esc_line + "\n" + m.group(1) + """
const t = %s;
const TRAVS = TRAVSJSON;
const row = boardRow(t);
if (!row.chips.includes("chip done")) throw new Error("chips");
if (stageClass("bogus") !== "pending") throw new Error("stageClass");
const roll = providerRollup(TRAVS);
if ((roll.counts["Jules"] || 0) < 1) throw new Error("rollup jules");
if ((roll.counts["Muse (in-house, pre-correction)"] || 0) !== 1) throw new Error("rollup in-house");
if (!roll.live.some(s => s.session_id === "17326020844735872479")) throw new Error("rollup live");
if (roll.coverage.total !== 5 || roll.coverage.waived !== 4 || roll.coverage.activity !== 1 || roll.coverage.covered !== 5 || roll.coverage.gap !== 0) throw new Error("coverage");
const syn = providerRollup([{provider_usage:[{provider:"X", usage:{value:null, status:"waived", note:"r"}},{provider:"Y", usage:{value:2, unit:"calls", status:"established", match:"exact"}}]}]);
if (syn.coverage.covered !== 2 || syn.coverage.waived !== 1 || syn.coverage.gap !== 0) throw new Error("coverage status");
if (!usageText({usage:{value:1, unit:"sessions", match:"activity-proxy"}}).includes("activity-proxy \u2014 not consumption")) throw new Error("proxy label");
if (!usageText({usage:{value:42, unit:"calls", match:"exact"}}).startsWith("usage: 42 calls")) throw new Error("exact text");
if (!phrasesText({phrases:{set:"deepseek", placement:"prefix", form:"leet", profile:"1337"}}).includes("deepseek")) throw new Error("phrases obj");
if (phrasesText({phrases:"NOT ESTABLISHED"}) !== "phrases: NOT ESTABLISHED") throw new Error("phrases str");
if (phrasesText({}) !== "") throw new Error("phrases absent");
console.log("ok");
""" % json.dumps(pack["traversals"][1])
    sim = sim.replace("TRAVSJSON", travs_json)
    f = tmp_path / "sim.cjs"
    f.write_text(sim, encoding="utf-8")
    r = subprocess.run(["node", str(f)], capture_output=True, text=True)
    assert r.returncode == 0 and "ok" in r.stdout, r.stderr
