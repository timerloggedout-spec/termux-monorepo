import unittest
from ml.pipelines.replay.ledger import ledger_row

class LedgerTest(unittest.TestCase):
    def test_mode(self) -> None:
        row = ledger_row({"master_sha": "a", "lane_counts": {"EXTRACT": 1}})
        self.assertEqual(row["mode"], "observe")
        self.assertEqual(row["issue"], 175)

if __name__ == "__main__":
    unittest.main()
