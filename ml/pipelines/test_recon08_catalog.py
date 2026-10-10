import unittest

from ml.pipelines.recon08.catalog import all_observations
from ml.pipelines.recon08.rules import VALID_LANES, classify_open_pr


class CatalogTest(unittest.TestCase):
    def test_frozen_matches_rules(self) -> None:
        rows = all_observations()
        self.assertGreaterEqual(len(rows), 70)
        numbers = [row.number for row in rows]
        self.assertEqual(len(numbers), len(set(numbers)))
        for row in rows:
            self.assertIn(row.lane, VALID_LANES)
            if row.kind == "pr":
                lane, reasons, action = classify_open_pr(
                    number=row.number, base=row.base, login=row.login, title=row.title
                )
                self.assertEqual(row.lane, lane)
                self.assertEqual(row.reasons, reasons)
                self.assertEqual(row.action, action)

    def test_known_rows(self) -> None:
        by_num = {row.number: row for row in all_observations()}
        self.assertEqual(by_num[48].action, "never-retarget")
        self.assertEqual(by_num[184].reasons, ("names-only",))
        self.assertEqual(by_num[772].lane, "SUPERSEDE")
        self.assertFalse(by_num[175].action == "pulse-comment")


if __name__ == "__main__":
    unittest.main()
