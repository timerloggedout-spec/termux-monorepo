import json, os, subprocess, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location("quota_poll", os.path.join(ROOT, "scripts/quota_poll.py"))
_qp = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_qp)
multiplier = _qp.multiplier
from ml.pipelines.moneyball.quota_weights import quota_multiplier  # noqa: E402


class QuotaPollTest(unittest.TestCase):
    def test_multiplier(self):
        self.assertEqual(multiplier(None, 5, 0.5, 0.9), 1.0)
        self.assertEqual(multiplier(100, 95, 0.5, 0.9), 0.0)
        self.assertGreater(multiplier(500, 50, 0.5, 0.9), 1.0)
        self.assertLess(multiplier(500, 400, 0.5, 0.9), 1.0)

    def test_offline_run_emits_spine_records(self):
        with tempfile.TemporaryDirectory() as d:
            subprocess.check_call([sys.executable, os.path.join(ROOT, "scripts/quota_poll.py"), "--offline",
                                   "--registry", os.path.join(ROOT, "ops/quota/registry.json"), "--out", d])
            recs = [json.loads(l) for l in open(os.path.join(d, "quota-records.jsonl"))]
            self.assertTrue(recs)
            for r in recs:
                for k in ("resource_id", "item_id", "lane_id", "canonical_source", "evidence_hash", "horizon"):
                    self.assertIn(k, r)
                self.assertEqual(r["canonical_source"], r["source"]["url"])
            self.assertEqual(quota_multiplier("nope", {}), 1.0)


if __name__ == "__main__":
    unittest.main()
