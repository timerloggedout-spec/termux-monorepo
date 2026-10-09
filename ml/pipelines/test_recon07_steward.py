import unittest

from ml.pipelines.recon07.steward import next_actions, report


class StewardTest(unittest.TestCase):
    def test_report_does_not_write(self) -> None:
        payload = report()
        self.assertFalse(payload["writes"])
        self.assertEqual(payload["rules_failed"], [])
        self.assertGreaterEqual(len(next_actions()), 8)
        self.assertIn("EXTRACT", payload["catalog_prs"])
        self.assertIn("NEED_EVIDENCE", payload["catalog_issues"])


if __name__ == "__main__":
    unittest.main()
