"""_v1_cache I/O."""

import sys, time, tempfile, pathlib, unittest

sys.path.insert(0, str(pathlib.Path.home() / "deepcli"))
from deepcli._v1_cache import atomic_json_dump, read_session, last_msg_ts, is_fresh


class TestCache(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())

    def test_write_read(self):
        p = self.tmp / "s.json"
        atomic_json_dump(
            p,
            [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "ok"}],
        )
        self.assertEqual(len(read_session(p)), 2)

    def test_missing(self):
        self.assertEqual(read_session(self.tmp / "nope.json"), [])

    def test_small(self):
        p = self.tmp / "t.json"
        p.write_text("[")
        self.assertEqual(read_session(p, retry_sleep=0.01), [])

    def test_ts_epoch(self):
        p = self.tmp / "s.json"
        now = time.time()
        atomic_json_dump(p, [{"inserted_at": now}])
        self.assertAlmostEqual(last_msg_ts(p), now, delta=1)

    def test_ts_iso(self):
        p = self.tmp / "s.json"
        atomic_json_dump(p, [{"inserted_at": "2026-10-03T00:00:00Z"}])
        self.assertGreater(last_msg_ts(p), 1_700_000_000)


class TestIsFresh(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())

    def test_missing_file_is_not_fresh(self):
        self.assertFalse(is_fresh(self.tmp / "nope.json"))

    def test_no_timestamp_is_not_fresh(self):
        p = self.tmp / "s.json"
        atomic_json_dump(p, [{"role": "user", "content": "no ts key here"}])
        self.assertFalse(is_fresh(p))

    def test_recent_epoch_is_fresh(self):
        p = self.tmp / "s.json"
        now = time.time()
        atomic_json_dump(p, [{"inserted_at": now}])
        self.assertTrue(is_fresh(p))

    def test_stale_beyond_threshold_is_not_fresh(self):
        p = self.tmp / "s.json"
        atomic_json_dump(p, [{"inserted_at": time.time() - 10000}])
        self.assertFalse(is_fresh(p, threshold_s=120))


if __name__ == "__main__":
    unittest.main()
