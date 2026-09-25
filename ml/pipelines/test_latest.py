import unittest
from ml.pipelines.lib.latest import latest_session_path

class LatestTest(unittest.TestCase):
    def test_exists(self) -> None:
        path = latest_session_path()
        self.assertTrue(path.name.startswith("session_"))
        self.assertTrue(path.exists())

if __name__ == "__main__":
    unittest.main()
