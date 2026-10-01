import unittest
from ml.pipelines.viz.mermaid import dag_mermaid

class MermaidTest(unittest.TestCase):
    def test_contains_recon(self) -> None:
        text = dag_mermaid()
        self.assertIn("recon_lanes", text)

if __name__ == "__main__":
    unittest.main()
