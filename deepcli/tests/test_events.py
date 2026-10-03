"""_v1_events symbols + session scanning."""

import json, sys, pathlib, tempfile, unittest

sys.path.insert(0, str(pathlib.Path.home() / "deepcli"))
from deepcli._v1_events import extract, message_text, scan_session


class TestEvents(unittest.TestCase):
    def test_kill(self):
        self.assertIn("KILL_AGENT", extract("gpgconf --kill gpg-agent"))

    def test_read(self):
        self.assertIn("CRED_READ", extract("cat ~/.gnupg/.2fa-pass"))

    def test_write(self):
        self.assertIn("CRED_WRITE", extract("echo pw > ~/.gnupg/.2fa-pass"))

    def test_empty(self):
        self.assertEqual(extract(""), [])


class TestMessageText(unittest.TestCase):
    """message_text joins content-bearing fields in a fixed order."""

    def test_content_only(self):
        self.assertEqual(message_text({"content": "hi"}), "hi")

    def test_ignores_empty_and_non_string(self):
        self.assertEqual(message_text({"content": "", "text": None, "ts": 5}), "")

    def test_order_content_then_thinking_then_text(self):
        m = {"content": "a", "thinking_content": "b", "text": "c"}
        self.assertEqual(message_text(m), "a\nb\nc")

    def test_fragments_fallback(self):
        # content empty after API refresh; reply lives in fragments[].content
        m = {"content": "", "fragments": [{"content": "from-frag"}]}
        self.assertEqual(message_text(m), "from-frag")

    def test_fragments_malformed_ignored(self):
        m = {"fragments": ["not-a-dict", {"content": 7}, {"content": "ok"}]}
        self.assertEqual(message_text(m), "ok")


class TestScanSession(unittest.TestCase):
    def _write(self, obj):
        d = tempfile.mkdtemp()
        p = pathlib.Path(d) / "s.json"
        p.write_text(json.dumps(obj))
        return str(p)

    def test_missing_file_returns_empty(self):
        self.assertEqual(scan_session("/nonexistent/nope.json"), [])

    def test_non_list_returns_empty(self):
        self.assertEqual(scan_session(self._write({"messages": []})), [])

    def test_only_symbol_bearing_messages(self):
        msgs = [
            {"role": "user", "content": "hello there"},
            {"role": "assistant", "content": "gpgconf --kill gpg-agent"},
        ]
        recs = scan_session(self._write(msgs))
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]["idx"], 1)
        self.assertEqual(recs[0]["role"], "assistant")
        self.assertIn("KILL_AGENT", recs[0]["symbols"])

    def test_role_defaults_and_lowercased(self):
        msgs = [{"content": "cat ~/.gnupg/.2fa-pass"}]
        recs = scan_session(self._write(msgs))
        self.assertEqual(recs[0]["role"], "?")

    def test_ts_prefers_inserted_at(self):
        msgs = [{"content": "gh2fa", "inserted_at": 111, "timestamp": 222}]
        self.assertEqual(scan_session(self._write(msgs))[0]["ts"], 111)

    def test_non_dict_entries_skipped(self):
        msgs = ["junk", {"content": "gh2fa"}]
        recs = scan_session(self._write(msgs))
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]["idx"], 1)


if __name__ == "__main__":
    unittest.main()
