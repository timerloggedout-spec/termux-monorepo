from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/autonomous-merge-eligibility.yml"


class AutonomousMergeWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_workflow_is_valid_yaml(self):
        parsed = yaml.safe_load(self.text)
        self.assertIsInstance(parsed, dict)
        self.assertIn("jobs", parsed)

    def test_workflow_is_opt_in_and_current_sha_aware(self):
        self.assertIn("const optInLabel = 'autonomous-merge';", self.text)
        self.assertIn("head_sha: ${pr.head.sha}", self.text)
        self.assertIn("sha: pr.head.sha", self.text)

    def test_workflow_targets_only_staging_and_same_repository_heads(self):
        self.assertIn("pr.base.ref !== 'master-staging'", self.text)
        self.assertIn("pr.head.repo?.full_name !== `${owner}/${repo}`", self.text)
        self.assertIn("pr.draft", self.text)

    def test_workflow_requires_review_threads_and_checks_to_be_clean(self):
        self.assertIn("no current-SHA independent review", self.text)
        self.assertIn("current-SHA changes requested", self.text)
        self.assertIn("unresolved review thread", self.text)
        self.assertIn("checks not eligible", self.text)

    def test_workflow_excludes_sensitive_and_self_modifying_paths(self):
        for path in (
            ".github/workflows/",
            ".github/actions/",
            "docs/proposals/",
            "config/",
            "scripts/ci/",
        ):
            with self.subTest(path=path):
                self.assertIn(path, self.text)

    def test_workflow_isolates_known_external_statuses_from_repository_gates(self):
        self.assertIn("app !== 'gitlab'", self.text)
        self.assertIn("!name.startsWith('ci/gitlab/')", self.text)
        self.assertIn("Ignored external status context", self.text)

    def test_workflow_emits_a_marker_before_an_attempted_squash_merge(self):
        marker_index = self.text.index("<!-- autonomous-merge-eligibility -->")
        merge_index = self.text.index("github.rest.pulls.merge")
        self.assertLess(marker_index, merge_index)
        self.assertIn("merge_method: 'squash'", self.text)


if __name__ == "__main__":
    unittest.main()
