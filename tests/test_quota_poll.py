import contextlib, io, json, os, subprocess, sys, tempfile, unittest
from datetime import datetime, timezone
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


    def test_unobserved_records_carry_no_observation_time(self):
        svc = {"id": "example.requests", "provider": "example", "lane": "ops",
               "metric": "requests", "unit": "requests", "window": "daily",
               "reset": "n/a", "zone": "UTC", "source": "https://example.com/docs",
               "limit": 100, "planned_use": {"safety": 0.9}}
        now = datetime(2026, 10, 27, 12, 0, tzinfo=timezone.utc)
        rec = _qp.record(svc, None, now)
        self.assertIsNone(rec["observed_at"])
        self.assertEqual(rec["horizon"], "H1")
        live = _qp.record(svc, {"used": 3, "limit": 100}, now)
        self.assertEqual(live["observed_at"], now.isoformat())
        self.assertEqual(live["horizon"], "H0")
        self.assertEqual(live["evidence_status"], "confirmed")

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
            self.assertEqual(set(row), {"resource_id", "provider", "status", "observed_at", "horizon", "evidence_status"})
            # Convergence with the readings contract: a genuine live read is
            # H0/confirmed evidence even though its status stays withheld.
            self.assertEqual((row["horizon"], row["evidence_status"]), ("H0", "confirmed"))
            self.assertIsNotNone(row["observed_at"])
            unobserved = next(r for r in json.loads(text)["readings"] if r["resource_id"] == "vercel.deployments")
            self.assertEqual(unobserved["status"], "unknown")
            self.assertIsNone(unobserved["observed_at"])
            self.assertEqual((unobserved["horizon"], unobserved["evidence_status"]), ("H1", "attributed_claim"))

    def test_readings_snapshot_converts_projection_to_dashboard_contract(self):
        services = [
            {"id": "openrouter.free_models", "provider": "openrouter", "lane": "model",
             "source": "https://openrouter.ai/docs", "limit": None, "unit": "requests/day"},
            {"id": "example.requests", "provider": "example", "lane": "ops",
             "source": "https://example.com/docs", "limit": 100, "unit": "requests"},
            {"id": "plain.requests", "provider": "plain", "lane": "ops",
             "source": "internal-note", "limit": 5, "unit": "requests"},
        ]
        now = datetime(2026, 10, 27, 12, 0, tzinfo=timezone.utc)
        public = _qp.public_snapshot(services, {"openrouter.free_models": {"used": 714239}}, now)
        snap = _qp.readings_snapshot(public, services)
        self.assertEqual(snap["schema"], "3l0.quota-readings.v1")
        self.assertEqual(snap["generated_at"], public["generated_at"])
        self.assertIn("not a live quota feed", snap["source"])
        self.assertNotIn("714239", json.dumps(snap))
        rows = {r["resource_id"]: r for r in snap["readings"]}
        # The projection withholds real statuses: no row may gain one, and no
        # used/reset value may be invented (openrouter pin included).
        for r in rows.values():
            self.assertEqual(r["status"], "unknown")
            self.assertIsNone(r["used"])
            self.assertIsNone(r["reset"])
            self.assertIn("observed_at", r)
        live = rows["openrouter.free_models"]
        self.assertEqual((live["horizon"], live["evidence_status"]), ("H0", "confirmed"))
        self.assertEqual(live["observed_at"], now.isoformat())
        self.assertIsNone(live["limit"])  # registry documents no limit; none inferred
        unobserved = rows["example.requests"]
        self.assertEqual((unobserved["horizon"], unobserved["evidence_status"]), ("H1", "attributed_claim"))
        self.assertIsNone(unobserved["observed_at"])
        self.assertEqual(unobserved["limit"], 100)  # documented entitlement, not a balance
        self.assertEqual(rows["plain.requests"]["evidence_status"], "early_signal")

    def test_readings_snapshot_rederives_evidence_for_pre_convergence_artifacts(self):
        services = [{"id": "example.requests", "provider": "example", "lane": "ops",
                     "source": "https://example.com/docs", "limit": 100, "unit": "requests"}]
        legacy = {"schema": "quota-public-status/v1", "generated_at": "2026-10-22T00:00:00+00:00",
                  "readings": [{"resource_id": "example.requests", "provider": "example",
                                "status": "private_preflight", "observed_at": "2026-10-22T00:00:00+00:00"}]}
        row = _qp.readings_snapshot(legacy, services)["readings"][0]
        self.assertEqual((row["horizon"], row["evidence_status"]), ("H0", "confirmed"))

    def test_readings_snapshot_rejects_non_projection_input(self):
        with self.assertRaises(ValueError):
            _qp.readings_snapshot({"schema": "3l0.quota-readings.v1", "readings": []}, [])
        with self.assertRaises(ValueError):
            _qp.readings_snapshot(["not-a-dict"], [])

    def test_from_public_cli_writes_only_the_readings_snapshot(self):
        artifact = {"schema": "quota-public-status/v1", "generated_at": "2026-10-27T12:00:00+00:00",
                    "readings": [{"resource_id": "openrouter.free_models", "provider": "openrouter",
                                  "status": "private_preflight", "observed_at": "2026-10-27T12:00:00+00:00",
                                  "horizon": "H0", "evidence_status": "confirmed", "used": 714239}]}
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "quota-public-status.json")
            with open(src, "w") as f:
                json.dump(artifact, f)
            output = os.path.join(d, "converted")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(_qp.main(["--from-public", src, "--registry",
                                           os.path.join(ROOT, "ops/quota/registry.json"), "--out", output]), 0)
            self.assertEqual(os.listdir(output), ["quota-status.json"])
            text = open(os.path.join(output, "quota-status.json")).read()
            self.assertNotIn("714239", text + stdout.getvalue())
            snap = json.loads(text)
            row = next(r for r in snap["readings"] if r["resource_id"] == "openrouter.free_models")
            self.assertEqual((row["status"], row["used"], row["reset"]), ("unknown", None, None))

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
