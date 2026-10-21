import contextlib, io, json, os, subprocess, sys, tempfile, unittest
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location("quota_poll", os.path.join(ROOT, "scripts/quota_poll.py"))
_qp = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_qp)
multiplier = _qp.multiplier
from ml.pipelines.moneyball.quota_weights import quota_multiplier  # noqa: E402


class QuotaPollTest(unittest.TestCase):
    def test_openrouter_reads_documented_free_request_counter_only(self):
        payload = {"data": {
            "limit_remaining": 0.42,
            "effective_budget": {"remaining_usd": 0.25},
            "free_model_daily_requests": {"used": 12, "limit": 50, "remaining": 38},
        }, "openrouter_metadata": {"private": "must not escape"}}
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "not-a-real-key"}), \
             patch.object(_qp, "_get", return_value=payload):
            result = _qp.openrouter_reader(None)
        self.assertEqual(result, {"used": 12, "limit": 50, "elapsed": None, "reset": "UTC midnight"})
        self.assertNotIn("private", json.dumps(result))

    def test_openrouter_rejects_missing_or_malformed_counter(self):
        cases = [
            {"data": {"free_model_daily_requests": {"used": 1, "limit": 50}}},
            {"data": {"free_model_daily_requests": {"used": True, "limit": 50, "remaining": 49}}},
            {"data": {"free_model_daily_requests": {"used": float("nan"), "limit": 50, "remaining": 49}}},
            {"data": {"free_model_daily_requests": {"used": -1, "limit": 50, "remaining": 51}}},
            {"data": {"free_model_daily_requests": {"used": "1", "limit": 50, "remaining": 49}}},
            {"data": {"free_model_daily_requests": {"used": 1, "limit": 50, "remaining": 48}}},
            {"data": {"free_model_daily_requests": {"count": 1, "limit": 50, "remaining": 49}}},
            {"data": {"free_model_daily_requests": {"used": 1, "limit": -1, "remaining": 0}}},
            {"data": {"limit_remaining": 50, "usage_daily": 1}},
            {"openrouter_metadata": {"free_model_daily_requests": {"used": 1, "limit": 50, "remaining": 49}}},
        ]
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "not-a-real-key"}):
            for payload in cases:
                with self.subTest(payload=payload), patch.object(_qp, "_get", return_value=payload):
                    self.assertIsNone(_qp.openrouter_reader(None))

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


    def test_public_mode_never_exports_private_values_or_reader_logs(self):
        def private_reader(now):
            print("secret-canary used=714239")
            print("private-stderr-canary", file=sys.stderr)
            return {"used": 714239, "limit": 714240, "reset": "private-reset-canary",
                    "extra": {"token": "secret-canary"}}
        with tempfile.TemporaryDirectory() as d:
            output = os.path.join(d, "public")
            stdout, stderr = io.StringIO(), io.StringIO()
            with patch.object(_qp, "LIVE", {"openrouter.free_models": private_reader}), \
                 patch.object(_qp, "MULTI", []), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                self.assertEqual(_qp.main(["--public", "--registry", os.path.join(ROOT, "ops/quota/registry.json"), "--out", output]), 0)
            self.assertEqual(os.listdir(output), ["quota-public-status.json"])
            text = open(os.path.join(output, "quota-public-status.json")).read()
            combined = text + stdout.getvalue() + stderr.getvalue()
            for private in ("714239", "714240", "secret-canary", "private-reset-canary", "private-stderr-canary", "routing_multiplier", "evidence_hash"):
                self.assertNotIn(private, combined)
            row = next(r for r in json.loads(text)["readings"] if r["resource_id"] == "openrouter.free_models")
            self.assertEqual(row["status"], "private_preflight")
            self.assertEqual(set(row), {"resource_id", "provider", "status", "observed_at"})

    def test_public_mode_refuses_stale_private_output_directory(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "quota-records.jsonl"), "w") as f:
                f.write("private-canary")
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                _qp.main(["--public", "--offline", "--out", d])

    def test_public_workflow_uploads_only_status_projection(self):
        from pathlib import Path
        workflow = (Path(ROOT) / ".github/workflows/vercel-quota-probe.yml").read_text()
        self.assertIn("scripts/quota_poll.py --public", workflow)
        self.assertIn("path: quota-out/quota-public-status.json", workflow)
        self.assertNotIn("r['used']", workflow)
        self.assertNotIn("path: quota-out/\n", workflow)


if __name__ == "__main__":
    unittest.main()
