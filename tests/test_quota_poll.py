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


    def test_official_openrouter_quota_snapshot_and_unknown_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            registry = os.path.join(d, "registry.json")
            out = os.path.join(d, "out")
            os.makedirs(out)
            with open(registry, "w") as handle:
                json.dump({
                    "services": [{
                        "id": "openrouter.free_models", "provider": "openrouter",
                        "lane": "model", "metric": "free requests", "unit": "requests/day",
                        "window": "UTC day", "reset": "UTC midnight", "zone": "UTC",
                        "source": "https://openrouter.ai/docs/api-reference/limits",
                        "planned_use": {"safety": 0.9},
                    }]
                }, handle)
            original_live, original_multi = _qp.LIVE, _qp.MULTI
            try:
                _qp.LIVE = {"openrouter.free_models": lambda now: {
                    "used": 70, "limit": 100, "remaining": 30, "elapsed": None,
                    "reset": "UTC midnight", "extra": {"source": "official"},
                }}
                _qp.MULTI = []
                _qp.main(["--registry", registry, "--out", out])
                snapshot = json.load(open(os.path.join(out, "provider-quota-state.json")))
                self.assertEqual(snapshot["status"], "live")
                self.assertEqual(snapshot["used"], 70)
                self.assertEqual(snapshot["limit"], 100)
                self.assertEqual(snapshot["remaining"], 30)
                weights = json.load(open(os.path.join(out, "routing-weights.json")))
                self.assertIn("openrouter", weights["multipliers"])

                _qp.LIVE = {}
                _qp.main(["--registry", registry, "--out", out])
                snapshot = json.load(open(os.path.join(out, "provider-quota-state.json")))
                self.assertEqual(snapshot["status"], "unknown")
                weights = json.load(open(os.path.join(out, "routing-weights.json")))
                self.assertNotIn("openrouter", weights["multipliers"])
            finally:
                _qp.LIVE, _qp.MULTI = original_live, original_multi



if __name__ == "__main__":
    unittest.main()
