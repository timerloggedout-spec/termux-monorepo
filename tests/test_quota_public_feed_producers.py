"""Public quota producer cadence and dependency-order contracts."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
READINGS = ROOT / ".github/workflows/quota-readings-promote.yml"
SERIES = ROOT / ".github/workflows/quota-usage-series-refresh.yml"


def test_public_readings_refresh_on_six_hour_cadence_with_state_gate():
    text = READINGS.read_text(encoding="utf-8")
    events = text.split("\non:", 1)[1].split("\nconcurrency:", 1)[0]
    assert "cron: '17 */6 * * *'" in events
    assert "workflow_dispatch:" in events
    assert "push:" in events
    assert "quota-gate.txt" in text
    assert "Commit promoted readings to master (single-writer)" in text


def test_usage_series_regenerates_self_counts_before_pack_and_series():
    text = SERIES.read_text(encoding="utf-8")
    triggers = text.split("\non:", 1)[1].split("\nconcurrency:", 1)[0]
    assert "'scripts/quota_self_counts.py'" in triggers
    step = text.split("Rebuild the quota-usage pack + regenerate usage-series", 1)[1]
    step = step.split("Commit generated artifacts to master", 1)[0]
    assert step.index("scripts/quota_self_counts.py") < step.index("scripts/quota_usage_pack.py")
    assert step.index("scripts/quota_usage_pack.py") < step.index("scripts/quota_usage_series.py")


def test_public_status_and_usage_series_keep_distinct_single_writers():
    readings = READINGS.read_text(encoding="utf-8")
    series = SERIES.read_text(encoding="utf-8")
    assert "SINGLE-WRITER for the readings pair" in readings
    assert "SINGLE-WRITER for ops/quota/usage-series.json" in series
    assert "quota-usage-series-refresh" in readings
