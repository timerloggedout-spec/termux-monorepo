import json
import sys
from datetime import datetime
from pathlib import Path

# Add repository root to sys.path so the script module is importable.
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import scripts.ci.calculate_lag_index as lag_index


def test_parse_iso8601():
    assert lag_index.parse_iso8601("2026-08-10T12:30:00Z") == datetime(2026, 8, 10, 12, 30, 0)
    assert lag_index.parse_iso8601("2026-08-10T12:30:00+00:00") == datetime(2026, 8, 10, 12, 30, 0)
    assert lag_index.parse_iso8601(None) is None
    assert lag_index.parse_iso8601("") is None
    assert lag_index.parse_iso8601("invalid-date") is None


def test_write_outputs_uses_context_managers(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    metrics = {
        "schema_version": 2,
        "global_averages": {
            "avg_message_response_lag_sec": 2700,
            "avg_actual_response_lag_sec": 7200,
            "suggested_debounce_ms": 2700000,
            "suggested_stale_ms": 7200000,
        },
    }
    rows = ["| PR #1 | 10.0 min | 1.0 hrs | OPEN |"]

    lag_index.write_outputs(metrics, rows)

    json_file = tmp_path / "docs" / "ops" / "response_time_lag_index.json"
    ssot_file = tmp_path / "docs" / "ops" / "LANE_CONSOLIDATION_SSOT.md"
    assert json_file.exists()
    assert ssot_file.exists()
    assert json.loads(json_file.read_text(encoding="utf-8"))["schema_version"] == 2
    assert rows[0] in ssot_file.read_text(encoding="utf-8")


def test_main_fallback(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for name in ("OPERATOR_GITHUB_TOKEN", "OPERATOR_TOKEN", "GITHUB_TOKEN"):
        monkeypatch.delenv(name, raising=False)

    lag_index.main()

    output = tmp_path / "docs" / "ops" / "response_time_lag_index.json"
    assert output.exists()
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["schema_version"] == 2
    assert "global_averages" in data
