import unittest
from ml.pipelines.viz.matrix import render_matrix

class MatrixTest(unittest.TestCase):
    def test_p0_present(self) -> None:
        rows = render_matrix()
        self.assertTrue(any(r["p"] == 0 for r in rows))

if __name__ == "__main__":
    unittest.main()
