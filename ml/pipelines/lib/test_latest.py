import unittest
from ml.pipelines.lib.latest import latest_session_path, session_paths

class LatestFixture(unittest.TestCase):
    def test_at_least_one(self):
        self.assertGreaterEqual(len(session_paths()), 1)

    def test_latest_is_newest_name(self):
        paths = session_paths()
        self.assertEqual(latest_session_path(), paths[-1])

    def test_latest_is_20260924(self):
        self.assertTrue(latest_session_path().name.startswith("session_20260924"))
