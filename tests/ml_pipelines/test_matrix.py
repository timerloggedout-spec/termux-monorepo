import unittest
from pathlib import Path

from ml_pipelines.matrix.load import load_matrix
from ml_pipelines.matrix.validate import validate_matrix

PATH = Path(__file__).resolve().parents[2] / "docs/ops/ISSUE-175-MATRIX.yaml"


class MatrixTests(unittest.TestCase):
    def test_valid(self):
        validate_matrix(load_matrix(PATH))


if __name__ == "__main__":
    unittest.main()
