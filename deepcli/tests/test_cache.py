"""_v1_cache I/O."""

import sys, time, tempfile, pathlib, unittest


def _repo_root():
    """Walk up from this test file to the checkout that owns deepcli/.

    The previous bootstrap inserted ``$HOME/deepcli`` unconditionally, so a
    worktree run imported the MAIN checkout's ``_v1_cache`` instead of the
    worktree's. Resolve ``__file__``-relative first, fall back to the old
    location only when no checkout root is found.
    """
    here = pathlib.Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "deepcli" / "_v1_cache.py").is_file():
            return parent
    return pathlib.Path.home() / "deepcli"


sys.path.insert(0, str(_repo_root()))
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

    def test_fresh_recent(self):
        p = self.tmp / "s.json"
        atomic_json_dump(p, [{"inserted_at": time.time()}])
        self.assertTrue(is_fresh(p, threshold_s=120))

    def test_fresh_stale(self):
        p = self.tmp / "s.json"
        atomic_json_dump(p, [{"inserted_at": time.time() - 10_000}])
        self.assertFalse(is_fresh(p, threshold_s=120))

    def test_fresh_no_ts(self):
        p = self.tmp / "s.json"
        atomic_json_dump(p, [{"role": "user", "content": "hi"}])
        self.assertFalse(is_fresh(p))

    def test_fresh_missing_file(self):
        self.assertFalse(is_fresh(self.tmp / "nope.json"))

    def test_bootstrap_is_checkout_relative(self):
        """_repo_root() must resolve to a directory that owns deepcli/."""
        root = _repo_root()
        self.assertTrue((root / "deepcli" / "_v1_cache.py").is_file())


if __name__ == "__main__":
    unittest.main()
