import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "telemetry_ingest"))

from deepcli.provider_guard import retired_hindsight_endpoint_reason
import retain_payloads


class HindsightProviderGuardTests(unittest.TestCase):
    def test_fly_and_koyeb_hosts_are_retired(self):
        for url in (
            "https://hindsight-termux.fly.dev",
            "https://hindsight-deepagent.koyeb.app",
            "https://api.fly.io/graphql",
            "https://app.koyeb.com/v1",
        ):
            with self.subTest(url=url):
                self.assertIsNotNone(retired_hindsight_endpoint_reason(url))

    def test_active_function_and_database_hosts_remain_available(self):
        for url in (
            "https://api.hindsight.vectorize.io",
            "https://mesh-edge.workers.dev",
            "https://termux-monorepo.vercel.app",
            "https://project.supabase.co",
            "http://localhost:8888",
        ):
            with self.subTest(url=url):
                self.assertIsNone(retired_hindsight_endpoint_reason(url))

    def test_retain_blocks_retired_endpoint_before_network_io(self):
        def fail_opener(*args, **kwargs):
            raise AssertionError("network call reached retired endpoint")

        result = retain_payloads.retain(
            [{"content": "synthetic", "metadata": {"unit_id": "1"}}],
            "https://hindsight-termux.fly.dev",
            "bank",
            "key",
            opener=fail_opener,
        )
        self.assertEqual(result["attempted"], 0)
        self.assertIn("retired provider host", result["blocked_reason"])
        self.assertEqual(result["ok"], 0)


if __name__ == "__main__":
    unittest.main()
