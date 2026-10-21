import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/swarms/research-plan.py"
SPEC = importlib.util.spec_from_file_location("swarms_research_plan", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_plan_is_deterministic_and_uses_registered_pins():
    first = MODULE.build_plan("parity", "  compare parity  ")
    second = MODULE.build_plan("parity", "compare parity")
    assert first == second
    assert first["status"] == "planned"
    assert first["execution"] == "not_performed"
    assert first["task"] == "compare parity"
    assert first["market_contract"].startswith("docs/proposals/active/model-selection-market/")
    assert first["sources"][0]["revision"] == "8ec7948ce6e8ab28c4454d6c2c3187a735672067"
    assert first["sources"][0]["sha256"]
    assert first["sources"][1]["revision"] == "ee1e74cb6e2c94775db88dddb311f2235e3fe9e3"


def test_research_wallet_sources_registered():
    research = MODULE.build_plan("research", "review")
    wallets = MODULE.build_plan("wallets", "review")
    assert research["sources"][0]["revision"] == "a262cb9d9703681c5a5066f03eb9fb89ad4d9cae"
    revisions = {source["revision"] for source in wallets["sources"] if "revision" in source}
    assert revisions == {"fc4940f145f38529b9acf5c9e79b0435ab769b7f", "25e66b156d70a6ff32735449876609a2ec91b3c0"}
    assert "RPC chain" in " ".join(wallets["evidence_requirements"])


def test_cli_emits_json_and_rejects_invalid_input():
    result = subprocess.run([sys.executable, str(SCRIPT), "--lane", "research", "--task", " inspect "], capture_output=True, text=True, check=True)
    assert json.loads(result.stdout)["task"] == "inspect"
    for args in (("--lane", "bogus", "--task", "x"), ("--lane", "parity", "--task", "   "), ("--lane", "parity", "--task", "x" * 501)):
        failed = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
        assert failed.returncode == 2


def test_planner_imports_are_offline_and_upstream_free(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("network access attempted")

    monkeypatch.setattr("socket.create_connection", blocked)
    monkeypatch.setattr("urllib.request.urlopen", blocked)
    monkeypatch.setattr("http.client.HTTPConnection.request", blocked)
    before = set(sys.modules)
    MODULE.build_plan("research", "offline")
    imported = set(sys.modules) - before
    assert not any(name == "swarms" or name.startswith("swarms.") for name in imported)


def test_registry_matches_canonical_locks_and_existing_market():
    registry = json.loads(MODULE.REGISTRY.read_text())
    source_lock = json.loads((ROOT / "integrations/swarms/source-lock.json").read_text())
    source = registry["lanes"]["parity"]["sources"][0]
    assert source["repository"] == source_lock["repository"]
    assert source["revision"] == source_lock["revision"]
    assert source["sha256"] == {name: value["sha256"] for name, value in source_lock["files"].items()}
    assert registry["lanes"]["wallets"]["sources"][0]["repository"] == "The-Swarm-Corporation/ATP-Protocol"
    market_path = registry["market_contract"].split("#")[0]
    assert (ROOT / market_path).is_file()
