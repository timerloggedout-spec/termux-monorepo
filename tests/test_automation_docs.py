from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "ci" / "automation_docs.py"
SPEC = importlib.util.spec_from_file_location("automation_docs", MODULE_PATH)
automation_docs = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = automation_docs
SPEC.loader.exec_module(automation_docs)


class AutomationDocumentationTests(unittest.TestCase):
    def test_material_change_classifier_distinguishes_impact_levels(self) -> None:
        high = automation_docs.classify_material_paths(
            [".github/workflows/peer-review-orchestrator.yml"]
        )
        self.assertEqual(high["status"], "high-impact control-plane review required")
        self.assertEqual(high["high_impact_paths"], [".github/workflows/peer-review-orchestrator.yml"])

        docs = automation_docs.classify_material_paths(
            ["docs/proposals/active/actions-refinements/ITEMS.md"]
        )
        self.assertEqual(docs["status"], "documentation update required")
        self.assertEqual(docs["high_impact_paths"], [])

        unrelated = automation_docs.classify_material_paths(["README.md"])
        self.assertEqual(unrelated["status"], "no diagram impact")

    def test_classifier_rejects_unsafe_repository_paths(self) -> None:
        with self.assertRaises(ValueError):
            automation_docs.classify_material_paths(["../outside.yml"])
        with self.assertRaises(ValueError):
            automation_docs.classify_material_paths(["/absolute.yml"])

    def test_parse_workflow_captures_triggers_authority_and_pins(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workflow = root / ".github/workflows/example.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text(
                """name: Example\non:\n  pull_request:\n    types: [opened]\n  schedule:\n    - cron: '17 6 * * 1'\nconcurrency:\n  group: example\n  cancel-in-progress: true\npermissions:\n  contents: write\njobs:\n  verify:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8\n""",
                encoding="utf-8",
            )
            record = automation_docs.parse_workflow(workflow, root)
            self.assertEqual(record.name, "Example")
            self.assertEqual(record.triggers, ("pull_request", "schedule"))
            self.assertEqual(record.schedules, ("17 6 * * 1",))
            self.assertEqual(record.authority, "writer")
            self.assertEqual(record.jobs, ("verify",))
            self.assertEqual(
                record.action_pins,
                ("actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8",),
            )

    def test_rendered_catalog_is_stable_and_contains_current_control_plane(self) -> None:
        first_json, first_markdown, first_assets = automation_docs.rendered_outputs(ROOT)
        second_json, second_markdown, second_assets = automation_docs.rendered_outputs(ROOT)
        self.assertEqual(first_json, second_json)
        self.assertEqual(first_markdown, second_markdown)
        self.assertEqual(first_assets, second_assets)
        catalog = json.loads(first_json)
        self.assertEqual(catalog["schema_version"], 1)
        self.assertGreaterEqual(catalog["workflow_count"], 40)
        paths = {item["path"] for item in catalog["workflows"]}
        self.assertIn(".github/workflows/peer-review-orchestrator.yml", paths)
        self.assertIn(".github/workflows/gemini-review.yml", paths)
        assets = json.loads(first_assets)["assets"]
        self.assertGreaterEqual(len(assets), 8)
        for asset in assets:
            self.assertTrue(asset["source"].endswith(".mmd"))
            self.assertTrue(asset["render"].endswith(".png"))
            self.assertEqual(len(asset["source_sha256"]), 64)
            self.assertEqual(len(asset["render_sha256"]), 64)

    def test_check_detects_missing_or_stale_generated_outputs(self) -> None:
        original_json = automation_docs.OUTPUT_JSON
        original_markdown = automation_docs.OUTPUT_MD
        with tempfile.TemporaryDirectory() as temporary:
            generated = Path(temporary) / "generated"
            automation_docs.OUTPUT_JSON = generated / "catalog.json"
            automation_docs.OUTPUT_MD = generated / "catalog.md"
            self.assertFalse(automation_docs.check_outputs(ROOT))
            automation_docs.write_outputs(ROOT)
            self.assertTrue(automation_docs.check_outputs(ROOT))
            automation_docs.OUTPUT_JSON.write_text("{}\n", encoding="utf-8")
            self.assertFalse(automation_docs.check_outputs(ROOT))
        automation_docs.OUTPUT_JSON = original_json
        automation_docs.OUTPUT_MD = original_markdown


if __name__ == "__main__":
    unittest.main()
