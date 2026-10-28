"""Linguist panel: feed-only consumption, surface markers, logic sim.

Re-pinned to the landed substrate feed (linguist-panel-feed/v1, PRs
#1864/#1868): FLAT wrapper, char tables on families as [{from,to}],
direction_panel logic field, layers = family.kind. The node sim runs
against a fixture in the REAL feed shape (small synthetic values, only
in this test) plus structural assertions against the landed feed file.
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "help-wanted-dashboard"
PAGE = APP / "linguist.html"
FEED = APP / "data" / "linguist-panel-feed.json"


def _html():
    return PAGE.read_text(encoding="utf-8")


def _script():
    return re.search(r"<script>(.*)</script>", _html(), re.S).group(1)


def test_page_consumes_only_linguist_feed():
    fetches = re.findall(r"""fetch\(\s*["']([^"']+)["']""", _html())
    assert fetches == ["./data/linguist-panel-feed.json"]
    assert "api.github.com" not in _html()


def test_surface_markers():
    html = _html()
    for marker in (
        "Side-by-side columns", "In-text (highlighted + threaded)",
        "Admin — all mappings", "in text", "thread",
        "feed-absent", "round-trip", "count-only", "not enumerated",
        "data-layer", "data-fam",
    ):
        assert marker in html, marker


def test_landed_feed_shape_matches_renderer_assumptions():
    feed = json.loads(FEED.read_text(encoding="utf-8"))
    assert feed["schema"] == "linguist-panel-feed/v1"
    assert "data" not in feed  # flat wrapper (G2)
    assert len(feed["families"]) == 15 and len(feed["entries"]) == 288
    kinds = {f["kind"] for f in feed["families"]}
    assert kinds <= {"cipher", "compression", "leet", "notation", "other"}
    tables = {f["id"]: f["table"] for f in feed["families"] if f.get("table")}
    assert set(tables) == {"phase-codec-leet-chars", "grimoire-char-variants"}
    assert all(isinstance(r, dict) and "from" in r and "to" in r
               for t in tables.values() for r in t)
    arch = [f for f in feed["families"] if f["entries_included"] is False]
    assert len(arch) == 1 and arch[0]["entry_count"] == 7287
    assert {e["direction_panel"] for e in feed["entries"]} <= {"both", "forward", "reverse", None}
    notation = {f["id"] for f in feed["families"] if f["kind"] == "notation"}
    assert all(e["direction_panel"] is None for e in feed["entries"]
               if e["family_id"] in notation)


FIXTURE = {
    "schema": "linguist-panel-feed/v1",
    "families": [
        {"id": "leet-fam", "label": "Leet fam", "kind": "leet", "granularity": "char",
         "direction": "encode-only", "direction_panel": "forward", "entries_included": True,
         "table": [{"from": "a", "to": "4"}, {"from": "e", "to": ["3", "€"]}]},
        {"id": "note-fam", "label": "Note fam", "kind": "notation", "granularity": "phrase",
         "direction": "definitional", "direction_panel": None, "entries_included": True},
        {"id": "arch", "label": "Arch", "kind": "other", "entries_included": False, "entry_count": 7287},
    ],
    "entries": [
        {"id": "n1", "family_id": "note-fam", "source": "ab", "variants": ["AB!"],
         "direction": "definitional", "direction_panel": None, "match": "ab",
         "round_trip_verified": None, "provenance": {"source_path": "x.py", "detail": "line 1"}},
    ],
    "sample_texts": [], "honesty_rules": [], "gaps": [],
}


def test_logic_sim_node():
    node = shutil.which("node")
    if not node:
        return
    harness = """
const fs = require("fs");
const src = fs.readFileSync(process.argv[2], "utf8");
const api = (function () {
  eval(src.split("/* ---- page wiring ---- */")[0].replace('"use strict";', ""));
  return module.exports;
})();
const {feedData, hoistTable, normEntry, familyTableEntry, applyFamily, familyHasTransform,
       findSpans, effectiveEnabled, LAYER_ORDER} = api;
const feed = JSON.parse(process.argv[3]);
const d = feedData(feed);
const byFam = {};
for (const fam of d.families) { const t = familyTableEntry(fam); if (t) (byFam[fam.id] ??= []).push(t); }
for (const e of d.entries) { const n = normEntry(e); (byFam[n.family_id] ??= []).push(n); }
const allOn = new Set(LAYER_ORDER), famOn = new Set(d.families.filter(f => f.entries_included !== false).map(f => f.id));
const out = {
  hoisted: hoistTable(d.families[0]),
  leet: applyFamily("abe", byFam["leet-fam"]),
  notation_transform: applyFamily("ab", byFam["note-fam"]),
  notation_has_col: familyHasTransform(byFam["note-fam"]),
  notation_spans: findSpans("ab", byFam, ["note-fam"]).length,
  none_enabled: effectiveEnabled(d.families, new Set(), famOn),
  leet_only: effectiveEnabled(d.families, new Set(["leet"]), famOn),
  arch_enabled: effectiveEnabled(d.families, allOn, famOn).includes("arch"),
};
console.log(JSON.stringify(out));
"""
    import os
    import tempfile
    paths = []
    try:
        for content in (harness, _script()):
            with tempfile.NamedTemporaryFile("w", suffix=".cjs", delete=False) as tf:
                tf.write(content); paths.append(tf.name)
        r = subprocess.run([node, paths[0], paths[1], json.dumps(FIXTURE)],
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr
        out = json.loads(r.stdout.strip().splitlines()[-1])
    finally:
        for p in paths:
            os.unlink(p)
    # G3: family table array hoisted; array `to` maps to first variant
    assert out["hoisted"] == {"a": "4", "e": "3"}
    # acceptance (b): leet char transforms from family tables render
    assert out["leet"] == "4b3"
    # acceptance (c): notation = spans + admin, NO transform column
    assert out["notation_transform"] == "ab" and out["notation_has_col"] is False
    assert out["notation_spans"] == 1
    # acceptance (a): all layers off -> nothing enabled (admin is toggle-independent)
    assert out["none_enabled"] == []
    assert out["leet_only"] == ["leet-fam"]
    # archwiz count-only: never enabled for spans/columns
    assert out["arch_enabled"] is False
