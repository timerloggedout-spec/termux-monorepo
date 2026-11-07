import unittest
from ml.pipelines.operator.hub import TRACKING_URL, REPO_TRACKING_DOC_URL, PR_DISPOSITION_URL

class HubTest(unittest.TestCase):
    def test_ssot_urls(self) -> None:
        self.assertTrue(TRACKING_URL.endswith("/ops/tracking/tracking.json"))
        self.assertTrue(REPO_TRACKING_DOC_URL.endswith("/docs/ops/REPO-TRACKING.md"))
        self.assertTrue(PR_DISPOSITION_URL.endswith("/docs/ops/generated/lane-matrix-status.md"))

if __name__ == "__main__":
    unittest.main()
