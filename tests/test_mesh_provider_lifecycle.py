import json
import tempfile
import unittest
from pathlib import Path

from scripts.ci.validate_mesh_provider_lifecycle import (
    ROOT,
    REGISTRY,
    validate_registry,
)


class MeshProviderLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_master_registry_satisfies_lifecycle_contract(self):
        self.assertEqual(validate_registry(self.document, ROOT), [])

    def test_retired_provider_cannot_remain_execution_eligible(self):
        self.document["providers"][0]["state"] = "retired"
        self.document["providers"][0]["retired_workflows"] = []
        self.assertTrue(any("execution_eligible=false" in item for item in validate_registry(self.document, ROOT)))

    def test_duplicate_provider_ids_fail(self):
        self.document["providers"].append(dict(self.document["providers"][0]))
        self.assertTrue(any("duplicate provider id" in item for item in validate_registry(self.document, ROOT)))

    def test_retired_workflow_requires_retired_name_and_dispatch_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workflow = root / ".github/workflows/retired.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text(
                "name: Active Fly deploy\non:\n  push:\njobs:\n  deploy:\n    steps:\n      - run: echo deploy\n",
                encoding="utf-8",
            )
            provider = {
                "id": "fly",
                "state": "retired",
                "execution_eligible": False,
                "retired_workflows": [".github/workflows/retired.yml"],
            }
            errors = validate_registry(
                {"schema": "mesh.provider-lifecycle/v1", "providers": [provider]},
                root,
            )
            self.assertTrue(any("name must carry RETIRED" in item for item in errors))
            self.assertTrue(any("triggers must equal workflow_dispatch" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
