import unittest
from pathlib import Path

from ml_pipelines.ingest.snapshot import load_snapshot

FIX = Path(__file__).resolve().parents[2] / "ml_pipelines/fixtures/ops-snapshot.json"


class SnapshotTests(unittest.TestCase):
    def test_loads_fixture(self):
        snap = load_snapshot(FIX)
        self.assertEqual(snap.repo, "timerloggedout-spec/termux-monorepo")
        self.assertGreaterEqual(len(snap.prs), 1)
        self.assertGreaterEqual(len(snap.issues), 1)

    def test_no_comment_bodies(self):
        snap = load_snapshot(FIX)
        blob = str(snap.as_dict())
        self.assertNotIn("raw_body", blob)


if __name__ == "__main__":
    unittest.main()
