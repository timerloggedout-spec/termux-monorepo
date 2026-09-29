import unittest
from ml.pipelines.viz.command_center import emit_center

class VizCenterTest(unittest.TestCase):
    def test_mermaid(self) -> None:
        out = emit_center({"master_sha": "8d36f149", "prs": []})
        self.assertIn("flowchart LR", out["mermaid"])
        self.assertEqual(out["kind"], "command-center")
