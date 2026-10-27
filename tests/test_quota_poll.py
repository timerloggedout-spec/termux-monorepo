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
            self.assertEqual(row["horizon"], "H0")
            self.assertEqual(row["evidence_status"], "confirmed")
            self.assertIsNotNone(row["observed_at"])

    def test_public_snapshot_speaks_the_dashboard_evidence_contract(self):
        """G-12c (1): the poller's published projection must be consumable by
        quota-evidence.js readingView — observed_at / horizon H0 /
        evidence_status confirmed plus a status from the panel's own set —
        or Needs attention stays unreachable from the poller path. Values
        (used/limit/reset) are never exported; exhaustion is claimed only
        at the documented limit, safety-zone pressure is watch."""
        def svc(sid, lane="ops", limit=100):
            return {"id": sid, "provider": "example", "lane": lane,
                    "source": "https://example.com/docs", "limit": limit,
                    "planned_use": {"safety": 0.9}}
        services = [svc("example.ok"), svc("example.watch"), svc("example.full"),
                    svc("vercel.deployments"), svc("example.nolimit", limit=None),
                    svc("example.model", lane="model"), svc("example.unseen")]
        readings = {"example.ok": {"used": 10, "limit": 100},
                    "example.watch": {"used": 85, "limit": 100},
                    "example.full": {"used": 100, "limit": 100},
                    "vercel.deployments": {"used": 100},
                    "example.nolimit": {"used": 3},
                    "example.model": {"used": 714239, "limit": 714240}}
        now = datetime(2026, 10, 27, 12, 0, tzinfo=timezone.utc)
        snap = _qp.public_snapshot(services, readings, now)
        self.assertEqual(snap["schema"], "quota-public-status/v2")
        rows = {r["resource_id"]: r for r in snap["readings"]}
        self.assertEqual(rows["example.ok"]["status"], "ok")
        self.assertEqual(rows["example.watch"]["status"], "watch")
        self.assertEqual(rows["example.full"]["status"], "exhausted")
        self.assertEqual(rows["vercel.deployments"]["status"], "cap_tripped")
        # observed but unclassifiable: honest unknown, still H0/confirmed
        self.assertEqual(rows["example.nolimit"]["status"], "unknown")
        self.assertEqual(rows["example.model"]["status"], "private_preflight")
        for sid in ("example.ok", "example.watch", "example.full",
                    "vercel.deployments", "example.nolimit", "example.model"):
            self.assertEqual(rows[sid]["observed_at"], now.isoformat())
            self.assertEqual(rows[sid]["horizon"], "H0")
            self.assertEqual(rows[sid]["evidence_status"], "confirmed")
        unseen = rows["example.unseen"]
        self.assertEqual(unseen["status"], "unknown")
        self.assertIsNone(unseen["observed_at"])
        self.assertEqual(unseen["horizon"], "H1")
        text = json.dumps(snap)
        for private in ("714239", "714240", '"used"', '"limit"', '"reset"'):
            self.assertNotIn(private, text)

    def test_public_mode_refuses_stale_private_output_directory(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "quota-records.jsonl"), "w") as f:
                f.write("private-canary")
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                _qp.main(["--public", "--offline", "--out", d])

    def test_readings_snapshot_converts_v2_projection_to_dashboard_contract(self):
        def svc(sid, lane="ops", limit=100, source="https://example.com/docs"):
            return {"id": sid, "provider": "example", "lane": lane, "source": source,
                    "limit": limit, "unit": "requests", "planned_use": {"safety": 0.9}}
        services = [svc("example.ok"), svc("example.canary", limit=714240),
                    svc("openrouter.free_models", lane="model", limit=None,
                        source="https://openrouter.ai/docs"),
                    svc("example.unseen")]
        readings = {"example.ok": {"used": 10, "limit": 100},
                    "example.canary": {"used": 714239, "limit": 714240},
                    "openrouter.free_models": {"used": 3, "limit": 50}}
        now = datetime(2026, 10, 27, 12, 0, tzinfo=timezone.utc)
        snap = _qp.readings_snapshot(_qp.public_snapshot(services, readings, now), services)
        self.assertEqual(snap["schema"], "3l0.quota-readings.v1")
        self.assertEqual(snap["generated_at"], now.isoformat())
        self.assertIn("not a live quota feed", snap["source"])
        self.assertNotIn("714239", json.dumps(snap))
        rows = {r["resource_id"]: r for r in snap["readings"]}
        for r in rows.values():
            self.assertIsNone(r["used"])
            self.assertIsNone(r["reset"])
            self.assertIn("observed_at", r)
        live = rows["example.ok"]
        self.assertEqual(live["status"], "ok")  # coarse v2 status carried on H0/confirmed evidence
        self.assertEqual((live["horizon"], live["evidence_status"]), ("H0", "confirmed"))
        self.assertEqual(live["observed_at"], now.isoformat())
        self.assertEqual(live["limit"], 100)  # documented entitlement, not a balance
        self.assertEqual(rows["example.canary"]["status"], "watch")
        self.assertEqual(rows["example.canary"]["limit"], 714240)
        model = rows["openrouter.free_models"]
        self.assertEqual(model["status"], "unknown")  # private_preflight is not a display status
        self.assertEqual((model["horizon"], model["evidence_status"]), ("H0", "confirmed"))
        self.assertIsNone(model["limit"])  # registry documents no limit; none inferred
        unseen = rows["example.unseen"]
        self.assertEqual((unseen["status"], unseen["horizon"], unseen["evidence_status"]),
                         ("unknown", "H1", "attributed_claim"))
        self.assertIsNone(unseen["observed_at"])

    def test_readings_snapshot_never_carries_status_without_live_evidence(self):
        services = [{"id": "example.requests", "provider": "example", "lane": "ops",
                     "source": "https://example.com/docs", "limit": 100, "unit": "requests"}]
        forged = {"schema": "quota-public-status/v2", "generated_at": "2026-10-27T12:00:00+00:00",
                  "readings": [{"resource_id": "example.requests", "provider": "example",
                                "status": "ok", "observed_at": None, "horizon": "H1",
                                "evidence_status": "attributed_claim"}]}
        row = _qp.readings_snapshot(forged, services)["readings"][0]
        self.assertEqual(row["status"], "unknown")

    def test_readings_snapshot_rederives_evidence_for_v1_artifacts(self):
        services = [{"id": "example.requests", "provider": "example", "lane": "ops",
                     "source": "https://example.com/docs", "limit": 100, "unit": "requests"}]
        legacy = {"schema": "quota-public-status/v1", "generated_at": "2026-10-22T00:00:00+00:00",
                  "readings": [{"resource_id": "example.requests", "provider": "example",
                                "status": "private_preflight", "observed_at": "2026-10-22T00:00:00+00:00"}]}
        row = _qp.readings_snapshot(legacy, services)["readings"][0]
        self.assertEqual((row["status"], row["horizon"], row["evidence_status"]),
                         ("unknown", "H0", "confirmed"))

    def test_readings_snapshot_rejects_non_projection_input(self):
        with self.assertRaises(ValueError):
            _qp.readings_snapshot({"schema": "3l0.quota-readings.v1", "readings": []}, [])
        with self.assertRaises(ValueError):
            _qp.readings_snapshot(["not-a-dict"], [])

    def test_from_public_cli_writes_only_the_readings_snapshot(self):
        artifact = {"schema": "quota-public-status/v2", "generated_at": "2026-10-27T12:00:00+00:00",
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
            row = next(r for r in json.loads(text)["readings"] if r["resource_id"] == "openrouter.free_models")
            self.assertEqual((row["status"], row["used"], row["reset"]), ("unknown", None, None))

    def test_public_workflow_uploads_only_status_projection(self):
        from pathlib import Path
        workflow = (Path(ROOT) / ".github/workflows/vercel-quota-probe.yml").read_text()
        self.assertIn("scripts/quota_poll.py --public", workflow)
        self.assertIn("path: quota-out/quota-public-status.json", workflow)
        self.assertNotIn("r['used']", workflow)
        self.assertNotIn("path: quota-out/\n", workflow)


if __name__ == "__main__":
    unittest.main()
