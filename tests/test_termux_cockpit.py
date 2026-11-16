import importlib
import os
import re
import subprocess
import sys

import pytest


MODULE = "archwiz.termux_cockpit"


def test_cockpit_imports_without_optional_dependencies():
    module = importlib.import_module(MODULE)
    assert module.ROOT.name in ("termux-monorepo", "app")
    assert module.ARCHWIZ.name == "archwiz"


def test_action_dispatches_existing_tool(monkeypatch):
    module = importlib.import_module(MODULE)
    calls = []

    def fake_run(path, *args, **kwargs):
        calls.append((path.name, args))
        return 0

    monkeypatch.setattr(module, "run", fake_run)
    assert module.action("2") is True
    assert calls == [("archaeo_sweep.py", ())]


def test_dual_gate_requires_both_gates(monkeypatch, capsys):
    module = importlib.import_module(MODULE)
    calls = []
    results = iter((0, 1))

    def fake_gate(command):
        calls.append(command)
        return next(results)

    monkeypatch.setattr(module, "gate", fake_gate)
    assert module.action("18") is False
    assert calls == [
        ["python3", "scripts/ci/repo_gate.py", "--base", "origin/master"],
        ["python3", "scripts/ci/termux_smoke.py"],
    ]
    output = capsys.readouterr().out
    assert "repo-gate=PASS" in output
    assert "termux-smoke=FAIL" in output


def test_backup_only_archives_state_that_exists(monkeypatch):
    module = importlib.import_module(MODULE)
    captured = {}

    class Result:
        returncode = 0

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        return Result()

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module.time, "strftime", lambda _fmt: "20990101_010203")
    monkeypatch.setattr(module.Path, "exists", lambda path: path.name in {"HANDOFF.json", "foresight_state.json"})

    assert module.action("5") is True
    assert captured["command"][0:2] == ["tar", "czf"]
    assert "HANDOFF.json" in captured["command"]
    assert "foresight_state.json" in captured["command"]
    assert "master_tasks.json" not in captured["command"]
    assert "metrics_log.jsonl" not in captured["command"]
    assert captured["kwargs"]["cwd"] == str(module.ARCHWIZ)


def test_status_action_reports_state_without_running_tools(monkeypatch, capsys):
    module = importlib.import_module(MODULE)
    monkeypatch.setattr(module.Path, "exists", lambda path: path.name == "foresight_state.json")
    assert module.action("20") is True
    output = capsys.readouterr().out
    assert "HYPER-FORGE ONLINE" in output
    assert "foresight_state : present" in output
    assert "canonical state : repository / protocol / GitHub evidence" in output


@pytest.mark.parametrize("theme, colored", [(None, True), ("tron", True), ("plain", False)])
def test_theme_applies_to_rendered_cockpit(theme, colored):
    module = importlib.import_module(MODULE)
    env = os.environ.copy()
    env.pop("ARCHWIZ_THEME", None)
    if theme is not None:
        env["ARCHWIZ_THEME"] = theme
    result = subprocess.run(
        [sys.executable, str(module.ARCHWIZ / "termux_cockpit.py")],
        input="20\n\nq\n", capture_output=True, text=True, env=env, timeout=10,
    )
    assert result.returncode == 0
    assert "COCKPIT MATRIX" in result.stdout
    assert "HYPER-FORGE ONLINE" in result.stdout
    assert bool(re.search(r"\x1b\[[0-9;]*m", result.stdout)) is colored


def test_dispatch_requires_auto_mode_selection(monkeypatch):
    module = importlib.import_module(MODULE)
    monkeypatch.delenv("ARCHWIZ_MODE", raising=False)
    calls = []
    monkeypatch.setattr(module, "run", lambda path, *args: calls.append((path.name, args)) or 0)
    assert module.action("1") is True
    assert module.action("a") is True
    assert module.action("1") is True
    assert module.action("r") is True
    assert module.action("1") is True
    assert calls == [
        ("autonomous_runner.py", ()),
        ("autonomous_runner.py", ("--auto-approve",)),
        ("autonomous_runner.py", ()),
    ]


@pytest.mark.parametrize("choice, directory, filename", [
    ("12", "LLM_MAP", "narrative.py"),
    ("13", "ARCHWIZ", "lexicon_harvest.py"),
    ("14", "ARCHWIZ", "forensic_toolchain.py"),
    ("15", "ARCHWIZ", "live_view.py"),
    ("16", "ARCHWIZ", "documentation_refresh.py"),
])
@pytest.mark.parametrize("installed, returncode", [(False, 0), (True, 0), (True, 1)])
def test_optional_helpers(choice, directory, filename, installed, returncode,
                          tmp_path, monkeypatch, capsys):
    module = importlib.import_module(MODULE)
    monkeypatch.setattr(module, directory, tmp_path)
    target = tmp_path / filename
    if installed:
        target.touch()
    calls = []
    monkeypatch.setattr(module, "run", lambda path: calls.append(path) or returncode)
    assert module.action(choice) is (not installed or returncode == 0)
    output = capsys.readouterr().out
    if installed:
        assert calls == [target]
        assert "not installed" not in output
    else:
        assert calls == []
        assert f"not installed: {target}" in output


@pytest.mark.parametrize("quit_choice", ["q", "0"])
def test_menu_continues_after_failed_action(quit_choice, monkeypatch, capsys):
    module = importlib.import_module(MODULE)
    choices = iter(("18", "", "20", "", quit_choice))
    monkeypatch.setattr("builtins.input", lambda _prompt: next(choices))
    monkeypatch.setattr(module, "gate", lambda _command: 1)
    assert module.main() == 0
    output = capsys.readouterr().out
    assert "Action 18 failed." in output
    assert "HYPER-FORGE ONLINE" in output
    assert output.count("COCKPIT MATRIX") == 3


@pytest.mark.parametrize("quit_choice", ["q", "0"])
def test_quit_does_not_dispatch_an_action(quit_choice, monkeypatch):
    module = importlib.import_module(MODULE)
    monkeypatch.setattr("builtins.input", lambda _prompt: quit_choice)
    monkeypatch.setattr(module, "action", lambda _choice: pytest.fail("Quit dispatched an action"))
    assert module.main() == 0


def test_established_tui_launches_cockpit(monkeypatch, capsys):
    module = importlib.import_module("archwiz.archwiz")
    choices = iter(("20", "0"))
    calls = []
    monkeypatch.setattr("builtins.input", lambda _prompt: next(choices))
    monkeypatch.setattr(module, "banner", lambda: None)
    monkeypatch.setattr(module.subprocess, "run", lambda command: calls.append(command))
    module.main()
    assert "Termux Hyper-Forge Cockpit" in capsys.readouterr().out
    assert calls == [["python3", str(module.ARCHWIZ_DIR / "termux_cockpit.py")]]
