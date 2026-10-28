"""Linguist panel: feed-only consumption, surface markers, logic sim.

The mapping logic in linguist.html is pure and exported for node, so the
transform / span / threading behavior is exercised against a SYNTHETIC
fixture here — fixture values live only in this test, never in the page.
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "help-wanted-dashboard"
PAGE = APP / "linguist.html"


def _html():
    return PAGE.read_text(encoding="utf-8")


def _script():
    return re.search(r"<script>(.*)</script>", _html(), re.S).group(1)


def test_page_consumes_only_linguist_feed():
    fetches = re.findall(r"""fetch\(\s*["']([^"']+)["']""", _html())
    assert fetches == ["./data/linguist-feed.json"]
    assert "api.github.com" not in _html()


def test_surface_markers():
    html = _html()
    for marker in (
        "Side-by-side columns", "In-text (highlighted + threaded)",
        "Admin — all mappings", "in text", "thread",
        "feed-absent", "round-trip",
    ):
        assert marker in html, marker
    # no mapping tables hardcoded in the page
    assert "leet" not in html.lower().replace("linguist-feed", "")


def test_logic_sim_node():
    node = shutil.which("node")
    if not node:
        return  # sim is a bonus where node exists; contract tests above still pin the page
    fixture = {
        "families": [{"id": "leet", "label": "Leet"}, {"id": "rot", "label": "Toy cipher"}],
        "entries": [
            {"family_id": "leet", "granularity": "char",
             "table": {"a": "4", "e": "3"}, "direction": "both", "round_trip_verified": True},
            {"family_id": "rot", "source": "ab", "variants": ["xy"], "direction": "both"},
        ],
    }
    harness = """
const fs = require("fs");
const src = fs.readFileSync(process.argv[2], "utf8");
const api = (function () {
  eval(src.split("/* ---- page wiring ---- */")[0].replace('"use strict";', ""));
  return module.exports;
})();
const {normEntry, applyFamily, findSpans, familyHits, threadSpan} = api;
const feed = JSON.parse(process.argv[3]);
const byFam = {};
for (const e of feed.entries) { const n = normEntry(e); (byFam[n.family_id] ??= []).push(n); }
const out = {
  leet: applyFamily("abe", byFam.leet),
  spans: findSpans("abe ab", byFam, ["leet","rot"]).map(s => [s.start, s.end, s.text]),
  hits: familyHits("abe", byFam),
  thread: threadSpan(findSpans("ab", byFam, ["rot"])[0], byFam),
};
console.log(JSON.stringify(out));
"""
    script = _script()
    import os
    import tempfile
    paths = []
    try:
        for content, suffix in ((harness, ".cjs"), (script, ".cjs")):
            with tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False) as tf:
                tf.write(content); paths.append(tf.name)
        r = subprocess.run([node, paths[0], paths[1], json.dumps(fixture)],
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr
        out = json.loads(r.stdout.strip().splitlines()[-1])
    finally:
        for p in paths:
            os.unlink(p)
    assert out["leet"] == "4b3"                    # char table applied
    assert out["hits"]["leet"] >= 1                 # "mapping exists in this text"
    assert any(s[2] == "ab" for s in out["spans"])  # phrase span located
    assert out["thread"][0]["mapped"] == "xy"       # threading across families
