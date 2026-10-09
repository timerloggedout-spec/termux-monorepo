import unittest

from ml.pipelines.recon07.registry import load_observations


class CatalogTest(unittest.TestCase):
    def test_unique_and_sized_for_review(self) -> None:
        rows = load_observations()
        keys = [(row.kind, row.number) for row in rows]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertGreaterEqual(sum(1 for row in rows if row.kind == "pr"), 45)
        self.assertGreaterEqual(sum(1 for row in rows if row.kind == "issue"), 8)
        self.assertTrue(all(row.action for row in rows))


if __name__ == "__main__":
    unittest.main()
