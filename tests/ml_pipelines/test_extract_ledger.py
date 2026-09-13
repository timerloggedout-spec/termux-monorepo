import unittest

from ml_pipelines.pipelines.extract_ledger import run


class ExtractLedgerTests(unittest.TestCase):
    def test_closed_264_and_open_263(self):
        snap = {
            "prs": [
                {"number": 263, "title": "Manus/context relationship graph"},
                {"number": 432, "title": "feat(ml): observe-mode"},
            ],
            "issues": [{"number": 502}],
        }
        result = run(snap)
        by_n = {row["number"]: row for row in result["parents"]}
        self.assertTrue(by_n[263]["open"])
        self.assertFalse(by_n[264]["open"])
        self.assertEqual(by_n[264]["expected"], "SUPERSEDED")
        self.assertEqual(result["authority"], "extract-only")


if __name__ == "__main__":
    unittest.main()
