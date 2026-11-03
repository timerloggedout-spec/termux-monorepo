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
