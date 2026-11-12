import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.linguist.readme_evolution import _git_show, compare_text, plan_file_budgets


class ReadmeEvolutionTests(unittest.TestCase):
    def test_compare_text_reports_symmetric_line_delta(self):
        result = compare_text("alpha\nbeta\ngamma\n", "alpha\ngamma\n")
        self.assertEqual(result["base_lines"], 3)
        self.assertEqual(result["candidate_lines"], 2)
        self.assertEqual(result["changed_base_lines"], 1)
        self.assertEqual(result["changed_candidate_lines"], 0)
        self.assertAlmostEqual(result["changed_line_percent"], 20.0)
        self.assertIsNone(result["quality_score"])

    def test_compare_text_preserves_crlf_byte_counts(self):
        result = compare_text("a\\r\\n", "a\\n")
        self.assertEqual(result["base_utf8_bytes"], 3)
        self.assertEqual(result["candidate_utf8_bytes"], 2)
        self.assertEqual(result["unchanged_lines"], 1)
        self.assertEqual(result["changed_line_percent"], 0.0)

    def test_git_show_preserves_raw_blob_line_endings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Readme Evolution Test"], cwd=root, check=True)
            subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=root, check=True)
            (root / "README.md").write_bytes(b"a\\r\\n")
            subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "fixture"], cwd=root, check=True, capture_output=True)
            self.assertEqual(_git_show(root, "HEAD", "README.md"), "a\\r\\n")

    def test_git_show_rejects_unsafe_refs_and_paths(self):
        with self.assertRaises(ValueError):
            _git_show(Path("."), "--help", "README.md")
        with self.assertRaises(ValueError):
            _git_show(Path("."), "HEAD", "../README.md")

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

    def test_file_order_does_not_change_seeded_plan(self):
        left = {"z/README.md": 8000, "a/README.md": 9000}
        right = {"a/README.md": 9000, "z/README.md": 8000}
        self.assertEqual(
            plan_file_budgets(left, seed="stable-order"),
            plan_file_budgets(right, seed="stable-order"),
        )

    def test_invalid_rate_is_rejected(self):
        with self.assertRaises(ValueError):
            plan_file_budgets({"README.md": 10}, seed="x", rate=0.08)

    def test_empty_content_has_zero_budget(self):
        row = plan_file_budgets({"README.md": 0}, seed="x")[0]
        self.assertEqual(row["budget_tokens"], 0)


if __name__ == "__main__":
    unittest.main()
