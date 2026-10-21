import unittest
from ml.pipelines.command_center.drift import drift_report, overlapping

class DriftTest(unittest.TestCase):
    def test_file_overlap(self) -> None:
        a = {"number": 630, "files": ["dashboard.py"], "user": {"login": "google-labs-jules[bot]"}}
        b = {"number": 750, "files": ["dashboard.py"], "user": {"login": "google-labs-jules[bot]"}}
        self.assertTrue(overlapping(a, b))
        report = drift_report([a, b])
        self.assertIn((630, 750), report["collisions"])
    def test_self_not_overlap(self) -> None:
        a = {"number": 1, "files": ["a.py"]}
        self.assertFalse(overlapping(a, a))
