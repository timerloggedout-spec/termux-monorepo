"""_v1_events scan helpers: message_text, scan_session, scan_dir.

Offline coverage for the parts of _v1_events not exercised by
test_events.py (which only covers extract()).
"""

import json, sys, pathlib, tempfile, unittest


def _repo_root():
    """Walk up from this file to the dir containing deepcli/_v1_events.py."""
    here = pathlib.Path(__file__).resolve()
    for d in here.parents:
        if (d / "deepcli" / "_v1_events.py").exists():
            return d
    return pathlib.Path.home() / "deepcli"


sys.path.insert(0, str(_repo_root()))
from deepcli._v1_events import message_text, scan_session, scan_dir


class TestBootstrap(unittest.TestCase):
    def test_bootstrap_resolves_to_this_checkout(self):
        root = _repo_root()
        self.assertTrue((root / "deepcli" / "_v1_events.py").exists())
        self.assertIn(root, pathlib.Path(__file__).resolve().parents)


class TestMessageText(unittest.TestCase):
    def test_content_only(self):
        self.assertEqual(message_text({"content": "hi"}), "hi")

    def test_thinking_included(self):
        self.assertEqual(
            message_text({"content": "a", "thinking_content": "b"}), "a\nb"
        )

    def test_fragments_joined(self):
        m = {"content": "", "fragments": [{"content": "x"}, {"content": "y"}]}
        self.assertEqual(message_text(m), "x\ny")

    def test_skips_non_string_and_non_dict_fragments(self):
        m = {"content": None, "fragments": ["nope", {"content": 5}, {"content": "z"}]}
        self.assertEqual(message_text(m), "z")

    def test_empty(self):
        self.assertEqual(message_text({}), "")


class TestScanSession(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())

    def _write(self, name, obj):
        p = self.tmp / name
        p.write_text(json.dumps(obj))
        return p

    def test_index_role_symbols(self):
        p = self._write(
            "s.json",
            [
                {"role": "USER", "content": "plain"},
                {"role": "Assistant", "content": "gpgconf --kill gpg-agent"},
            ],
        )
        recs = scan_session(p)
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]["idx"], 1)
        self.assertEqual(recs[0]["role"], "assistant")
        self.assertIn("KILL_AGENT", recs[0]["symbols"])

    def test_non_dict_entries_skipped(self):
        p = self._write(
            "s.json", ["x", 3, {"role": "user", "content": "cat ~/.gnupg/.2fa-pass"}]
        )
        recs = scan_session(p)
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]["idx"], 2)
        self.assertIn("CRED_READ", recs[0]["symbols"])

    def test_missing_file_returns_empty(self):
        self.assertEqual(scan_session(self.tmp / "nope.json"), [])

    def test_non_list_root_returns_empty(self):
        p = self._write("s.json", {"messages": []})
        self.assertEqual(scan_session(p), [])


class TestScanDir(unittest.TestCase):
    def test_yields_only_nonempty_sessions(self):
        tmp = pathlib.Path(tempfile.mkdtemp())
        (tmp / "a.json").write_text(json.dumps([{"role": "user", "content": "plain"}]))
        (tmp / "b.json").write_text(
            json.dumps([{"role": "user", "content": "pkill gpg-agent"}])
        )
        got = dict(scan_dir(tmp))
        self.assertNotIn("a", got)
        self.assertIn("b", got)


if __name__ == "__main__":
    unittest.main()
