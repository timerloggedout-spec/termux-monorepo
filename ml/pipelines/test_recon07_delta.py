import unittest

from ml.pipelines.recon07.delta import disagreements, summary


class DeltaTest(unittest.TestCase):
    def test_wholesale_agrees_and_nothing_is_promotable(self) -> None:
        rows = {row["number"]: row for row in disagreements()}
        self.assertEqual(rows[432]["catalog"], "EXTRACT")
        self.assertEqual(rows[432]["classifier"], "EXTRACT")
        self.assertTrue(rows[432]["agree"])
        self.assertEqual(rows[48]["catalog"], "EXTRACT")
        self.assertEqual(rows[48]["classifier"], "NEED_EVIDENCE")
        self.assertFalse(rows[48]["agree"])
        self.assertEqual(summary()["promotable"], [])


if __name__ == "__main__":
    unittest.main()
