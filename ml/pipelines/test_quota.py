import unittest
from ml.pipelines.actions.quota import skip_comment

class QuotaTest(unittest.TestCase):
    def test_comment(self) -> None:
        self.assertTrue(skip_comment().startswith("skip-reason:"))
