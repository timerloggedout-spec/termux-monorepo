import importlib


MODULE = "archwiz.termux_cockpit"


def test_cockpit_imports_without_optional_dependencies():
    module = importlib.import_module(MODULE)
    assert module.ROOT.name == "termux-monorepo"
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
