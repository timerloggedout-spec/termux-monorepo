"""_v1_cache I/O."""

import sys, time, tempfile, pathlib, unittest

sys.path.insert(0, str(pathlib.Path.home() / "deepcli"))
from deepcli._v1_cache import atomic_json_dump, read_session, last_msg_ts


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


class TestLastMsgTsNonPositive(unittest.TestCase):
    """last_msg_ts must ignore non-positive epoch values and fall through."""

    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())

    def _write(self, msgs):
        p = self.tmp / "s.json"
        atomic_json_dump(p, msgs)
        return p

    def test_zero_epoch_is_skipped(self):
        p = self._write([{"inserted_at": 0}, {"inserted_at": 1_700_000_000}])
        self.assertAlmostEqual(last_msg_ts(p), 1_700_000_000, delta=1)

    def test_negative_epoch_is_skipped(self):
        p = self._write([{"inserted_at": -5}, {"inserted_at": 1_700_000_000}])
        self.assertAlmostEqual(last_msg_ts(p), 1_700_000_000, delta=1)

    def test_all_nonpositive_returns_none(self):
        p = self._write([{"inserted_at": 0}, {"inserted_at": -1}])
        self.assertIsNone(last_msg_ts(p))

    def test_numeric_string_epoch(self):
        p = self._write([{"inserted_at": "1700000000"}])
        self.assertAlmostEqual(last_msg_ts(p), 1_700_000_000, delta=1)

    def test_malformed_iso_returns_none(self):
        p = self._write([{"inserted_at": "not-a-date"}])
        self.assertIsNone(last_msg_ts(p))

    def test_walks_back_to_freshest(self):
        p = self._write([{"inserted_at": 1_600_000_000}, {"ts": 1_700_000_000}])
        self.assertAlmostEqual(last_msg_ts(p), 1_700_000_000, delta=1)


if __name__ == "__main__":
    unittest.main()
