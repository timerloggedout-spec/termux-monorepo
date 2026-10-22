import json
import os
import subprocess
import sys
from types import SimpleNamespace
from pathlib import Path
import importlib.util

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("swarms_adapter", ROOT / "src/swarms_adapter.py")
adapter = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = adapter
spec.loader.exec_module(adapter)


@pytest.fixture(autouse=True)
def isolated_telemetry(tmp_path, monkeypatch):
    from src import telemetry
    monkeypatch.setattr(telemetry, "TELEMETRY_LOG", str(tmp_path / "telemetry.jsonl"))


def test_dry_run_does_not_import_or_call_swarms(monkeypatch):
    def forbidden():
        raise AssertionError("network/upstream work during dry run")
    monkeypatch.setattr(adapter, "_HubLLM", forbidden)
    out = adapter.run({"task": "  summarize  "})
    assert out["status"] == "dry_run"
    assert out["task"] == "summarize"


@pytest.mark.parametrize("config", [
    {"task": "x", "wat": 1}, {"task": "x", "max_loops": True},
    {"task": "x", "number_agents": 3}, {"task": " "},
    {"task": "x", "model": " "}, {"task": "x", "execute": "yes"},
    {"task": "x", "execute": True},
])
def test_invalid_configs(config):
    with pytest.raises((TypeError, ValueError)):
        adapter.validate_config(config)


def test_fake_upstream_forwarding_and_hub_contract(monkeypatch, tmp_path):
    calls = []
    workspaces = []
    original_cwd = Path.cwd()
    class Agent:
        def __init__(self, **kw):
            calls.append(("agent", kw))
            self.llm = kw["llm"]
            workspaces.append(Path(os.environ["WORKSPACE_DIR"]))
            assert Path.cwd() == workspaces[-1]
            assert os.environ["SWARMS_TELEMETRY_ON"] == "false"
    class Workflow:
        def __init__(self, **kw):
            calls.append(("workflow", kw))
        def run(self, task):
            calls.append(("run", task))
            return "done"
    upstream = SimpleNamespace(Agent=Agent, SequentialWorkflow=Workflow)
    monkeypatch.setenv("WORKSPACE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("SWARMS_TELEMETRY_ON", "true")
    import llm_api_hub.clients.openai_compat as hub
    def chat(messages, model, **kwargs):
        assert messages == [{"role": "user", "content": "task"}]
        assert model == "provider/model"
        return {"choices": [{"message": {"content": "response"}}]}
    monkeypatch.setattr(hub, "chat_completions", chat)
    out = adapter.run({"task": "task", "model": "provider/model", "execute": True,
                       "max_loops": 2, "number_agents": 2}, swarms_module=upstream)
    assert out["output"] == "done"
    assert Path.cwd() == original_cwd
    assert os.environ["WORKSPACE_DIR"] == str(tmp_path / "state")
    assert os.environ["SWARMS_TELEMETRY_ON"] == "true"
    assert all(not path.exists() for path in workspaces)
    assert [x[0] for x in calls] == ["agent", "agent", "workflow", "run"]
    for _, kw in calls[:2]:
        assert kw["retry_attempts"] == 1 and kw["print_on"] is False
        assert kw["autosave"] is False and kw["tools"] == []
        assert kw["llm"].run("task") == "response"
    assert calls[2][1]["max_loops"] == 2 and calls[2][1]["autosave"] is False


def test_failed_execution_restores_state(monkeypatch):
    workspaces = []
    original_cwd = Path.cwd()
    monkeypatch.delenv("WORKSPACE_DIR", raising=False)
    monkeypatch.delenv("SWARMS_TELEMETRY_ON", raising=False)
    class BrokenAgent:
        def __init__(self, **kw):
            workspaces.append(Path(os.environ["WORKSPACE_DIR"]))
            raise RuntimeError("deliberate constructor failure")
    upstream = SimpleNamespace(Agent=BrokenAgent, SequentialWorkflow=object)
    with pytest.raises(RuntimeError, match="deliberate constructor failure"):
        adapter.run({"task": "x", "model": "route", "execute": True}, swarms_module=upstream)
    assert Path.cwd() == original_cwd
    assert "WORKSPACE_DIR" not in os.environ
    assert "SWARMS_TELEMETRY_ON" not in os.environ
    assert all(not path.exists() for path in workspaces)


def test_sdk_conversation_messages_are_forwarded_not_null_task(monkeypatch):
    import llm_api_hub.clients.openai_compat as hub
    messages = [{"role": "system", "content": "Review supplied evidence."},
                {"role": "user", "content": "The actual task."}]
    seen = []
    def chat(payload, model, **kwargs):
        seen.append(payload)
        return {"choices": [{"message": {"content": "reviewed"}}]}
    monkeypatch.setattr(hub, "chat_completions", chat)
    assert adapter._HubLLM("hub/route").run(task=None, messages=messages) == "reviewed"
    assert seen == [messages]


@pytest.mark.parametrize("kwargs", [{}, {"messages": []}, {"messages": "text"},
                                   {"messages": [{"role": "user", "content": None}]},
                                   {"messages": [{"role": "tool", "content": "x"}]}])
def test_invalid_sdk_payload_is_rejected_before_hub_call(monkeypatch, kwargs):
    import llm_api_hub.clients.openai_compat as hub
    def forbidden(*args, **kwargs):
        raise AssertionError("Invalid payload must not reach hub")
    monkeypatch.setattr(hub, "chat_completions", forbidden)
    with pytest.raises(ValueError):
        adapter._HubLLM("hub/route").run(**kwargs)


def test_cli_prints_json_dry_run():
    p = subprocess.run([sys.executable, "scripts/swarms/run.py", "--task", "offline"],
                       text=True, capture_output=True, check=True)
    assert json.loads(p.stdout)["status"] == "dry_run"
    assert not p.stderr
