"""Schema_version discipline (#4470): every synced/stored
artifact class carries an explicit version; readers refuse
loudly on mismatch. This file pins the state class end to
end; SCHEMA-VERSIONS.md inventories the rest."""
import json
import sys
from pathlib import Path

import pytest

APP_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_ROOT))


def test_emitters_stamp_the_state():
    import importlib.util
    from study_tools import STATE_SCHEMA_VERSION, validate_state
    spec = importlib.util.spec_from_file_location(
        "build_data", APP_ROOT / "web" / "build_data.py")
    build_data = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build_data)
    doc = build_data.emit_state(APP_ROOT)
    assert doc["schema_version"] == STATE_SCHEMA_VERSION
    assert validate_state(doc) is doc
    import tui
    tui_state = tui.build_state(APP_ROOT)
    assert tui_state["schema_version"] == STATE_SCHEMA_VERSION


def test_validator_refuses_mismatch_and_absence_loudly():
    from study_tools import validate_state
    with pytest.raises(ValueError, match="schema mismatch"):
        validate_state({"schema_version": "studysprint-state/99"})
    with pytest.raises(ValueError, match="schema mismatch"):
        validate_state({})  # absent = refused, not guessed


def test_committed_bundle_state_carries_the_stamp():
    from study_tools import STATE_SCHEMA_VERSION
    doc = json.loads(
        (APP_ROOT / "web" / "data" / "state.json").read_text())
    assert doc["schema_version"] == STATE_SCHEMA_VERSION


def test_web_reader_gate_matches_the_core_constant():
    """Cross-language pin (the FSRS battery pattern): the JS
    reader's version constant must equal the core's, and the
    refusal must route through the named load-failure state."""
    from study_tools import STATE_SCHEMA_VERSION
    app_js = (APP_ROOT / "web" / "app.js").read_text()
    assert f'const STATE_SCHEMA_VERSION = "{STATE_SCHEMA_VERSION}";' \
        in app_js
    assert "foundSchema !== STATE_SCHEMA_VERSION" in app_js
    assert "nothing was rendered from mismatched data" in app_js
