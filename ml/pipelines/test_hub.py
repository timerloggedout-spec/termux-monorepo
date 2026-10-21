import unittest
from ml.pipelines.operator.hub import ISSUE_URL

class HubTest(unittest.TestCase):
    def test_url(self) -> None:
        self.assertTrue(ISSUE_URL.endswith("/issues/175"))

if __name__ == "__main__":
    unittest.main()
