import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts import provider_quota_managers as managers
from scripts import provider_quota_transport as transport

FIXTURES = Path(__file__).parent / "fixtures"
NOW = "2026-10-21T09:00:00Z"


class OllamaQuotaTests(unittest.TestCase):
    def load(self, name):
        return json.loads((FIXTURES / name).read_text())

    def test_modern_usd_balances_and_period_are_private_and_allowlisted(self):
        obs = managers.normalize_observation("ollama", metadata=self.load("provider_quota_ollama_modern.json"), observed_at=NOW, scope="caller-declared")
        self.assertEqual(obs["signals"]["ollama_included_balance_usd"], 72.5)
        self.assertEqual(obs["signals"]["ollama_purchased_balance_usd"], 25)
        self.assertEqual(obs["signals"]["ollama_included_period_from"], "2026-09-15T09:30:00Z")
        self.assertEqual(obs["scope_status"], "caller_declared_unverified")
        self.assertNotIn("remaining_requests", obs["signals"])
        self.assertNotIn("account_id", obs)
        self.assertNotIn("email", obs)

    def test_legacy_percentages_never_become_counts(self):
        obs = managers.normalize_observation("ollama", metadata=self.load("provider_quota_ollama_legacy.json"), observed_at=NOW, scope="caller-declared")
        self.assertEqual(obs["signals"]["ollama_session_remaining_percent"], 75)
        self.assertEqual(obs["signals"]["ollama_weekly_remaining_percent"], 40)
        self.assertFalse(any("requests" in k or "tokens" in k for k in obs["signals"]))

    def test_missing_unknown_and_rejects_malformed_variants(self):
        self.assertEqual(managers.normalize_observation("ollama", metadata={}, observed_at=NOW, scope="x")["status"], "unknown")
        base = self.load("provider_quota_ollama_modern.json")
        cases = []
        partial = json.loads(json.dumps(base)); del partial["included"]["period"]["until"]; cases.append(partial)
        mixed = json.loads(json.dumps(base)); mixed["included"]["session"] = {}; cases.append(mixed)
        badpct = self.load("provider_quota_ollama_legacy.json"); badpct["included"]["session"]["remaining_percent"] = 100.01; cases.append(badpct)
        badtime = json.loads(json.dumps(base)); badtime["included"]["period"]["from"] = "2026-10-16T00:00:00Z"; cases.append(badtime)
        badnum = json.loads(json.dumps(base)); badnum["purchased"]["balance_usd"] = float("inf"); cases.append(badnum)
        for payload in cases:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                managers.normalize_observation("ollama", metadata=payload, observed_at=NOW, scope="x")

    def test_transport_uses_only_fixed_endpoint_and_suppresses_failures_without_logs(self):
        payload = self.load("provider_quota_ollama_modern.json")
        calls = []
        def request(**kwargs):
            calls.append(kwargs)
            return SimpleNamespace(status_code=200, json=lambda: payload)
        secret = "bearer-secret-canary"
        obs = transport.observe_ollama_balance(secret, request, observed_at=NOW, scope="unverified", timeout=4)
        self.assertEqual(obs["status"], "observed")
        self.assertEqual(calls, [{"method": "GET", "url": "https://ollama.com/api/balance", "headers": {"Authorization": "Bearer " + secret}, "timeout": 4.0, "allow_redirects": False, "max_response_bytes": 65536}])
        for code in (301, 302, 307, 401, 403, 429, 503):
            result = transport.observe_ollama_balance(secret, lambda **kw: SimpleNamespace(status_code=code), observed_at=NOW, scope="x")
            self.assertEqual(result["status"], "unknown")
            self.assertEqual(result["signals"], {})
        result = transport.observe_ollama_balance(secret, lambda **kw: SimpleNamespace(status_code=200, json=lambda: {"payload": "payload-canary"}), observed_at=NOW, scope="x")
        self.assertEqual(result["status"], "unknown")
        result = transport.observe_ollama_balance(secret, lambda **kw: (_ for _ in ()).throw(RuntimeError("secret payload-canary")), observed_at=NOW, scope="x")
        self.assertEqual(result["status"], "unknown")
        self.assertNotIn(secret, json.dumps(result))
        self.assertNotIn("payload-canary", json.dumps(result))

    def test_transport_does_not_log_or_affect_runtime_router(self):
        with patch("builtins.print") as printed:
            obs = transport.observe_ollama_balance("secret", lambda **kw: (_ for _ in ()).throw(Exception("private")), observed_at=NOW, scope="x")
        printed.assert_not_called()
        self.assertEqual(obs["status"], "unknown")
        self.assertEqual(managers.build_public_metadata()["runtime_admission"], "unchanged")

    def test_invalid_context_and_keys_never_invoke_transport(self):
        calls = []
        def request(**kwargs):
            calls.append(kwargs)
            raise AssertionError("must not be called")
        for key in ("", "line\r\nbreak", "white space", "nonascii-é"):
            self.assertEqual(transport.observe_ollama_balance(key, request, observed_at=NOW, scope="x")["status"], "unknown")
        for timestamp, scope in ((NOW, ""), ("invalid", "x"), ("2026-10-21T09:00:00", "x")):
            with self.assertRaises(ValueError):
                transport.observe_ollama_balance("secret", request, observed_at=timestamp, scope=scope)
        for timeout in (True, float("nan"), float("inf"), 0, 11):
            self.assertEqual(transport.observe_ollama_balance("secret", request, observed_at=NOW, scope="x", timeout=timeout)["status"], "unknown")
        self.assertEqual(calls, [])

    def test_oversized_or_nonfinite_payload_is_unknown(self):
        for payload in ({"padding": "x" * 65537}, {"bad": float("nan")}):
            result = transport.observe_ollama_balance("secret", lambda **kw: SimpleNamespace(status_code=200, json=lambda: payload), observed_at=NOW, scope="x")
            self.assertEqual(result["status"], "unknown")
            self.assertEqual(result["signals"], {})


if __name__ == "__main__":
    unittest.main()
