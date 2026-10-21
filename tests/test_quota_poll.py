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
        self.assertEqual(result, {"used": 12, "limit": 50, "remaining": 38, "elapsed": None,
                                  "reset": None,
                                  "extra": {"source": "official OpenRouter GET /api/v1/key"}})
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
                    "reset": "UTC midnight", "extra": {"source": "official OpenRouter GET /api/v1/key"},
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


def test_openrouter_reader_validates_real_response_shape(monkeypatch):
    from datetime import datetime, timezone
    monkeypatch.setenv("OPENROUTER_API_KEY", "offline-dummy")
    payload = {"data": {"free_model_daily_requests": {"used": 4, "limit": 100, "remaining": 96}}}
    monkeypatch.setattr(_qp, "_get", lambda *args, **kwargs: payload)
    assert _qp.openrouter_reader(datetime.now(timezone.utc))["used"] == 4
    for used, limit in [(True, 100), (1, False), (float("nan"), 100),
                        (1, float("inf")), (-1, 100), (1, 0)]:
        payload["data"]["free_model_daily_requests"] = {"used": used, "limit": limit, "remaining": 96}
        assert _qp.openrouter_reader(datetime.now(timezone.utc)) is None


def test_official_snapshot_never_borrows_registry_limit(tmp_path, monkeypatch):
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({"services": [{
        "id": "openrouter.free_models", "provider": "openrouter", "lane": "model",
        "metric": "free requests", "unit": "requests/day", "window": "UTC day",
        "reset": "UTC midnight", "zone": "UTC", "source": "https://example.test/docs",
        "limit": 999, "planned_use": {"safety": 0.9},
    }]}))
    monkeypatch.setattr(_qp, "LIVE", {"openrouter.free_models": lambda now: {
        "used": 4, "extra": {"source": "official OpenRouter GET /api/v1/key"},
    }})
    monkeypatch.setattr(_qp, "MULTI", [])
    out = tmp_path / "out"
    _qp.main(["--registry", str(registry), "--out", str(out)])
    snapshot = json.loads((out / "provider-quota-state.json").read_text())
    assert snapshot["status"] == "unknown"
    assert snapshot["limit"] is None
