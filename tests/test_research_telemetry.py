import json

from src import telemetry


def test_logger_writes_bounded_correlation_and_omits_sensitive_context(tmp_path, monkeypatch):
    target = tmp_path / "events.jsonl"
    monkeypatch.setattr(telemetry, "TELEMETRY_LOG", str(target))
    telemetry.TermuxTelemetryLogger.notify("INFO", "hub", "terminal event", context={
        "run_id": "run-1", "job_id": "job-2", "request_id": "req-3",
        "attempt_id": "try-4", "parent_id": "parent-5", "adapter": "swarms",
        "source_revision": "abc123", "model": "provider/model", "provider": "provider",
        "outcome": "UNKNOWN", "event": "response", "prompt": "do not persist",
        "request_body": "secret", "oversized": "x" * 300,
    })
    row = json.loads(target.read_text().splitlines()[0])
    assert row["correlation"] == {
        "run_id": "run-1", "job_id": "job-2", "request_id": "req-3",
        "attempt_id": "try-4", "parent_id": "parent-5", "adapter": "swarms",
        "source_revision": "abc123", "model": "provider/model", "provider": "provider",
        "outcome": "UNKNOWN", "event": "response",
    }
    assert "prompt" not in row and "request_body" not in row


def test_logger_events_ingest_into_existing_ledger_with_unknown_dimensions(tmp_path, monkeypatch):
    from scripts.telemetry.research_evidence import ingest
    target = tmp_path / "events.jsonl"
    ledger_file = tmp_path / "ledger.jsonl"
    monkeypatch.setattr(telemetry, "TELEMETRY_LOG", str(target))
    base = {"run_id": "r-1", "job_id": "j-1", "request_id": "q-1",
            "attempt_id": "a-1", "parent_id": "p-1", "adapter": "swarms",
            "source_revision": "rev-1", "provider": "provider", "model": "m",}
    for outcome, event in (("UNKNOWN", "response"), ("failure", "error"),
                           ("deny", "denied"), ("cancel", "cancelled"),
                           ("success", "completed")):
        telemetry.TermuxTelemetryLogger.notify("INFO", "hub", "terminal event",
                                               context={**base, "request_id": "q-" + event, "attempt_id": "a-" + event, "outcome": outcome, "event": event})
    rows = ingest(target, ledger_file)
    assert len(rows) == 5
    assert all(row["confidence"] == 0 for row in rows)
    assert all(row["provenance"]["execution"]["run_id"] == "r-1" for row in rows)
    assert ingest(target, ledger_file) == []
    assert all(row["model_id"] == "provider/m" for row in rows)
    assert all(all(value is None for value in row["dimensions"].values()) for row in rows)
    from scripts.model_selection_market.ledger import PerformanceLedger
    aggregates = PerformanceLedger(ledger_file).aggregate()
    assert aggregates["sample_count"] == 5
    assert aggregates["aggregates"]["swarms"]["provider/m"]["weight"] == 1.0


def test_correlation_rejects_malicious_field_values():
    from src.telemetry import sanitize_correlation
    safe = sanitize_correlation({"run_id": "valid", "job_id": "Bearer secret\n", "model": "x" * 161,
                                 "outcome": "success", "event": "response", "prompt": "text"})
    assert safe == {"run_id": "valid", "outcome": "success", "event": "response"}


def test_openai_compat_forwards_only_correlation_allowlist(monkeypatch):
    import io
    from llm_api_hub.clients import openai_compat as client
    seen = {}
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return b'{"choices":[]}'
    def open_url(req, timeout):
        seen.update(req.headers)
        return Response()
    monkeypatch.setattr(client.urllib.request, "urlopen", open_url)
    client.chat_completions([{"role": "user", "content": "do not put in headers"}],
        model="m", correlation={"run_id": "r", "request_id": "q", "prompt": "secret",
                                 "event": "request", "outcome": "UNKNOWN", "job_id": "bad\nvalue"})
    headers = {key.lower(): value for key, value in seen.items()}
    assert headers["x-termux-run-id"] == "r"
    assert headers["x-termux-request-id"] == "q"
    assert headers["x-termux-event"] == "request"
    assert "x-termux-prompt" not in headers and "x-termux-job-id" not in headers


def test_full_checkout_legacy_src_exposes_adapters_and_one_logger(tmp_path):
    import subprocess
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    code = '''import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
assert (root / 'termux-multi-agent/src/__init__.py').is_file()
sys.path.insert(0, str(root / 'termux-multi-agent'))
from src import telemetry
from src.swarms_adapter import validate_config
from src.swarms_rust_adapter import _HubBridge
from src.advanced_research_adapter import PIN
assert pathlib.Path(telemetry.__file__).resolve() == root / 'src' / 'telemetry.py'
telemetry.TELEMETRY_LOG = sys.argv[2]
telemetry.TermuxTelemetryLogger.notify('INFO', 'hub', 'static', context={'run_id':'legacy-root', 'event':'execution_complete', 'outcome':'UNKNOWN', 'prompt':'not-logged'})
row = json.loads(pathlib.Path(sys.argv[2]).read_text())
assert row['correlation']['run_id'] == 'legacy-root'
assert 'not-logged' not in pathlib.Path(sys.argv[2]).read_text()
'''
    subprocess.run([sys.executable, '-c', code, str(root), str(tmp_path / 'shared.jsonl')], cwd=root, check=True, capture_output=True, text=True, timeout=10)
