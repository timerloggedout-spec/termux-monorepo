import unittest

from scripts.ci.workflow_surface_policy import classify_path, classify_paths, normalize_path


class WorkflowSurfacePolicyTests(unittest.TestCase):
    def test_docs_only_paths_are_docs_without_execution_surfaces(self):
        result = classify_paths(
            [
                "docs/proposals/active/actions-refinements/ITEMS.md",
                "README.md",
                ".github/ISSUE_TEMPLATE/bug.md",
            ]
        )
        self.assertEqual(
            result,
            {"automation": False, "source": False, "tests": False, "docs": True},
        )

    def test_workflow_and_composite_action_paths_are_automation(self):
        self.assertTrue(classify_path(".github/workflows/repo-gate.yml")["automation"])
        self.assertTrue(classify_path(".github/actions/model-router/action.yml")["automation"])
        self.assertTrue(classify_path("scripts/ci/workflow_surface_policy.py")["automation"])

    def test_source_and_test_paths_stay_distinct(self):
        source = classify_path("deepcli/session_manager.py")
        test = classify_path("tests/test_session_manager.py")
        self.assertTrue(source["source"])
        self.assertFalse(source["tests"])
        self.assertTrue(test["tests"])
        self.assertFalse(test["source"])

    def test_mixed_paths_set_all_relevant_flags(self):
        result = classify_paths(
            [
                ".github/workflows/repo-gate.yml",
                "deepcli/runner.py",
                "tests/test_runner.py",
                "docs/ops/guide.md",
            ]
        )
        self.assertEqual(
            result,
            {"automation": True, "source": True, "tests": True, "docs": True},
        )

    def test_rejects_path_traversal_and_absolute_paths(self):
        for value in ("../.github/workflows/repo-gate.yml", "/etc/passwd", "./docs/guide.md"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    normalize_path(value)

    def test_backslashes_normalize_but_do_not_escape_repository(self):
        self.assertEqual(normalize_path("docs\\ops\\guide.md"), "docs/ops/guide.md")
        with self.assertRaises(ValueError):
            normalize_path("docs\\..\\secret.txt")


if __name__ == "__main__":
    unittest.main()
