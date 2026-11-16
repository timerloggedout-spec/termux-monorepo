import json
import unittest
from io import StringIO
from unittest.mock import patch

from ml.pipelines.cli import main
from ml.pipelines.eval_lanes.registry import all_contracts, promote_gates
from ml.pipelines.recon09.catalog import all_observations
from ml.pipelines.recon09.connectors import connector_report
from ml.pipelines.recon09.drift import drift_report
from ml.pipelines.recon09.rules import INVALID_PARKING, VALID_LANES, classify_open_pr
from ml.pipelines.recon09.steward import report


class Recon09LiveTest(unittest.TestCase):
    def test_stamp_does_not_promote_observer(self) -> None:
        payload = report()
        self.assertEqual(payload["version"], "0.9.0")
        self.assertEqual(payload["product_sha"], "8d36f149214f4a147932188bc424e7c29b8de444")
        self.assertEqual(payload["observer_tip"], "c15fbdf6207a540276e8c959738e4444b67afbb6")
        self.assertFalse(payload["observer_tip_promotable"])
        self.assertFalse(payload["writes"])
        self.assertTrue(payload["keep_pipelines"])
        self.assertFalse(payload["locks"]["coderabbit_is_gate"])
        self.assertFalse(payload["locks"]["pulse_comment_175"])
        self.assertFalse(payload["locks"]["force_push_master"])
        self.assertEqual(payload["open_prs_observed"], 205)
        self.assertFalse(payload["catalog_is_full_board"])

    def test_catalog_matches_rules_and_vocab(self) -> None:
        rows = all_observations()
        self.assertGreaterEqual(len(rows), 70)
        self.assertLessEqual(len(rows), 90)
        for row in rows:
            self.assertIn(row.lane, VALID_LANES)
            self.assertTrue(INVALID_PARKING.isdisjoint(row.reasons))
            self.assertNotIn(row.lane, INVALID_PARKING)
            if row.kind != "pr":
                continue
            lane, reasons, action = classify_open_pr(
                number=row.number,
                base=row.base,
                login=row.login,
                title=row.title,
                draft="draft" in row.reasons,
            )
            self.assertEqual(row.lane, lane, row.number)
            self.assertEqual(row.action, action, row.number)
            self.assertEqual(row.reasons, reasons, row.number)

    def test_wholesale_and_staging_locks(self) -> None:
        by_number = {row.number: row for row in all_observations() if row.kind == "pr"}
        for number in (432, 682, 787):
            if number in by_number:
                self.assertEqual(by_number[number].lane, "EXTRACT")
                self.assertEqual(by_number[number].action, "extract-only-keep-pipelines")
        if 48 in by_number:
            self.assertEqual(by_number[48].action, "never-retarget")

    def test_connectors_carry_no_secrets(self) -> None:
        payload = connector_report()
        self.assertFalse(payload["secrets"])
        blob = json.dumps(payload)
        self.assertNotIn("ghp_", blob)
        self.assertNotIn("github_pat_", blob)
        self.assertNotIn("BEGIN PRIVATE", blob)
        names = {row["name"] for row in payload["connectors"]}
        self.assertIn("github", names)
        self.assertIn("vercel", names)
        vercel = next(row for row in payload["connectors"] if row["name"] == "vercel")
        self.assertNotEqual(vercel["lane"], "CANDIDATE")

    def test_native_gate_is_the_only_promote_authority(self) -> None:
        self.assertEqual(promote_gates(), ("repo-gate", "termux-smoke"))
        for contract in all_contracts():
            self.assertFalse(contract.retains_secret_values)
            self.assertFalse(contract.retains_private_bodies)

    def test_cli_live_and_frozen_status(self) -> None:
        buf = StringIO()
        with patch("sys.stdout", buf):
            code = main(["live"])
        self.assertEqual(code, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["version"], "0.9.0")
        buf = StringIO()
        with patch("sys.stdout", buf):
            code = main(["status"])
        self.assertEqual(code, 0)
        status = json.loads(buf.getvalue())
        self.assertEqual(status["version"], "0.8.0")
        drift = drift_report()
        self.assertFalse(drift["writes"])
        self.assertIsInstance(drift["lane_or_action_changes"], list)


if __name__ == "__main__":
    unittest.main()
