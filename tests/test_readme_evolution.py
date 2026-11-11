import unittest

from scripts.linguist.readme_evolution import compare_text, plan_file_budgets


class ReadmeEvolutionTests(unittest.TestCase):
    def test_compare_text_reports_symmetric_line_delta(self):
        result = compare_text("alpha\nbeta\ngamma\n", "alpha\ngamma\n")
        self.assertEqual(result["base_lines"], 3)
        self.assertEqual(result["candidate_lines"], 2)
        self.assertEqual(result["changed_base_lines"], 1)
        self.assertEqual(result["changed_candidate_lines"], 0)
        self.assertAlmostEqual(result["changed_line_percent"], 20.0)
        self.assertIsNone(result["quality_score"])

    def test_budget_plan_is_reproducible_for_same_seed(self):
        counts = {"README.md": 5000, "docs/linguist/guide.md": 1200}
        self.assertEqual(
            plan_file_budgets(counts, seed="abc123"),
            plan_file_budgets(counts, seed="abc123"),
        )

    def test_budget_plan_varies_by_seed_and_stays_bounded(self):
        counts = {f"docs/lane-{i}/README.md": 100_000 for i in range(12)}
        first = plan_file_budgets(counts, seed="seed-a")
        second = plan_file_budgets(counts, seed="seed-b")
        self.assertNotEqual(
            [row["selected_rate"] for row in first],
            [row["selected_rate"] for row in second],
        )
        for row in first:
            self.assertGreaterEqual(row["selected_rate"], 0.00063)
            self.assertLessEqual(row["selected_rate"], 0.00077)
            self.assertLessEqual(row["budget_tokens"], row["eligible_tokens"])

    def test_invalid_rate_is_rejected(self):
        with self.assertRaises(ValueError):
            plan_file_budgets({"README.md": 10}, seed="x", rate=0.08)

    def test_empty_content_has_zero_budget(self):
        row = plan_file_budgets({"README.md": 0}, seed="x")[0]
        self.assertEqual(row["budget_tokens"], 0)


if __name__ == "__main__":
    unittest.main()
