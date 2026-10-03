"""_v1_delegate poll/active/cancel/journal coverage.

Offline coverage for the parts of _v1_delegate that do NOT spawn a
process. `assign()` forks a real `deepagent.py` child and is out of
scope here; the read-side protocol (poll/active/cancel) and the
append-only journal are pure filesystem operations and are covered.

Module paths are redirected to a tempdir in setUp so the tests never
touch the real ~/.deepcli/coordination tree.
"""

import json, sys, pathlib, tempfile, unittest


def _repo_root():
    """Walk up from this file to the dir containing deepcli/_v1_delegate.py."""
    here = pathlib.Path(__file__).resolve()
    for d in here.parents:
        if (d / "deepcli" / "_v1_delegate.py").exists():
            return d
    return pathlib.Path.home() / "deepcli"


sys.path.insert(0, str(_repo_root()))
from deepcli import _v1_delegate as d


class TestBootstrap(unittest.TestCase):
    def test_bootstrap_resolves_to_this_checkout(self):
        root = _repo_root()
        self.assertTrue((root / "deepcli" / "_v1_delegate.py").exists())
        self.assertIn(root, pathlib.Path(__file__).resolve().parents)


class _Isolated(unittest.TestCase):
    """Redirect the module's coordination paths into a tempdir."""

    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.status = self.tmp / "status"
        self.pids = self.tmp / "pids"
        self.status.mkdir()
        self.pids.mkdir()
        self.assign = self.tmp / "assignments.jsonl"
        self._saved = (d.STATUS, d.PIDS, d.ASSIGN)
        d.STATUS, d.PIDS, d.ASSIGN = self.status, self.pids, self.assign

    def tearDown(self):
        d.STATUS, d.PIDS, d.ASSIGN = self._saved


class TestPoll(_Isolated):
    def test_missing_returns_none(self):
        self.assertIsNone(d.poll("ghost"))

    def test_returns_last_row(self):
        (self.status / "kid.jsonl").write_text(
            json.dumps({"step": 1}) + "\n" + json.dumps({"step": 2}) + "\n"
        )
        self.assertEqual(d.poll("kid"), {"step": 2})

    def test_malformed_last_row_returns_none(self):
        (self.status / "kid.jsonl").write_text("{not json}\n")
        self.assertIsNone(d.poll("kid"))

    def test_empty_file_returns_none(self):
        (self.status / "kid.jsonl").write_text("")
        self.assertIsNone(d.poll("kid"))


class TestActive(_Isolated):
    def test_no_pids_returns_empty(self):
        self.assertEqual(d.active(), [])

    def test_live_pid_reported_alive(self):
        # our own pid is guaranteed alive for the duration of the call
        import os

        (self.pids / "me.pid").write_text(str(os.getpid()))
        rows = {r["child_id"]: r for r in d.active()}
        self.assertTrue(rows["me"]["alive"])
        self.assertEqual(rows["me"]["pid"], os.getpid())

    def test_dead_pid_reported_not_alive(self):
        (self.pids / "dead.pid").write_text("999999999")
        rows = {r["child_id"]: r for r in d.active()}
        self.assertFalse(rows["dead"]["alive"])
        self.assertIsNone(rows["dead"]["pid"])

    def test_garbage_pid_file_is_not_alive(self):
        (self.pids / "junk.pid").write_text("not-a-pid")
        rows = {r["child_id"]: r for r in d.active()}
        self.assertFalse(rows["junk"]["alive"])


class TestCancel(_Isolated):
    def test_unknown_child(self):
        self.assertEqual(d.cancel("ghost"), {"cancelled": False, "reason": "unknown"})

    def test_cancel_live_child(self):
        import os, signal

        (self.pids / "kid.pid").write_text(str(os.getpid()))
        sent = {}
        real_kill = os.kill

        def fake_kill(pid, sig):
            sent["pid"], sent["sig"] = pid, sig

        os.kill = fake_kill
        try:
            res = d.cancel("kid")
        finally:
            os.kill = real_kill
        self.assertTrue(res["cancelled"])
        self.assertEqual(sent["sig"], signal.SIGTERM)


class TestJournal(_Isolated):
    def test_appends_jsonl(self):
        d.journal({"op": "assign", "child": "kid"})
        d.journal({"op": "cancel", "child": "kid"})
        lines = self.assign.read_text().strip().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[1])["op"], "cancel")

    def test_default_str_serialises_non_json(self):
        d.journal({"op": "x", "when": object()})
        rec = json.loads(self.assign.read_text().strip())
        self.assertEqual(rec["op"], "x")


if __name__ == "__main__":
    unittest.main()
