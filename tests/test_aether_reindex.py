"""Aether completion messages must represent successful invoked generators."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load():
    spec = importlib.util.spec_from_file_location("aether_reindex", ROOT / "archwiz/aether.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("failed_call", [0, 1, 2])
def test_map_stops_at_each_failed_generator(failed_call, capsys):
    module = load()
    results = [("", "", 0)] * failed_call + [("", "generator failed", 7)]
    with patch.object(module, "run", side_effect=results) as run:
        assert module.cmd_map([]) == 7
    assert run.call_count == failed_call + 1
    assert "Map + func index ready" not in capsys.readouterr().out


def test_map_reports_success_only_after_all_generators(capsys):
    module = load()
    with patch.object(module, "run", return_value=("", "", 0)) as run:
        assert module.cmd_map([]) == 0
    assert run.call_count == 3
    assert "Map + func index ready" in capsys.readouterr().out


@pytest.mark.parametrize("stage", ["bloat", "func", "manifest", "tools", "fts"])
def test_reindex_stops_at_failed_stage(stage, capsys):
    module = load()
    with patch.object(module.os.path, "exists", return_value=True), patch.object(
        module, "run", return_value=("", "generator failed", 9)
    ) as run:
        assert module.cmd_reindex([stage]) == 9
    assert run.call_count == 1
    output = capsys.readouterr().out
    assert f"Stopped at {stage}" in output
    assert "Full reindex complete" not in output


def test_reindex_propagates_map_failure(capsys):
    module = load()
    with patch.object(module, "cmd_map", return_value=8), patch.object(module, "run") as run:
        assert module.cmd_reindex(["map"]) == 8
    run.assert_not_called()
    assert "Full reindex complete" not in capsys.readouterr().out


def test_reindex_stops_after_failed_reference_hub(capsys):
    module = load()
    with patch.object(module, "run", side_effect=[("", "", 0), ("", "hub failed", 6)]):
        assert module.cmd_reindex(["manifest"]) == 6
    output = capsys.readouterr().out
    assert "Full reindex complete" not in output
    assert "reference" in output.lower()


@pytest.mark.parametrize("stage", ["bloat", "fts"])
def test_missing_optional_stage_remains_a_skip(stage, capsys):
    module = load()
    with patch.object(module.os.path, "exists", return_value=False), patch.object(
        module, "run", return_value=("", "", 0)
    ) as run:
        assert module.cmd_reindex([stage]) == 0
    assert run.call_count == 1  # Only the final reference hub is required.
    assert "Full reindex complete" in capsys.readouterr().out


def test_full_reindex_success_runs_all_stages(capsys):
    module = load()
    with patch.object(module.os.path, "exists", return_value=True), patch.object(
        module, "run", return_value=("", "", 0)
    ) as run:
        assert module.cmd_reindex([]) == 0
    assert run.call_count == 9
    assert "Full reindex complete" in capsys.readouterr().out


def test_full_reindex_stops_before_downstream_stages(capsys):
    module = load()
    results = [("", "", 0)] * 5 + [("", "manifest failed", 11)]
    with patch.object(module.os.path, "exists", return_value=True), patch.object(
        module, "run", side_effect=results
    ) as run:
        assert module.cmd_reindex([]) == 11
    assert run.call_count == 6
    assert "Full reindex complete" not in capsys.readouterr().out


@pytest.mark.parametrize("failure", ["manifest", "hub", None])
def test_real_cli_returns_generator_status(tmp_path, failure):
    home = tmp_path / "home"
    archwiz = home / "archwiz"
    archwiz.mkdir(parents=True)
    for stage, script in [("manifest", "build_data_flow_manifest.py"), ("hub", "build_reference_hub.py")]:
        (archwiz / script).write_text(f"raise SystemExit({13 if stage == failure else 0})\n")
    env = dict(os.environ, HOME=str(home))
    result = subprocess.run(
        [sys.executable, str(ROOT / "archwiz/aether.py"), "reindex", "manifest"],
        env=env, capture_output=True, text=True, check=False,
    )
    assert result.returncode == (13 if failure else 0)
    assert ("Full reindex complete" in result.stdout) == (failure is None)


@pytest.mark.parametrize("status", [None, 0, 17])
def test_main_returns_handler_status(status):
    module = load()
    with patch.object(module.sys, "argv", ["aether", "map"]), patch.object(
        module, "cmd_map", return_value=status
    ):
        assert module.main() == status


def test_real_cli_map_failure_has_nonzero_status(tmp_path):
    home = tmp_path / "home"
    llm_map = home / "workspace/llm_map"
    llm_map.mkdir(parents=True)
    (llm_map / "build_final_all_profile.py").write_text("raise SystemExit(14)\n")
    result = subprocess.run(
        [sys.executable, str(ROOT / "archwiz/aether.py"), "map"],
        env=dict(os.environ, HOME=str(home)), capture_output=True, text=True, check=False,
    )
    assert result.returncode == 14
    assert "Map + func index ready" not in result.stdout
