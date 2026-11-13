"""Scheduled public quota-reading promotion contract."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/quota-readings-promote.yml"


def test_public_readings_have_bounded_automatic_refresh():
    doc = yaml.safe_load(WORKFLOW.read_text())
    events = doc.get("on", doc.get(True))  # YAML 1.1 may parse on as bool
    assert events["schedule"] == [{"cron": "17 */6 * * *"}]
    assert "workflow_dispatch" in events
    assert events["push"]["branches"] == ["master"]
    assert events["push"]["paths"] == [
        "ops/quota/registry.json",
        ".github/workflows/quota-readings-promote.yml",
    ]


def test_schedule_uses_existing_state_gate_and_single_writer():
    text = WORKFLOW.read_text()
    assert "quota-gate.txt" in text
    assert "unchanged apart from generated_at" in text
    assert "Commit promoted readings to master (single-writer)" in text
    assert "quota-usage-series-refresh" in text
