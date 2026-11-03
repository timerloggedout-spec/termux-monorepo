"""Tests for the webApp surface bundle (web/, issue #4092).

The state builder must emit the core's state shapes; the committed
state.json must match that structure; the bundle must be complete
and installable-shaped; app.js must parse and carry both SR
engines with scheduler-named receipts.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "web"))

WEB = ROOT / "web"


def test_state_builder_emits_core_shapes():
    from build_data import emit_state
    state = emit_state(ROOT)
    assert state["surface"] == "studysprint-webapp"
    assert state["surface_version"] == \
        (WEB / "VERSION").read_text().strip()
    assert state["plan"]["total_sessions"] > 0
    assert state["trust_receipt"] is not None
    assert state["today"]["sessions"]
    assert state["sr"]["cards"]
    ux = state["sr"]["ux_state"]["cards"]
    assert ux and "ts_fsrs" in ux[0]  # the core UX-state export
    assert state["reader"]["sections"]
    assert state["reader"]["sections"][0]["words"]


def test_committed_state_matches_builder_structure():
    from build_data import emit_state
    committed = json.loads((WEB / "data" / "state.json").read_text())
    fresh = emit_state(ROOT)
    assert sorted(committed) == sorted(fresh)
    assert len(committed["sr"]["cards"]) == len(fresh["sr"]["cards"])
    assert committed["surface_version"] == fresh["surface_version"]


def test_bundle_complete_and_installable():
    manifest = json.loads((WEB / "manifest.webmanifest").read_text())
    assert manifest["display"] == "standalone"
    assert manifest["name"] == "StudySprint"
    for icon in manifest["icons"]:
        assert (WEB / icon["src"]).exists(), icon["src"]
    html = (WEB / "index.html").read_text()
    assert 'rel="manifest"' in html
    assert "serviceWorker" in html and "sw.js" in html
    sw = (WEB / "sw.js").read_text()
    for asset in ("index.html", "app.js", "styles.css",
                  "data/state.json", "manifest.webmanifest"):
        assert asset in sw, f"sw.js must cache {asset}"
        assert (WEB / asset).exists(), asset
    css = (WEB / "styles.css").read_text()
    assert "min-height: 48px" in css  # FEATURES one-thumb rule


def test_app_js_engines_and_syntax():
    js = (WEB / "app.js").read_text()
    assert "fsrsReview" in js and "FSRS_W" in js
    assert "sm2Review" in js
    assert "scheduler=fsrs" in js and "scheduler=sm2" in js
    assert "localStorage" in js
    node = shutil.which("node")
    if node:
        subprocess.run([node, "--check", str(WEB / "app.js")],
                       check=True)


def test_web_ingest_legs():
    html = (WEB / "index.html").read_text()
    assert 'id="ingest-file"' in html
    assert 'accept=".txt,.md,text/plain"' in html
    assert 'id="ingest-camera"' in html
    assert 'accept="image/*" capture="environment"' in html
    assert 'id="ingest-confirm"' in html
    js = (WEB / "app.js").read_text()
    assert "function parseSyllabus" in js
    assert "ss.ingest.pending" in js  # confirm gate: pending first
    assert "ss.ingest.placed" in js   # placed only on confirm
    assert "awaiting-core-ocr" in js  # captures are honest, not parsed


# ------------------------------------------------------ RFP-D1-7 award batch
def test_state_carries_plan_start_and_surface_version():
    from build_data import emit_state
    state = emit_state(ROOT)
    assert state["plan_start"]  # #4214: Today advances from here
    assert state["surface_version"] == "0.1.1"


def test_service_worker_cache_is_versioned_and_state_network_first():
    sw = (WEB / "sw.js").read_text()
    version = (WEB / "VERSION").read_text().strip()
    assert f"studysprint-webapp-v{version}" in sw  # #4219
    assert "network-first" in sw and "data/state.json" in sw


def test_js_pure_helpers_behavior():
    """The due-queue + day-index helpers are pure functions —
    exercise them for real in node (extracted from app.js)."""
    node = shutil.which("node")
    if node is None:
        pytest.skip("node not available")
    app_js = (WEB / "app.js").read_text()
    start = app_js.index("function computeDayIndex")
    end = app_js.index("/* ---------------- loading")
    helpers = app_js[start:end]
    script = helpers + """
const assert = require("assert");
// #4214: three days after plan start, 12 sessions -> day 3
assert.strictEqual(computeDayIndex("2026-11-01", 12,
  new Date("2026-11-04T12:00:00")), 3);
assert.strictEqual(computeDayIndex("2026-11-01", 12,
  new Date("2027-01-01T00:00:00")), 5);  // clamped to plan end
// #4218: a card graded to tomorrow is NOT in today's queue;
// a new card is; earliest due first
const cards = [{card_id: "a"}, {card_id: "b"}, {card_id: "c"}];
const sr = { a: {due: "2999-01-01T00:00:00.000Z"},
             c: {due: "2020-01-01T00:00:00.000Z"} };
const q = dueQueue(cards, sr, "fsrs", new Date());
assert.deepStrictEqual(q.map((c) => c.card_id), ["c", "b"]);
assert.strictEqual(nextDueDate(cards, sr, "fsrs"),
                   "2020-01-01T00:00:00.000Z");
console.log("helpers ok");
"""
    proc = subprocess.run([node, "-e", script], capture_output=True,
                          text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr


def test_today_checkins_persist_and_sample_disclosed():
    app_js = (WEB / "app.js").read_text()
    assert "ss.checkins" in app_js  # #4215: recorded, not cosmetic
    assert "shifted to tomorrow" in app_js  # the no-guilt shift
    html = (WEB / "index.html").read_text()
    assert 'id="sample-disclosure"' in html  # #4216
    assert 'id="reader-section-select"' in html  # #4217
    assert 'id="reader-prev"' in html and 'id="reader-next"' in html


def test_parity_statement_names_true_foundation():
    parity = (ROOT / "evidence" / "web" / "parity.md").read_text()
    version = (ROOT / "VERSION").read_text().strip()
    assert f"Rides the foundation (v{version}" in parity  # #4225
    assert "(v0.4.0" not in parity


def test_versioning_doc_records_surface_ruling():
    doc = (ROOT / "VERSIONING.md").read_text()
    assert "Surface version lines are independent" in doc  # #4212
