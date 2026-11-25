"""Offline process-boundary contracts; does not compile or import swarms-rs."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import threading
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import swarms_rust_adapter as adapter

CONFIG = {"task": "fixture-input", "model": "wrapper/deepseek", "execute": True}


@pytest.fixture(autouse=True)
def isolated_telemetry(tmp_path, monkeypatch):
    from src import telemetry
    monkeypatch.setattr(telemetry, "TELEMETRY_LOG", str(tmp_path / "telemetry.jsonl"))


def worker(tmp_path, body):
    script = tmp_path / "fixture-worker"
    script.write_text(f"#!{sys.executable}\n" + body)
    script.chmod(0o700)
    return script


def test_dry_run_needs_no_binary_or_network(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("dry-run must not spawn or inspect a worker")
    monkeypatch.setattr(adapter.subprocess, "run", forbidden)
    monkeypatch.setattr(adapter.shutil, "which", forbidden)
    monkeypatch.setenv("LLM_API_HUB_BASE", "invalid URL")
    result = adapter.run({"task": "  offline  "})
    assert result["status"] == "dry_run"
    assert result["backend"] == "swarms-rs"
    assert result["task"] == "offline"
    assert "output" not in result


@pytest.mark.parametrize("config", [
    {"task": "x", "execute": True}, {"task": "x", "unknown": 1},
    {"task": " "}, {**CONFIG, "max_loops": 4}, {**CONFIG, "number_agents": True},
])
def test_invalid_config_never_spawns(config, monkeypatch):
    monkeypatch.setattr(adapter.subprocess, "run", lambda *a, **k: pytest.fail("spawned"))
    with pytest.raises((ValueError, TypeError)):
        adapter.run(config)


@pytest.mark.parametrize("base", [
    "http://example.org/v1", "ftp://localhost/v1", "https://user:secret@host/v1",
    "https://host/v1?key=secret", "https://host/v1#fragment", "http://host:bad/v1",
    "https:///v1", "https://host:0/v1", "https://host/a b", "https://host\\evil/v1",
])
def test_invalid_endpoint_rejected_without_leaking_url(base):
    with pytest.raises(ValueError) as exc:
        adapter.validate_base(base)
    assert base not in str(exc.value)
    assert "secret" not in str(exc.value)


@pytest.mark.parametrize("base", ["http://127.0.0.1:8787/v1", "http://[::1]:8787/v1/",
                                  "http://localhost:8787/v1", "https://hub.example/v1"])
def test_supported_endpoint(base):
    assert adapter.validate_base(base) == base.rstrip("/") + "/"


@pytest.mark.parametrize("option", [{"timeout_seconds": 0}, {"timeout_seconds": True},
                                    {"max_tokens": -1}, {"max_tokens": 1.5}])
def test_invalid_execution_settings(option):
    with pytest.raises(ValueError):
        adapter.run({"task": "offline"}, **option)


def test_missing_worker_is_not_automatically_built(monkeypatch):
    monkeypatch.delenv("SWARMS_RS_BINARY", raising=False)
    monkeypatch.delenv("LLM_API_HUB_BASE", raising=False)
    with pytest.raises(ValueError, match="no automatic build"):
        adapter.run(CONFIG)


def test_worker_state_and_diagnostics_are_isolated(tmp_path, monkeypatch, capsys):
    record = tmp_path / "record.json"
    monkeypatch.setenv("FIXTURE_RECORD", str(record))
    monkeypatch.setenv("LLM_API_HUB_BASE", "http://127.0.0.1:8787/v1")
    original_cwd = Path.cwd()
    executable = worker(tmp_path, '''import json, os, pathlib, sys
cfg = json.load(sys.stdin)
cwd = pathlib.Path.cwd()
assert os.environ['HOME'] == str(cwd) == os.environ['TMPDIR']
assert os.environ['LLM_API_HUB_BASE'].endswith('/v1/')
assert cfg['execute'] is True and cfg['max_tokens'] == 32
pathlib.Path(os.environ['FIXTURE_RECORD']).write_text(json.dumps({'cwd': str(cwd), 'cfg': cfg}))
(cwd / 'metadata').mkdir()
(cwd / 'metadata' / 'task.json').write_text('private workflow state')
print('upstream diagnostic on stdout')
print('upstream diagnostic on stderr', file=sys.stderr)
(cwd / 'result.json').write_text(json.dumps({'status': 'complete', 'backend': 'swarms-rs',
    'output': {'history': [{'role': {'Assistant': 'reviewer'}, 'content': {'Text': 'reviewed'}}]}}))
''')
    result = adapter.run(CONFIG, binary=executable, max_tokens=32)
    assert result["output"]["history"][0]["content"]["Text"] == "reviewed"
    assert result["status"] == "complete"
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "on stdout" not in captured.err and "on stderr" not in captured.err
    assert not Path(json.loads(record.read_text())["cwd"]).exists()
    assert Path.cwd() == original_cwd


def test_sdk_requests_are_bridged_with_parent_and_unique_child_correlation(tmp_path, monkeypatch):
    seen = []
    class Hub(BaseHTTPRequestHandler):
        def do_POST(self):
            seen.append((self.path, dict(self.headers)))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"choices":[{"message":{"content":"ok"}}]}')
        def log_message(self, *_args):
            pass
    server = ThreadingHTTPServer(("127.0.0.1", 0), Hub)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv("LLM_API_HUB_BASE", f"http://127.0.0.1:{server.server_port}/v1")
    monkeypatch.setenv("LLM_API_HUB_KEY", "fixture-secret")
    executable = worker(tmp_path, '''import json, os, pathlib, urllib.request
url = os.environ['LLM_API_HUB_BASE'] + 'chat/completions'
for _ in range(2):
 req = urllib.request.Request(url, data=b'{"model":"fixture"}', headers={'Authorization':'Bearer fixture-secret','Content-Type':'application/json'}, method='POST')
 with urllib.request.urlopen(req, timeout=4) as r: assert r.status == 200
pathlib.Path('result.json').write_text(json.dumps({'status':'complete','backend':'swarms-rs','output':'ok'}))
''')
    try:
        cfg = {**CONFIG, "run_id": "run-a", "job_id": "job-b", "request_id": "parent-request",
               "attempt_id": "parent-attempt", "source_revision": "rev-c"}
        result = adapter.run(cfg, binary=executable)
        assert result["status"] == "complete"
        assert [path for path, _ in seen] == ["/v1/chat/completions"] * 2
        assert {h["X-Termux-Run-Id"] for _, h in seen} == {"run-a"}
        assert {h["X-Termux-Job-Id"] for _, h in seen} == {"job-b"}
        assert {h["X-Termux-Source-Revision"] for _, h in seen} == {"ee1e74cb6e2c94775db88dddb311f2235e3fe9e3"}
        assert {h["X-Termux-Parent-Id"] for _, h in seen} == {"parent-request"}
        assert len({h["X-Termux-Request-Id"] for _, h in seen}) == 2
        assert len({h["X-Termux-Attempt-Id"] for _, h in seen}) == 2
        assert all(h["Authorization"] == "Bearer fixture-secret" for _, h in seen)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


@pytest.mark.parametrize("payload,code,match", [
    ("not json", 0, "no valid JSON"), ("[]", 0, "invalid result object"),
    ('{"status":"error","error":"hub HTTP 401"}', 2, "Rust worker execution failed"),
    ('{"status":"complete","backend":"swarms-rs","output":"x"}', 2, "failed"),
    ('{"status":"complete"}', 0, "incomplete success"),
])
def test_bad_worker_results_and_errors_clean_state(tmp_path, monkeypatch, payload, code, match):
    record = tmp_path / "cwd.txt"
    monkeypatch.setenv("FIXTURE_RECORD", str(record))
    executable = worker(tmp_path, f'''import os, pathlib, sys
pathlib.Path(os.environ['FIXTURE_RECORD']).write_text(str(pathlib.Path.cwd()))
pathlib.Path('result.json').write_text({payload!r})
sys.exit({code})
''')
    with pytest.raises(RuntimeError, match=match):
        adapter.run(CONFIG, binary=executable)
    assert not Path(record.read_text()).exists()


def test_outer_timeout_cleans_private_workspace(tmp_path, monkeypatch):
    def timeout(*args, **kwargs):
        assert kwargs["timeout"] == 6
        assert Path(kwargs["cwd"]).is_dir()
        workspaces.append(Path(kwargs["cwd"]))
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])
    workspaces = []
    executable = worker(tmp_path, "pass\n")
    monkeypatch.setattr(adapter.subprocess, "run", timeout)
    with pytest.raises(RuntimeError, match="deadline"):
        adapter.run(CONFIG, binary=executable, timeout_seconds=1)
    assert all(not path.exists() for path in workspaces)


def test_cli_stdout_is_single_json_with_no_sdk():
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/swarms/run-rust.py"),
                           "--task", "offline"], capture_output=True, text=True, check=True)
    assert json.loads(proc.stdout)["status"] == "dry_run"
    assert not proc.stderr
