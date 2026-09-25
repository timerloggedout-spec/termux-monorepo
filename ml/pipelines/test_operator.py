import unittest
from ml.pipelines.operator.issue175 import ISSUE
from ml.pipelines.operator.matrix import PRIORITY
from ml.pipelines.operator.receipt import receipt

class OperatorTest(unittest.TestCase):
    def test_issue(self) -> None:
        self.assertEqual(ISSUE, 175)
        self.assertGreaterEqual(len(PRIORITY), 4)
    def test_receipt(self) -> None:
        row = receipt(head_sha="abc", base_sha="def", state="PASS", decision="KEEP", reason="extract")
        self.assertEqual(row["issue"], 175)

if __name__ == "__main__":
    unittest.main()
