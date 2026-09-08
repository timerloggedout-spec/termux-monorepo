import json
import subprocess
import sys


def test_hex_moneyball_export_builds_sanitized_bundle(tmp_path):
    source = tmp_path / "events.ndjson"
    source.write_text(
        json.dumps(
            {
                "timestamp": "2026-09-09T00:00:00Z",
                "level": "INFO",
                "agent": "agent-a",
                "target": "issue-461",
                "attempt": 2,
                "message": "private payload must not leave the evidence plane",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    ndjson = tmp_path / "bundle.ndjson"
    csv = tmp_path / "bundle.csv"
    receipt = tmp_path / "receipt.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/hex_moneyball_export.py",
            str(source),
            str(ndjson),
            "--csv",
            str(csv),
            "--receipt",
            str(receipt),
            "--snapshot-id",
            "run-1-attempt-1",
            "--source-sha",
            "abc123",
            "--source-ref",
            "master",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    record = json.loads(ndjson.read_text(encoding="utf-8").splitlines()[0])
    receipt_data = json.loads(receipt.read_text(encoding="utf-8"))
    assert record["contract_version"] == "3l0.moneyball.v1"
    assert record["snapshot_id"] == "run-1-attempt-1"
    assert record["message_present"] is True
    assert "message" not in record
    assert "prompt" not in record
    assert receipt_data["validation_status"] == "VALIDATED"
    assert receipt_data["privacy_assertion"] == "passed"
    assert receipt_data["raw_content_exported"] is False
    assert csv.exists()
    assert '"validation_status":"VALIDATED"' in result.stdout
    assert '"records":1' in result.stdout
