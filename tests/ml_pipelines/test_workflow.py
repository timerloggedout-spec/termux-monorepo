import unittest
from pathlib import Path

WF = Path(__file__).resolve().parents[2] / ".github/workflows/ml-pipelines.yml"


class WorkflowTests(unittest.TestCase):
    def test_read_only_permissions(self):
        text = WF.read_text(encoding="utf-8")
        self.assertIn("permissions:", text)
        self.assertIn("contents: read", text)
        self.assertNotIn("contents: write", text)
        self.assertIn("persist-credentials: false", text)


if __name__ == "__main__":
    unittest.main()
