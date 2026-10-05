"""RoutedHindsightClient: cloud->codespace->local routing + circuit breaker.

Offline coverage for deepcli/deepcli/_v1_hindsight_router.py, which had
zero tests. Everything is exercised with injected fakes; no network, no
sqlite (the local store is a plain dict-returning stub), no real sleeps.
"""

import asyncio
import os
import pathlib
import sys
import unittest


def _repo_root():
    """Walk up from this file to the dir containing deepcli/_v1_hindsight.py."""
    here = pathlib.Path(__file__).resolve()
    for d in here.parents:
        if (d / "deepcli" / "_v1_hindsight_router.py").exists():
            return d
    return pathlib.Path.home() / "deepcli"


sys.path.insert(0, str(_repo_root()))
from deepcli._v1_hindsight import HindsightError
from deepcli._v1_hindsight_router import (
    DEMOTE_CODES,
    RoutedHindsightClient,
    _LocalCodespaceClient,
)


RUN = lambda coro: asyncio.run(coro)


class _FakeLocal:
    """Minimal stand-in for LocalHindsightClient (no sqlite)."""

    def __init__(self, db_path="/tmp/x.db"):
        self.db_path = db_path
        self.default_bank_id = "local-bank"
        self.retained = []
        self.calls = []

    async def aretain(self, content, *, bank_id=None, metadata=None):
        self.calls.append("aretain")
        self.retained.append((content, bank_id, metadata))
        return {"success": True, "local": True, "id": "local:deadbeef"}

    async def arecall(self, query, *, bank_id=None, limit=None):
        self.calls.append("arecall")
        return {"results": [], "local": True, "query": query}

    async def areflect(self, query, *, bank_id=None):
        self.calls.append("areflect")
        return {"answer": None, "reason": "local-only", "local": True}

    async def aclose(self):
        self.calls.append("aclose")


class _FakeCloud:
    def __init__(self, *, error=None):
        self.base_url = "https://cloud.example"
        self.default_bank_id = "cloud-bank"
        self.error = error
        self.calls = []
        self.closed = False

    async def aretain(self, content, *, bank_id=None, metadata=None):
        self.calls.append("aretain")
        if self.error:
            raise self.error
        return {"success": True, "cloud": True}

    async def arecall(self, query, *, bank_id=None, limit=None):
        self.calls.append("arecall")
        if self.error:
            raise self.error
        return {"results": ["cloud"], "cloud": True}

    async def areflect(self, query, *, bank_id=None):
        self.calls.append("areflect")
        if self.error:
            raise self.error
        return {"answer": "cloud", "cloud": True}

    async def aclose(self):
        self.calls.append("aclose")
        self.closed = True


class _FakeCodespace(_LocalCodespaceClient):
    """Codespace client whose HTTP layer is replaced by a scripted responder."""

    def __init__(self, responder):
        super().__init__("http://localhost:18888")
        self._responder = responder
        self.paths = []

    async def _req(self, path, method="GET", payload=None):
        self.paths.append((method, path, payload))
        return self._responder(path, method, payload)


class _EnvGuard:
    """Save/restore the HS_* env vars a test mutates."""

    KEYS = (
        "HS_LOCAL_URL",
        "HS_REMOTE_URL",
        "HS_WRITE_MODE",
        "HINDSIGHT_BANK_ID",
    )

    def __enter__(self):
        self._saved = {k: os.environ.get(k) for k in self.KEYS}
        for k in self.KEYS:
            os.environ.pop(k, None)
        return self

    def __exit__(self, *exc):
        for k in self.KEYS:
            os.environ.pop(k, None)
            if self._saved[k] is not None:
                os.environ[k] = self._saved[k]


class TestBootstrap(unittest.TestCase):
    def test_module_is_on_this_checkout(self):
        root = _repo_root()
        self.assertTrue((root / "deepcli" / "_v1_hindsight_router.py").exists())

    def test_demote_codes_set(self):
        self.assertEqual(DEMOTE_CODES, {402, 429, 500, 502, 503, 504})


class TestConstruction(unittest.TestCase):
    def test_defaults_to_injected_children(self):
        with _EnvGuard():
            local = _FakeLocal()
            cloud = _FakeCloud()
            r = RoutedHindsightClient(cloud=cloud, local=local)
        self.assertIs(r.cloud, cloud)
        self.assertIs(r.local, local)
        self.assertIsNone(r.codespace)
        self.assertIsNone(r.remote)
        self.assertTrue(r._cloud_healthy)
        self.assertEqual(r._demoted_at, 0.0)

    def test_codespace_and_remote_built_from_env(self):
        with _EnvGuard():
            os.environ["HS_LOCAL_URL"] = "http://localhost:18888"
            os.environ["HS_REMOTE_URL"] = "https://cs.example"
            r = RoutedHindsightClient(cloud=_FakeCloud(), local=_FakeLocal())
            self.assertIsNotNone(r.codespace)
            self.assertIsNotNone(r.remote)
            self.assertEqual(r.base_url, "http://localhost:18888")

    def test_base_url_falls_back_to_cloud(self):
        with _EnvGuard():
            r = RoutedHindsightClient(cloud=_FakeCloud(), local=_FakeLocal())
            self.assertEqual(r.base_url, "https://cloud.example")

    def test_bank_id_from_env_overrides_cloud(self):
        with _EnvGuard():
            os.environ["HINDSIGHT_BANK_ID"] = "explicit-bank"
            r = RoutedHindsightClient(cloud=_FakeCloud(), local=_FakeLocal())
            self.assertEqual(r.default_bank_id, "explicit-bank")

    def test_bank_id_defaults_to_cloud(self):
        with _EnvGuard():
            r = RoutedHindsightClient(cloud=_FakeCloud(), local=_FakeLocal())
            self.assertEqual(r.default_bank_id, "cloud-bank")


class TestRetainFailover(unittest.TestCase):
    def test_routes_to_local_when_no_codespace(self):
        with _EnvGuard():
            local = _FakeLocal()
            r = RoutedHindsightClient(cloud=_FakeCloud(), local=local)
            out = RUN(r.aretain("hello", metadata={"k": 1}))
        self.assertTrue(out["local"])
        self.assertEqual(local.retained[0][0], "hello")

    def test_codespace_error_demotes_then_local(self):
        with _EnvGuard():
            os.environ["HS_LOCAL_URL"] = "http://localhost:18888"
            local = _FakeLocal()
            r = RoutedHindsightClient(cloud=_FakeCloud(), local=local)
            r.codespace = _FakeCodespace(
                lambda p, m, pl: (_ for _ in ()).throw(
                    HindsightError("boom", status_code=503)
                )
            )
            out = RUN(r.aretain("x"))
        self.assertTrue(out["local"])
        self.assertFalse(r._cloud_healthy)

    def test_codespace_non_demote_code_reraises(self):
        with _EnvGuard():
            os.environ["HS_LOCAL_URL"] = "http://localhost:18888"
            r = RoutedHindsightClient(cloud=_FakeCloud(), local=_FakeLocal())
            r.codespace = _FakeCodespace(
                lambda p, m, pl: (_ for _ in ()).throw(
                    HindsightError("bad", status_code=400)
                )
            )
            with self.assertRaises(HindsightError):
                RUN(r.aretain("x"))

    def test_codespace_success_short_circuits(self):
        with _EnvGuard():
            os.environ["HS_LOCAL_URL"] = "http://localhost:18888"
            local = _FakeLocal()
            r = RoutedHindsightClient(cloud=_FakeCloud(), local=local)
            r.codespace = _FakeCodespace(lambda p, m, pl: {"ok": True})
            out = RUN(r.aretain("x"))
        self.assertEqual(out, {"ok": True})
        self.assertEqual(local.retained, [])


class TestRecallReflect(unittest.TestCase):
    def test_recall_local_when_no_codespace(self):
        with _EnvGuard():
            r = RoutedHindsightClient(cloud=_FakeCloud(), local=_FakeLocal())
            out = RUN(r.arecall("q"))
        self.assertTrue(out["local"])

    def test_recall_codespace_503_demotes(self):
        with _EnvGuard():
            os.environ["HS_LOCAL_URL"] = "http://localhost:18888"
            r = RoutedHindsightClient(cloud=_FakeCloud(), local=_FakeLocal())
            r.codespace = _FakeCodespace(
                lambda p, m, pl: (_ for _ in ()).throw(
                    HindsightError("x", status_code=429)
                )
            )
            out = RUN(r.arecall("q"))
        self.assertTrue(out["local"])
        self.assertFalse(r._cloud_healthy)

    def test_reflect_codespace_ok(self):
        with _EnvGuard():
            os.environ["HS_LOCAL_URL"] = "http://localhost:18888"
            r = RoutedHindsightClient(cloud=_FakeCloud(), local=_FakeLocal())
            r.codespace = _FakeCodespace(lambda p, m, pl: {"answer": "cs"})
            out = RUN(r.areflect("q"))
        self.assertEqual(out, {"answer": "cs"})

    def test_reflect_local_fallback(self):
        with _EnvGuard():
            r = RoutedHindsightClient(cloud=_FakeCloud(), local=_FakeLocal())
            out = RUN(r.areflect("q"))
        self.assertEqual(out["reason"], "local-only")


class TestCircuitBreaker(unittest.TestCase):
    def test_maybe_restore_after_reset_window(self):
        with _EnvGuard():
            r = RoutedHindsightClient(cloud=_FakeCloud(), local=_FakeLocal())
            r._demote("test")
            self.assertFalse(r._cloud_healthy)
            r._demoted_at -= 10_000  # older than any RESET_AFTER_S
            r._maybe_restore()
            self.assertTrue(r._cloud_healthy)

    def test_maybe_restore_is_noop_when_healthy(self):
        with _EnvGuard():
            r = RoutedHindsightClient(cloud=_FakeCloud(), local=_FakeLocal())
            r._maybe_restore()
            self.assertTrue(r._cloud_healthy)


class TestFanout(unittest.TestCase):
    def test_fanout_writes_local_cloud_and_codespace(self):
        with _EnvGuard():
            os.environ["HS_WRITE_MODE"] = "fanout"
            os.environ["HS_LOCAL_URL"] = "http://localhost:18888"
            local = _FakeLocal()
            cloud = _FakeCloud()
            r = RoutedHindsightClient(cloud=cloud, local=local)
            r.codespace = _FakeCodespace(lambda p, m, pl: {"cs": True})
            out = RUN(r.aretain("x"))
        self.assertTrue(out["fanout"])
        self.assertEqual(set(out["results"]), {"codespace", "cloud", "local"})

    def test_fanout_records_per_target_errors(self):
        with _EnvGuard():
            os.environ["HS_WRITE_MODE"] = "fanout"
            local = _FakeLocal()
            cloud = _FakeCloud(error=RuntimeError("cloud down"))
            r = RoutedHindsightClient(cloud=cloud, local=local)
            out = RUN(r.aretain("x"))
        self.assertFalse(out["results"]["cloud"]["success"])
        self.assertIn("cloud down", out["results"]["cloud"]["error"])

    def test_fanout_skips_cloud_when_unhealthy(self):
        with _EnvGuard():
            os.environ["HS_WRITE_MODE"] = "fanout"
            r = RoutedHindsightClient(cloud=_FakeCloud(), local=_FakeLocal())
            r._demote("test")
            out = RUN(r.aretain("x"))
        self.assertNotIn("cloud", out["results"])
        self.assertIn("local", out["results"])


class TestStatusAndClose(unittest.TestCase):
    def test_status_shape(self):
        with _EnvGuard():
            r = RoutedHindsightClient(
                cloud=_FakeCloud(), local=_FakeLocal(db_path="/tmp/zz.db")
            )
            s = r.status()
        self.assertEqual(
            set(s), {"cloud_healthy", "demoted_at", "base_url", "bank_id", "local_db"}
        )
        self.assertEqual(s["local_db"], "/tmp/zz.db")

    def test_aclose_delegates_to_cloud(self):
        with _EnvGuard():
            cloud = _FakeCloud()
            r = RoutedHindsightClient(cloud=cloud, local=_FakeLocal())
            RUN(r.aclose())
        self.assertTrue(cloud.closed)

    def test_aclose_swallows_cloud_errors(self):
        class _Boom(_FakeCloud):
            async def aclose(self):
                raise RuntimeError("nope")

        with _EnvGuard():
            r = RoutedHindsightClient(cloud=_Boom(), local=_FakeLocal())
            RUN(r.aclose())  # must not raise


if __name__ == "__main__":
    unittest.main()
