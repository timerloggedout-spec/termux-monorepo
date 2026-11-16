import unittest

from ml.pipelines.eval_lanes.app_probe import probe_blocked
from ml.pipelines.eval_lanes.registry import promote_gates


class EvalLaneTest(unittest.TestCase):
    def test_missing_app_credentials_block_probe_only(self) -> None:
        blocked, reason = probe_blocked(False, False)
        self.assertTrue(blocked)
        self.assertEqual(reason, "missing-app-credentials")
        blocked, reason = probe_blocked(True, True)
        self.assertFalse(blocked)
        self.assertEqual(reason, "configured")

    def test_advisory_reviewers_are_not_gates(self) -> None:
        self.assertEqual(promote_gates(), ("repo-gate", "termux-smoke"))


if __name__ == "__main__":
    unittest.main()
