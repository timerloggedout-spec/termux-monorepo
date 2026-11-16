"""Offline tests for the Temporal pass assets (no server needed)."""
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "scripts" / "temporal"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, T / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_unit_payload_deterministic():
    h = _load("kill_resume_harness")
    a, b = h._unit_payload("unit-x"), h._unit_payload("unit-x")
    assert a == b and a["records"] and len(a["digest"]) == 64


def test_versioning_model_properties():
    m = _load("versioning_model")
    assert m.route(["b1", "b2"], "b2", {"wf": "b1"}, "wf") == "b1"
    assert m.route(["b1", "b2"], "b2", {}, "new") == "b2"
    assert m.autoscale(0, 100) == m.MIN_WORKERS
    assert m.autoscale(10**9, 10**5) == m.MAX_WORKERS
    assert m.autoscale(100, 100) <= m.autoscale(500, 100)


def test_envelope_validators_agree():
    v = _load("validate_envelope")
    sha = "a" * 64
    valid = {"workflow_id": "w", "unit_id": "u", "receipt_sha256": sha,
             "receipt_count": 1, "history_sha256": sha, "unknown_outcomes": []}
    assert v.validate(valid) == []
    broken = {"unit_id": "", "receipt_sha256": "nope",
              "receipt_count": "one", "unknown_outcomes": {}}
    assert len(v.validate(broken)) >= 4  # aggregated, never first-fail
    if shutil.which("node"):
        out = subprocess.run(
            ["python3", str(T / "run_contract_fixture.py")],
            capture_output=True, text=True, timeout=120)
        assert out.returncode == 0, out.stdout + out.stderr


def test_doe_scorer_deterministic():
    d = _load("doe_slice")
    result = {"unit_id": "u", "receipt": {"unit_id": "u"}, "unknown_outcomes": []}
    assert d._score("completed", result) == 1.0
    assert d._score("completed", {**result, "unknown_outcomes": [{"x": 1}]}) == 0.0
    assert d._score("specified_not_run", None) == 0.0
