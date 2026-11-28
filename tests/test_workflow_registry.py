from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "ci" / "workflow_registry.py"
SPEC = importlib.util.spec_from_file_location("workflow_registry", MODULE_PATH)
workflow_registry = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = workflow_registry
SPEC.loader.exec_module(workflow_registry)


class WorkflowRegistryTests(unittest.TestCase):
    def test_parses_event_filters_dispatch_inputs_permissions_and_job_guards(self) -> None:
        source = """\
name: Dispatch fixture
on:
  push:
    branches: [main, release/**]
    paths-ignore: [docs/**]
  issue_comment:
    types: [created, edited]
  workflow_dispatch:
    inputs:
      target:
        description: Deployment target
        required: true
        type: choice
        options: [staging, production]
        default: staging
permissions:
  contents: read
concurrency:
  group: workflow-${{ github.ref }}
  cancel-in-progress: false
jobs:
  deploy:
    if: github.ref == 'refs/heads/main'
    needs: [validate]
    permissions:
      contents: write
      deployments: write
    steps:
      - uses: actions/checkout@0123456789012345678901234567890123456789
      - uses: actions/setup-python@v5
  validate:
    if: contains(github.event.comment.body, '/deploy')
    runs-on: ubuntu-latest
    steps:
      - run: echo validate
  reusable:
    uses: example/automation/.github/workflows/reusable.yml@abcdefabcdefabcdefabcdefabcdefabcdefabcd
"""
        record = workflow_registry.parse_workflow_text(source, ".github/workflows/dispatch.yml")
        self.assertEqual(record["events"], ["issue_comment", "push", "workflow_dispatch"])
        self.assertEqual(record["event_config"]["push"]["branches"], ["main", "release/**"])
        self.assertEqual(record["event_config"]["push"]["paths-ignore"], ["docs/**"])
        self.assertEqual(record["event_config"]["issue_comment"]["types"], ["created", "edited"])
        self.assertEqual(record["workflow_dispatch_inputs"]["target"]["options"], ["staging", "production"])
        self.assertTrue(record["workflow_dispatch_inputs"]["target"]["required"])
        self.assertEqual(record["permissions"]["workflow"], {"contents": "read"})
        self.assertEqual(record["authority_basis"], "declared GitHub workflow/job permissions")
        self.assertEqual(record["permissions"]["jobs"]["deploy"], {"contents": "write", "deployments": "write"})
        self.assertEqual(record["job_selectors"]["deploy"]["if"], "github.ref == 'refs/heads/main'")
        self.assertEqual(record["job_selectors"]["validate"]["if"], "contains(github.event.comment.body, '/deploy')")
        self.assertEqual(record["job_selectors"]["deploy"]["needs"], ["validate"])
        self.assertEqual(record["concurrency"]["cancel-in-progress"], "false")
        self.assertEqual(record["action_refs"], [
            "actions/checkout@0123456789012345678901234567890123456789",
            "actions/setup-python@v5",
            "example/automation/.github/workflows/reusable.yml@abcdefabcdefabcdefabcdefabcdefabcdefabcd",
        ])
        self.assertEqual(record["action_pins"], [
            "actions/checkout@0123456789012345678901234567890123456789",
            "example/automation/.github/workflows/reusable.yml@abcdefabcdefabcdefabcdefabcdefabcdefabcd",
        ])
        self.assertEqual(record["action_pins"], ["actions/checkout@0123456789012345678901234567890123456789"])

    def test_job_permissions_override_workflow_permissions_for_authority(self) -> None:
        source = """\\
name: Scoped permissions
on: [push]
permissions:
  contents: write
jobs:
  verify:
    permissions:
      contents: read
    steps:
      - run: echo verify
"""
        record = workflow_registry.parse_workflow_text(source, ".github/workflows/scoped.yml")
        self.assertEqual(record["source_authority"], "read-only-or-advisory")

    def test_classifies_declared_non_advisory_write_scopes_as_writers(self) -> None:
        source = """\\
name: Action control
on: [workflow_dispatch]
permissions:
  actions: write
jobs:
  cancel:
    steps:
      - run: echo control
"""
        record = workflow_registry.parse_workflow_text(source, ".github/workflows/action-control.yml")
        self.assertEqual(record["source_authority"], "writer")

    def test_parses_sequence_event_syntax(self) -> None:
        source = "name: Compact\non: [push, workflow_dispatch]\njobs:\n  test:\n    runs-on: ubuntu-latest\n"
        record = workflow_registry.parse_workflow_text(source, ".github/workflows/compact.yml")
        self.assertEqual(record["events"], ["push", "workflow_dispatch"])
        self.assertEqual(record["event_config"], {"push": {}, "workflow_dispatch": {}})

    def test_rejects_invalid_yaml_with_workflow_path(self) -> None:
        source = "name: Broken\non: [push\njobs: {}\n"
        with self.assertRaisesRegex(ValueError, r"broken\\.yml.*YAML"):
            workflow_registry.parse_workflow_text(source, ".github/workflows/broken.yml")

    def test_git_blob_sha_matches_git_object_format(self) -> None:
        self.assertEqual(workflow_registry.git_blob_sha(b"name: x\n"), "595a3aeae4904608eee47f61ba721453a70460b0")

    def test_build_index_reconciles_catalog_and_records_source_authority_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workflow_dir = root / ".github/workflows"
            workflow_dir.mkdir(parents=True)
            source = """\
name: Visibility change
on:
  push:
    branches: [master]
    paths: [ops/requests/project-visibility-public.yaml]
permissions:
  contents: read
jobs:
  publish:
    permissions:
      contents: write
    steps:
      - run: gh api --method PATCH repos/example/repo -F private=false
"""
            (workflow_dir / "project-repository-visibility.yml").write_text(source, encoding="utf-8")
            catalog = {
                "source_fingerprint": "fingerprint-1",
                "workflows": [{
                    "path": ".github/workflows/project-repository-visibility.yml",
                    "name": "Visibility change",
                    "triggers": ["push"],
                    "authority": "read-only-or-advisory",
                    "jobs": ["publish"],
                }],
            }
            index = workflow_registry.build_index(root, catalog)
            self.assertEqual(index["reconciliation"]["status"], "IN_SYNC")
            item = index["workflows"][0]
            self.assertEqual(item["source_authority"], "writer")
            self.assertEqual(item["catalog_authority"], "read-only-or-advisory")
            self.assertTrue(item["authority_conflict"])
            self.assertEqual(item["event_config"]["push"]["paths"], ["ops/requests/project-visibility-public.yaml"])
            self.assertEqual(item["permissions"]["jobs"]["publish"]["contents"], "write")

    def test_write_and_check_generate_stable_v2_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workflow_dir = root / ".github/workflows"
            catalog_dir = root / "docs/ops/generated"
            workflow_dir.mkdir(parents=True)
            catalog_dir.mkdir(parents=True)
            (workflow_dir / "one.yml").write_text(
                "name: One\\non: [push]\\njobs: {}\\n", encoding="utf-8"
            )
            (catalog_dir / "automation-workflow-catalog.json").write_text(
                json.dumps({"source_fingerprint": "abc", "workflows": [{"path": ".github/workflows/one.yml", "authority": "read-only-or-advisory"}]}),
                encoding="utf-8",
            )
            workflow_registry.write_outputs(root)
            self.assertTrue(workflow_registry.check_outputs(root))
            output = json.loads((catalog_dir / "workflow-event-index.json").read_text(encoding="utf-8"))
            self.assertEqual(output["schema_version"], "workflow-event-index/v2")
            (catalog_dir / "workflow-event-index.json").write_text("{}\\n", encoding="utf-8")
            self.assertFalse(workflow_registry.check_outputs(root))

    def test_build_index_reports_directory_catalog_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".github/workflows").mkdir(parents=True)
            (root / ".github/workflows/actual.yml").write_text("name: Actual\non: [push]\njobs: {}\n", encoding="utf-8")
            catalog = {"source_fingerprint": "x", "workflows": [{"path": ".github/workflows/stale.yml", "authority": "writer"}]}
            index = workflow_registry.build_index(root, catalog)
            self.assertEqual(index["reconciliation"]["status"], "DRIFT")
            self.assertEqual(index["reconciliation"]["missing_from_catalog"], [".github/workflows/actual.yml"])
            self.assertEqual(index["reconciliation"]["missing_from_directory"], [".github/workflows/stale.yml"])


if __name__ == "__main__":
    unittest.main()
