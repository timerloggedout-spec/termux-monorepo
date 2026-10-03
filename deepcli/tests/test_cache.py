"""_v1_cache I/O."""

import json, sys, time, tempfile, pathlib, unittest

sys.path.insert(0, str(pathlib.Path.home() / "deepcli"))
from deepcli._v1_cache import atomic_json_dump, read_session, last_msg_ts, MIN_BYTES


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


class TestReadSession(unittest.TestCase):
    """Direct coverage of read_session's retry + tolerance branches."""

    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())

    def _write(self, name, obj):
        """Write obj as JSON, padded past MIN_BYTES so the size guard passes."""
        p = self.tmp / name
        text = json.dumps(obj)
        if len(text) < MIN_BYTES:
            text = text + " " * (MIN_BYTES - len(text))
        p.write_text(text)
        return p

    def test_dict_messages_key(self):
        """A dict wrapper with a 'messages' list is unwrapped."""
        p = self._write("d.json", {"messages": [{"role": "user"}]})
        self.assertEqual(read_session(p), [{"role": "user"}])

    def test_dict_alternate_keys(self):
        """Each of the known wrapper keys is honoured."""
        for key in ("conversation", "data", "history"):
            p = self._write(f"{key}.json", {key: [{"k": key}]})
            self.assertEqual(read_session(p), [{"k": key}])

    def test_dict_without_known_key_is_empty(self):
        """A dict with no recognisable message list yields [] (not raise)."""
        p = self._write("nokey.json", {"unrelated": [1, 2, 3]})
        self.assertEqual(read_session(p), [])

    def test_retry_recovers_after_partial_then_valid(self):
        """First read looks partial; the retry sees a valid file."""
        p = self.tmp / "race.json"
        p.write_text("[")  # below MIN_BYTES and unparseable
        payload = json.dumps([{"role": "user", "content": "recovered"}])

        real_sleep = time.sleep

        def fake_sleep(_s):
            real_sleep(0)
            p.write_text(payload)  # writer finishes during the retry window

        time.sleep = fake_sleep
        try:
            self.assertEqual(
                read_session(p, retry_sleep=0.01),
                [{"role": "user", "content": "recovered"}],
            )
        finally:
            time.sleep = real_sleep

    def test_retry_on_invalid_json_then_valid(self):
        """First read raises JSONDecodeError; retry sees valid JSON."""
        p = self.tmp / "bad.json"
        p.write_text("x" * (MIN_BYTES + 10))  # big enough, still invalid JSON
        payload = json.dumps([{"role": "assistant", "content": "ok"}])

        real_sleep = time.sleep

        def fake_sleep(_s):
            real_sleep(0)
            p.write_text(payload)

        time.sleep = fake_sleep
        try:
            self.assertEqual(
                read_session(p, retry_sleep=0.01),
                [{"role": "assistant", "content": "ok"}],
            )
        finally:
            time.sleep = real_sleep

    def test_persistent_partial_returns_empty(self):
        """A file that stays partial across both attempts yields [] (no raise)."""
        p = self.tmp / "stuck.json"
        p.write_text("[")  # never becomes valid
        self.assertEqual(read_session(p, retry_sleep=0.01), [])


if __name__ == "__main__":
    unittest.main()
