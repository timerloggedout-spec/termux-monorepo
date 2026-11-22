import tempfile
import unittest
from pathlib import Path

from scripts.ci.issue_intake_coverage import audit, labels_for_template, labeled_event_workflows


class IssueIntakeCoverageTests(unittest.TestCase):
    def test_frontmatter_labels_are_extracted(self):
        path = Path("roadmap.md")
        self.assertEqual(
            labels_for_template(path, "---\nname: Example\nlabels: roadmap, completion\n---\nBody"),
            ["roadmap", "completion"],
        )

    def test_complete_fixture_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".github/ISSUE_TEMPLATE").mkdir(parents=True)
            (root / ".github/workflows").mkdir(parents=True)
            (root / "docs/ops").mkdir(parents=True)
            (root / ".github/ISSUE_TEMPLATE/example.yml").write_text(
                "name: Example\nlabels: example, task\n", encoding="utf-8"
            )
            (root / ".github/workflows/example.yml").write_text(
                "name: Example\non:\n  issues: [opened, labeled]\njobs:\n  check:\n    runs-on: ubuntu-latest\n",
                encoding="utf-8",
            )
            (root / "docs/ops/GITHUB-ISSUE-INTAKE-MAP.md").write_text(
                "`example.yml` `example` `task` `example.yml`", encoding="utf-8"
            )
            self.assertEqual(audit(root), [])

    def test_missing_template_label_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".github/ISSUE_TEMPLATE").mkdir(parents=True)
            (root / ".github/workflows").mkdir(parents=True)
            (root / "docs/ops").mkdir(parents=True)
            (root / ".github/ISSUE_TEMPLATE/example.yml").write_text(
                "name: Example\nlabels: example\n", encoding="utf-8"
            )
            (root / "docs/ops/GITHUB-ISSUE-INTAKE-MAP.md").write_text(
                "`example.yml`", encoding="utf-8"
            )
            errors = audit(root)
            self.assertTrue(any("label is absent" in error for error in errors))

    def test_labeled_issue_and_pull_request_workflows_are_discovered(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workflows = root / ".github/workflows"
            workflows.mkdir(parents=True)
            (workflows / "issue-label.yml").write_text(
                "name: Issue\non:\n  issues:\n    types: [labeled]\njobs:\n  run:\n    runs-on: ubuntu-latest\n",
                encoding="utf-8",
            )
            (workflows / "pr-label.yaml").write_text(
                "name: PR\non:\n  pull_request: [labeled]\njobs:\n  run:\n    runs-on: ubuntu-latest\n",
                encoding="utf-8",
            )
            self.assertEqual(
                labeled_event_workflows(root),
                ["issue-label.yml", "pr-label.yaml"],
            )


if __name__ == "__main__":
    unittest.main()
