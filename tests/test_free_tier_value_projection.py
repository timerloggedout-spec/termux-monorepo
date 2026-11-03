import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "free_tier_value_projection.py"


class FreeTierValueProjectionTest(unittest.TestCase):
    def fixture(self, root, pricing=None):
        board = root / "apps/tribute-dashboard/data/free-tier-value.json"
        board.parent.mkdir(parents=True)
        board.write_text(json.dumps({
            "schema": "3l0.free-tier-use-value.v1",
            "pricing": pricing if pricing is not None else [{
                "pricing_id": "price-a",
                "canonical_model_id": "provider/model-a",
                "input_usd_per_million": 1,
                "output_usd_per_million": 2
            }],
            "sessions": []
        }), encoding="utf-8")
        return board

    def row(self, **overrides):
        row = {
            "run_id": "10", "run_attempt": 2, "repository": "o/r",
            "timestamp": "2026-11-02T00:00:00Z", "call_uid": "call-1",
            "workflow": "Continuous Evaluation", "head_sha": "a" * 40,
            "latency_ms": 500,
            "provider": "provider-a", "model_id": "model-a",
            "model_version_pin": "model-a@v1",
            "canonical_model_id": "provider/model-a", "pricing_id": "price-a",
            "tokens_in": 12, "tokens_out": 5,
            "outcome_status": "SUCCESS", "validation_status": "VALIDATED",
            "basksweep_status": "PASS", "publication_status": "PUBLIC_SAFE",
            "billing_status": "VERIFIED_NO_COST", "cost_usd": 0
        }
        row.update(overrides)
        return row

    def run_projection(self, root, rows):
        source = root / "observations.ndjson"
        source.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        out = root / "out.json"
        subprocess.run([
            sys.executable, str(SCRIPT), "--root", str(root),
            "--observations", str(source), "--source-sha", "a" * 40, "--out", str(out)
        ], check=True, capture_output=True, text=True)
        return json.loads(out.read_text(encoding="utf-8"))

    def test_unvalidated_observation_is_coverage_not_value(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            data = self.run_projection(root, [{
                "run_id": "10", "run_attempt": 2, "request_id": "req-1",
                "provider": "provider-a", "requested_model": "model-a",
                "tokens_in": 12, "tokens_out": 5, "requests_used": 1
            }])
            self.assertEqual(data["sessions"], [])
            self.assertEqual(data["coverage"][0]["tokens_in"], 12)
            self.assertEqual(data["coverage"][0]["evidence_status"], "missing_call_identity")
            self.assertEqual(data["source_manifest"]["withheld_count"], 1)
            self.assertEqual(data["totals"]["availability"], "UNAVAILABLE_NO_VALIDATED_SESSIONS")
            self.assertIsNone(data["totals"]["input_tokens"])
            self.assertIsNone(data["totals"]["paid_equivalent_usd"])

    def test_exact_decimal_paid_equivalent_and_cost_separation(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            data = self.run_projection(root, [self.row()])
            self.assertEqual(len(data["sessions"]), 1)
            session = data["sessions"][0]
            self.assertEqual(session["run_uid"], "gha:o/r:10:2")
            self.assertEqual(session["session_label"], "call-1")
            self.assertEqual(session["elapsed_seconds"], 0.5)
            self.assertEqual(session["source_sha"], "a" * 40)
            self.assertEqual(session["evidence_url"], "https://github.com/o/r/actions/runs/10")
            self.assertEqual(data["totals"]["paid_equivalent_usd"], 0.000022)
            self.assertEqual(data["totals"]["paid_equivalent_usd_exact"], "0.000022")
            self.assertEqual(session["billing_status"], "VERIFIED_NO_COST")
            self.assertEqual(set(session), {
                "session_label", "run_uid", "workflow", "source_sha", "observed_at",
                "provider", "model_id", "canonical_model_id", "input_tokens",
                "output_tokens", "elapsed_seconds", "outcome_status", "evidence_url",
                "validation_status", "basksweep_status", "publication_status",
                "billing_status", "pricing_id"
            })
            self.assertEqual(data["source_manifest"]["value_rounding"], "ROUND_HALF_UP")

    def test_positive_actual_cost_contradicts_verified_no_cost(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            data = self.run_projection(root, [
                self.row(),
                self.row(call_uid="call-2", cost_usd=0.01)
            ])
            self.assertEqual(len(data["sessions"]), 1)
            self.assertIn("not_established", data["coverage"][1]["evidence_status"])

    def test_ambiguous_price_identity_is_withheld(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            price = {
                "pricing_id": "price-a", "canonical_model_id": "provider/model-a",
                "input_usd_per_million": 1, "output_usd_per_million": 2
            }
            self.fixture(root, [price, dict(price, input_usd_per_million=9)])
            data = self.run_projection(root, [self.row()])
            self.assertEqual(data["sessions"], [])
            self.assertEqual(data["source_manifest"]["withheld_count"], 1)

    def test_decimal_rates_are_not_binary_float_accumulated(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root, [{
                "pricing_id": "price-a", "canonical_model_id": "provider/model-a",
                "input_usd_per_million": 0.1, "output_usd_per_million": 0.2
            }])
            data = self.run_projection(root, [self.row(tokens_in=1_000_000, tokens_out=1_000_000)])
            self.assertEqual(data["sessions"][0]["paid_equivalent_usd"], 0.3)

    def test_invalid_token_types_and_attempts_are_withheld(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            data = self.run_projection(root, [
                self.row(call_uid="bool-token", tokens_in=True),
                self.row(call_uid="float-token", tokens_out=5.0),
                self.row(call_uid="zero-attempt", run_attempt=0),
                self.row(call_uid="missing-pin", model_version_pin=None),
            ])
            self.assertEqual(data["sessions"], [])
            self.assertEqual(data["source_manifest"]["withheld_count"], 4)

    def test_aggregate_is_summed_exactly_then_rounded_once(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root, [{
                "pricing_id": "price-a", "canonical_model_id": "provider/model-a",
                "input_usd_per_million": 0.00001, "output_usd_per_million": 0
            }])
            rows = [self.row(call_uid=f"tiny-{i}", tokens_in=1, tokens_out=0)
                    for i in range(6)]
            data = self.run_projection(root, rows)
            self.assertEqual(len(data["sessions"]), 6)
            self.assertEqual(data["sessions"][0]["elapsed_seconds"], 0.5)
            self.assertEqual(data["totals"]["paid_equivalent_usd_exact"], "0.00000000006")
            self.assertEqual(data["totals"]["paid_equivalent_usd"], 0.0000000001)

    def test_duplicate_call_identity_is_counted_once(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            data = self.run_projection(root, [
                self.row(),
                self.row(tokens_in=999, call_uid="call-1")
            ])
            self.assertEqual(len(data["sessions"]), 1)
            self.assertEqual(data["sessions"][0]["input_tokens"], 12)
            self.assertEqual(data["coverage"][1]["evidence_status"], "duplicate_call_identity")

    def test_different_repository_run_attempts_do_not_collide(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            data = self.run_projection(root, [
                self.row(repository="o/r1"),
                self.row(repository="o/r2"),
                self.row(repository="o/r1", run_attempt=3),
            ])
            self.assertEqual(len(data["sessions"]), 3)


if __name__ == "__main__":
    unittest.main()
