import unittest
from pathlib import Path

from ml_pipelines.io import load_simple_yaml
from ml_pipelines.pipelines.gitmodules_audit import run

PATH = Path(__file__).resolve().parents[2] / "docs/ops/GITMODULES-AUDIT-503.yaml"


class GitmodulesAuditTests(unittest.TestCase):
    def test_vendors_live_and_no_mutate(self):
        doc = load_simple_yaml(PATH)
        self.assertEqual(doc.get("issue"), 503)
        extras = []
        # load_simple_yaml flattens lists poorly; stage uses snapshot extras
        snap = {
            "gitmodules": [
                {"path": "multi-ai-cli/vendors/CLIProxyAPI", "status": "LIVE"},
                {"path": "multi-ai-cli/vendors/Chapito", "status": "LIVE"},
            ]
        }
        result = run(snap)
        self.assertEqual(result["live"], 2)
        self.assertFalse(result["mutate_gitmodules"])


if __name__ == "__main__":
    unittest.main()
