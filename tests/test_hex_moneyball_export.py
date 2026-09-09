import csv
import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


class HexMoneyballExportTest(unittest.TestCase):
    def test_builds_sanitized_bundle(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "events.ndjson"
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
            ndjson = root / "bundle.ndjson"
            csv_path = root / "bundle.csv"
            receipt = root / "receipt.json"

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/hex_moneyball_export.py",
                    str(source),
                    str(ndjson),
                    "--csv",
                    str(csv_path),
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
            self.assertEqual(record["contract_version"], "3l0.moneyball.v1")
            self.assertEqual(record["snapshot_id"], "run-1-attempt-1")
            self.assertTrue(record["message_present"])
            self.assertNotIn("message", record)
            self.assertNotIn("prompt", record)
            self.assertEqual(receipt_data["validation_status"], "VALIDATED")
            self.assertEqual(receipt_data["privacy_assertion"], "passed")
            self.assertFalse(receipt_data["raw_content_exported"])

            self.assertTrue(csv_path.exists())
            with csv_path.open(newline="", encoding="utf-8") as stream:
                reader = csv.DictReader(stream)
                self.assertEqual(
                    reader.fieldnames,
                    [
                        "contract_version", "snapshot_id", "timestamp", "level",
                        "agent_id", "target", "attempt_no", "message_sha256",
                        "message_present",
                    ],
                )
                rows = list(reader)
            self.assertEqual(rows[0]["snapshot_id"], "run-1-attempt-1")
            self.assertEqual(rows[0]["message_present"], "true")
            self.assertEqual(len(rows), 1)

            self.assertIn('"validation_status":"VALIDATED"', result.stdout)
            self.assertIn('"records":1', result.stdout)


if __name__ == "__main__":
    unittest.main()
