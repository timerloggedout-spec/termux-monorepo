import json
import unittest
from io import StringIO
from unittest.mock import patch

from ml.pipelines.cli import main
from ml.pipelines.recon08.budget import budget_report
from ml.pipelines.recon08.roles import OBSERVER_TIP, PRODUCT_SHA, VERSION
from ml.pipelines.recon08.steward import report


class StampTest(unittest.TestCase):
    def test_stamp_does_not_promote_observer(self) -> None:
        payload = report()
        self.assertEqual(payload["version"], VERSION)
        self.assertEqual(payload["product_sha"], PRODUCT_SHA)
        self.assertEqual(payload["observer_tip"], OBSERVER_TIP)
        self.assertFalse(payload["observer_tip_promotable"])
        self.assertFalse(payload["writes"])
        self.assertTrue(payload["keep_pipelines"])
        self.assertFalse(payload["locks"]["coderabbit_is_gate"])
        self.assertFalse(payload["locks"]["pulse_comment_175"])

    def test_budget_is_not_a_gate(self) -> None:
        over = budget_report(101)
        self.assertFalse(over["within_advisory_budget"])
        self.assertFalse(over["is_promote_gate"])

    def test_cli_recon_and_existing_status(self) -> None:
        buf = StringIO()
        with patch("sys.stdout", buf):
            code = main(["recon"])
        self.assertEqual(code, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["version"], "0.8.0")
        buf = StringIO()
        with patch("sys.stdout", buf):
            code = main(["status"])
        self.assertEqual(code, 0)
        status = json.loads(buf.getvalue())
        self.assertEqual(status["issue"], 175)
        self.assertEqual(status["version"], "0.8.0")
        self.assertFalse(status["observer_tip_promotable"])


if __name__ == "__main__":
    unittest.main()
