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


class TestLastMsgTs(unittest.TestCase):
    """last_msg_ts walks backwards and honours TS_KEYS priority."""

    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())

    def _write(self, msgs):
        p = self.tmp / "s.json"
        atomic_json_dump(p, msgs)
        return p

    def test_last_message_wins(self):
        # Two timestamped messages: the LAST one's ts must be returned.
        p = self._write([{"inserted_at": 1700000000}, {"inserted_at": 1700009999}])
        self.assertAlmostEqual(last_msg_ts(p), 1700009999.0, delta=1)

    def test_key_priority_inserted_at_over_timestamp(self):
        # One message carrying two keys: TS_KEYS order must pick inserted_at.
        p = self._write([{"timestamp": 1700000000, "inserted_at": 1700009999}])
        self.assertAlmostEqual(last_msg_ts(p), 1700009999.0, delta=1)

    def test_uncoercible_last_falls_back(self):
        # Last message has no usable ts; walk back to the earlier one.
        p = self._write([{"inserted_at": 1700000000}, {"role": "user"}])
        self.assertAlmostEqual(last_msg_ts(p), 1700000000.0, delta=1)

    def test_non_dict_message_skipped(self):
        # A non-dict trailing entry must be skipped, not crash.
        p = self._write([{"inserted_at": 1700000000}, "garbage"])
        self.assertAlmostEqual(last_msg_ts(p), 1700000000.0, delta=1)

    def test_no_timestamp_anywhere(self):
        p = self._write([{"role": "user"}, {"role": "assistant"}])
        self.assertIsNone(last_msg_ts(p))


if __name__ == "__main__":
    unittest.main()
