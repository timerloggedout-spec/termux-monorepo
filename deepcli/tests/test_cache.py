"""_v1_cache I/O."""
import json, sys, time, tempfile, pathlib, unittest
sys.path.insert(0, str(pathlib.Path.home() / "deepcli"))
from deepcli._v1_cache import atomic_json_dump, read_session, last_msg_ts, _coerce_ts

class TestCache(unittest.TestCase):
    def setUp(self): self.tmp = pathlib.Path(tempfile.mkdtemp())
    def test_write_read(self):
        p = self.tmp/"s.json"
        atomic_json_dump(p, [{"role":"user","content":"hi"},{"role":"assistant","content":"ok"}])
        self.assertEqual(len(read_session(p)), 2)
    def test_missing(self): self.assertEqual(read_session(self.tmp/"nope.json"), [])
    def test_small(self):
        p = self.tmp/"t.json"; p.write_text("[")
        self.assertEqual(read_session(p, retry_sleep=0.01), [])
    def test_ts_epoch(self):
        p = self.tmp/"s.json"; now = time.time()
        atomic_json_dump(p, [{"inserted_at": now}]); self.assertAlmostEqual(last_msg_ts(p), now, delta=1)
    def test_ts_iso(self):
        p = self.tmp/"s.json"
        atomic_json_dump(p, [{"inserted_at": "2026-10-03T00:00:00Z"}])
        self.assertGreater(last_msg_ts(p), 1_700_000_000)


class TestCoerceTs(unittest.TestCase):
    def test_none(self):        self.assertIsNone(_coerce_ts(None))
    def test_epoch(self):      self.assertEqual(_coerce_ts(1700000000), 1700000000.0)
    def test_nonpositive(self):self.assertIsNone(_coerce_ts(0)); self.assertIsNone(_coerce_ts(-5))
    def test_numstring(self):  self.assertEqual(_coerce_ts("1700000000"), 1700000000.0)
    def test_iso_z(self):      self.assertGreater(_coerce_ts("2026-10-03T00:00:00Z"), 1_700_000_000)
    def test_iso_naive(self):  self.assertIsNotNone(_coerce_ts("2026-10-03T00:00:00"))
    def test_bad_string(self): self.assertIsNone(_coerce_ts("not-a-date"))
    def test_bad_type(self):   self.assertIsNone(_coerce_ts([1,2]))

if __name__ == "__main__": unittest.main()
