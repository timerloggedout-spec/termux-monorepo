"""Offline coverage for the canonical DeepAgent entrypoint."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / "DeepAgent.py"


def run(*args, token=None):
    env = os.environ.copy()
    env.pop("DEEPSEEK_API_KEY", None)
    env.pop("DEEPCLI_TOKEN", None)
    if token:
        env["DEEPSEEK_API_KEY"] = token
    return subprocess.run([sys.executable, str(ENTRY), *args], cwd=ROOT, env=env,
                          text=True, capture_output=True, check=False)


def test_doctor_reports_readiness_and_no_secret_value():
    secret = "do-not-print-this-value"
    result = run("--doctor", token=secret)
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["ok"] is True
    assert report["checks"]["admin_is_privilege"] is False
    assert "engineer" in report["checks"]["available_roles"]
    assert secret not in result.stdout


def test_doctor_is_offline_when_credentials_absent():
    result = run("--doctor")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["checks"]["deepseek_token_configured"] is False
    assert report["ok"] is True  # installation readiness is distinct from provider auth


def test_doctor_rejects_task_arguments():
    result = run("--doctor", "task")
    assert result.returncode == 2
    assert "cannot be combined" in result.stderr


def test_mocked_task_execution_reaches_chat_and_finishes(monkeypatch, capsys):
    # Importing the real agent proves its direct runtime dependencies resolve;
    # replace provider/session edges so this exercises loop orchestration offline.
    sys.path.insert(0, str(ROOT / "deepcli"))
    import deepagent
    monkeypatch.setattr(deepagent.session_store, "task_key", lambda *_: "test-key")
    monkeypatch.setattr(deepagent.session_store, "load", lambda *_: None)
    monkeypatch.setattr(deepagent.session_store, "load_run_state", lambda *_: None)
    monkeypatch.setattr(deepagent.session_store, "save", lambda *_, **__: None)
    monkeypatch.setattr(deepagent.session_store, "save_run_state", lambda *_, **__: None)
    monkeypatch.setattr(deepagent, "_notify", lambda *_, **__: None)
    monkeypatch.setattr(deepagent, "_autosnapshot", lambda *_: None)
    monkeypatch.setattr(deepagent, "_chat_once", lambda *_, **__: ("sid", "mock complete", [], None))
    monkeypatch.setenv("AGENT_SAFETY_CEILING", "1")
    monkeypatch.setenv("AGENT_STEP_PACE", "0")
    result = deepagent.loop("offline task", role="release_steward", task_id="t1", transport="auto")
    assert result == "mock complete"
    assert "[role] release_steward [task_id] t1" in capsys.readouterr().out
