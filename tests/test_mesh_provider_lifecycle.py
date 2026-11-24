import tempfile
import unittest
from pathlib import Path

from scripts.ci.validate_mesh_provider_lifecycle import (
    RETIRED_WORKFLOWS,
    ROOT,
    validate_lifecycle_sources,
    workflow_errors,
)


class MeshProviderLifecycleTests(unittest.TestCase):
    def test_existing_authorities_and_retired_workflows_satisfy_contract(self):
        self.assertEqual(validate_lifecycle_sources(ROOT), [])

    def test_retired_workflow_requires_dispatch_only_trigger(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workflow = root / "retired.yml"
            workflow.write_text(
                "name: Active Fly deploy\non:\n  push:\njobs:\n  deploy:\n    steps:\n      - run: echo deploy\n",
                encoding="utf-8",
            )
            errors = workflow_errors("Fly.io", "retired.yml", root)
            self.assertTrue(any("name must carry RETIRED" in item for item in errors))
            self.assertTrue(any("triggers must equal workflow_dispatch" in item for item in errors))

    def test_retired_workflow_rejects_provider_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workflow = root / "retired.yml"
            workflow.write_text(
                "name: RETIRED — Fly.io\non:\n  workflow_dispatch:\njobs:\n  retirement:\n    steps:\n      - run: fly deploy\n",
                encoding="utf-8",
            )
            errors = workflow_errors("Fly.io", "retired.yml", root)
            self.assertTrue(any("active provider operation remains" in item for item in errors))

    def test_retirement_workflow_inventory_is_bounded(self):
        self.assertEqual(len(RETIRED_WORKFLOWS["Fly.io"]), 2)
        self.assertEqual(len(RETIRED_WORKFLOWS["Koyeb"]), 1)


if __name__ == "__main__":
    unittest.main()
