import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "free_tier_value_projection.py"


class FreeTierValueProjectionTest(unittest.TestCase):
    def fixture(self, root):
        board = root / "apps/tribute-dashboard/data/free-tier-value.json"
        board.parent.mkdir(parents=True)
        board.write_text(json.dumps({
            "schema": "3l0.free-tier-use-value.v1",
            "pricing": [{
                "pricing_id": "price-a",
                "canonical_model_id": "provider/model-a",
                "input_usd_per_million": 1,
                "output_usd_per_million": 2
            }],
            "sessions": []
        }), encoding="utf-8")
        return board

    def test_unvalidated_observation_is_coverage_not_value(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            source = root / "observations.ndjson"
            source.write_text(json.dumps({
                "run_id": "10", "run_attempt": 2, "request_id": "req-1",
                "provider": "provider-a", "requested_model": "model-a",
                "tokens_in": 12, "tokens_out": 5, "requests_used": 1
            }) + "\n", encoding="utf-8")
            out = root / "out.json"
            subprocess.run([sys.executable, str(SCRIPT), "--root", str(root),
                            "--observations", str(source), "--source-sha", "a" * 40,
                            "--out", str(out)], check=True, capture_output=True, text=True)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["sessions"], [])
            self.assertEqual(data["coverage"][0]["tokens_in"], 12)
            self.assertEqual(data["coverage"][0]["evidence_status"],
                             "publication_gates_or_exact_model_pricing_not_established")
            self.assertEqual(data["source_manifest"]["withheld_count"], 1)

    def test_only_fully_gated_exact_call_is_published(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            source = root / "observations.ndjson"
            row = {
                "run_id": "10", "run_attempt": 2, "repository": "o/r",
                "timestamp": "2026-11-02T00:00:00Z", "call_uid": "call-1",
                "provider": "provider-a", "model_id": "model-a",
                "model_version_pin": "model-a@v1", "canonical_model_id": "provider/model-a",
                "pricing_id": "price-a", "tokens_in": 12, "tokens_out": 5,
                "outcome_status": "SUCCESS", "validation_status": "VALIDATED",
                "basksweep_status": "PASS", "publication_status": "PUBLIC_SAFE",
                "billing_status": "VERIFIED_NO_COST", "cost_usd": 0.0
            }
            source.write_text(json.dumps(row) + "\n", encoding="utf-8")
            out = root / "out.json"
            subprocess.run([sys.executable, str(SCRIPT), "--root", str(root),
                            "--observations", str(source), "--out", str(out)],
                           check=True, capture_output=True, text=True)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(len(data["sessions"]), 1)
            self.assertEqual(data["sessions"][0]["run_uid"], "gha:o/r:10:2")
            self.assertEqual(data["sessions"][0]["call_uid"], "call-1")


if __name__ == "__main__":
    unittest.main()
