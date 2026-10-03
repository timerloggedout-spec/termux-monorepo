"""_v1_cache atomic-write durability: non-ASCII round-trip + no .tmp orphan.

Additive coverage for atomic_json_dump() in deepcli/deepcli/_v1_cache.py.
Invariant under test: a successful dump (a) preserves non-ASCII content
verbatim (ensure_ascii=False), (b) leaves exactly one file in the target
dir (the destination) with no .cache.*.tmp orphan, and (c) replaces an
existing file's contents wholesale (no stale tail from the old payload).
"""

import sys, pathlib, tempfile, unittest

sys.path.insert(0, str(pathlib.Path.home() / "deepcli"))
from deepcli._v1_cache import atomic_json_dump, read_session


class TestAtomicDumpDurability(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())

    def test_non_ascii_preserved(self):
        # ensure_ascii=False must keep multibyte chars literal on disk.
        p = self.tmp / "s.json"
        msg = [
            {"role": "user", "content": "caf\u00e9 \u2014 \u65e5\u672c\u8a9e \u2713"}
        ]
        atomic_json_dump(p, msg)
        raw = p.read_text(encoding="utf-8")
        self.assertIn("caf\u00e9", raw)
        self.assertIn("\u65e5\u672c\u8a9e", raw)
        # round-trips back to the identical object
        self.assertEqual(read_session(p), msg)

    def test_no_tmp_orphan_on_success(self):
        p = self.tmp / "s.json"
        atomic_json_dump(p, [{"role": "user", "content": "x" * 80}])
        leftovers = [
            f.name
            for f in self.tmp.iterdir()
            if f.name.startswith(".cache.") and f.name.endswith(".tmp")
        ]
        self.assertEqual(leftovers, [])
        self.assertEqual([f.name for f in self.tmp.iterdir()], ["s.json"])

    def test_overwrite_replaces_wholesale(self):
        # A shorter second payload must not leave a tail from the first.
        p = self.tmp / "s.json"
        atomic_json_dump(p, [{"role": "user", "content": "A" * 500}])
        atomic_json_dump(p, [{"role": "user", "content": "B"}])
        self.assertEqual(read_session(p), [{"role": "user", "content": "B"}])

    def test_creates_parent_dirs(self):
        p = self.tmp / "nested" / "deep" / "s.json"
        atomic_json_dump(p, [{"role": "user", "content": "y" * 50}])
        self.assertTrue(p.is_file())


if __name__ == "__main__":
    unittest.main()
