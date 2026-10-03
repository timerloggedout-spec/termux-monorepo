"""_v1_hindsight cloud client + tool specs.

First offline coverage for deepcli/deepcli/_v1_hindsight.py (previously
zero tests). The HTTP layer is fully injectable: HindsightClient builds
its httpx.AsyncClient lazily in _http(), and _post() drives it via
client.post(). We replace _client with a scripted fake so no socket is
ever opened.
"""

import asyncio
import pathlib
import sys
import unittest

_HERE = pathlib.Path(__file__).resolve()
for _root in (_HERE.parents[1], pathlib.Path.home() / "deepcli"):
    if (_root / "deepcli" / "_v1_hindsight.py").exists():
        sys.path.insert(0, str(_root))
        break

import httpx  # noqa: E402

from deepcli._v1_hindsight import (  # noqa: E402
    DEFAULT_BANK_ID,
    HindsightClient,
    HindsightError,
    HindsightToolSpec,
    build_hindsight_tools,
    recall,
    reflect,
    retain,
)


def _run(coro):
    return asyncio.run(coro)


class _FakeResponse:
    def __init__(self, status_code=200, json_body=None, content=b"{}"):
        self.status_code = status_code
        self._json = json_body
        self.content = content if content is not None else b""

    def json(self):
        if self._json is None:
            raise ValueError("no json")
        return self._json

    @property
    def text(self):
        return self.content.decode()


class _FakeAsyncClient:
    """Stands in for httpx.AsyncClient. Records calls, replays scripted
    responses or exceptions."""

    is_closed = False

    def __init__(self, *, response=None, exc=None):
        self.response = response
        self.exc = exc
        self.calls = []

    async def post(self, path, json=None):
        self.calls.append((path, json))
        if self.exc is not None:
            raise self.exc
        return self.response

    async def aclose(self):
        self.is_closed = True


def _client_with(fake):
    """Build a HindsightClient whose _http() returns the given fake."""
    c = HindsightClient(base_url="https://hs.example", api_key=None)
    c._client = fake
    return c


class TestConfig(unittest.TestCase):
    def test_defaults(self):
        c = HindsightClient()
        self.assertTrue(c.base_url.startswith("http"))
        self.assertEqual(c.default_bank_id, DEFAULT_BANK_ID)

    def test_env_override(self):
        import os

        saved = {
            k: os.environ.get(k)
            for k in (
                "HINDSIGHT_BASE_URL",
                "HINDSIGHT_API_KEY",
                "HINDSIGHT_BANK_ID",
                "HINDSIGHT_TIMEOUT_S",
            )
        }
        try:
            os.environ["HINDSIGHT_BASE_URL"] = "http://localhost:8888"
            os.environ["HINDSIGHT_API_KEY"] = "sekret"
            os.environ["HINDSIGHT_BANK_ID"] = "bank::x"
            os.environ["HINDSIGHT_TIMEOUT_S"] = "5"
            c = HindsightClient()
            self.assertEqual(c.base_url, "http://localhost:8888")
            self.assertEqual(c.api_key, "sekret")
            self.assertEqual(c.default_bank_id, "bank::x")
            self.assertEqual(c.timeout_s, 5.0)
        finally:
            for k, v in saved.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v


class TestPlumbing(unittest.TestCase):
    def test_headers_without_key(self):
        c = HindsightClient(api_key=None)
        h = c._headers()
        self.assertNotIn("Authorization", h)
        self.assertEqual(h["Content-Type"], "application/json")

    def test_headers_with_key(self):
        c = HindsightClient(api_key="abc")
        self.assertEqual(c._headers()["Authorization"], "Bearer abc")

    def test_url_join(self):
        c = HindsightClient(base_url="https://hs.example/")
        self.assertEqual(c._url("/v1/x"), "https://hs.example/v1/x")
        self.assertEqual(c._url("v1/x"), "https://hs.example/v1/x")


class TestPost(unittest.TestCase):
    def test_success_json(self):
        fake = _FakeAsyncClient(response=_FakeResponse(200, {"ok": 1}))
        c = _client_with(fake)
        out = _run(c._post("/p", {"a": 1}))
        self.assertEqual(out, {"ok": 1})
        self.assertEqual(fake.calls, [("/p", {"a": 1})])

    def test_empty_body_returns_none(self):
        fake = _FakeAsyncClient(response=_FakeResponse(204, None, content=b""))
        c = _client_with(fake)
        self.assertIsNone(_run(c._post("/p", {})))

    def test_non_json_body_returns_text(self):
        fake = _FakeAsyncClient(response=_FakeResponse(200, None, content=b"raw"))
        c = _client_with(fake)
        self.assertEqual(_run(c._post("/p", {})), "raw")

    def test_http_400_raises_with_payload(self):
        fake = _FakeAsyncClient(response=_FakeResponse(404, {"err": "nope"}))
        c = _client_with(fake)
        with self.assertRaises(HindsightError) as cm:
            _run(c._post("/p", {}))
        self.assertEqual(cm.exception.status_code, 404)
        self.assertEqual(cm.exception.payload, {"err": "nope"})

    def test_http_400_non_json_payload_is_text(self):
        fake = _FakeAsyncClient(response=_FakeResponse(500, None, content=b"boom"))
        c = _client_with(fake)
        with self.assertRaises(HindsightError) as cm:
            _run(c._post("/p", {}))
        self.assertEqual(cm.exception.payload, "boom")

    def test_network_error_wrapped(self):
        fake = _FakeAsyncClient(exc=httpx.ConnectError("refused"))
        c = _client_with(fake)
        with self.assertRaises(HindsightError):
            _run(c._post("/p", {}))


class TestOperations(unittest.TestCase):
    def test_aretain_payload(self):
        fake = _FakeAsyncClient(response=_FakeResponse(200, {"id": "m1"}))
        c = _client_with(fake)
        out = _run(c.aretain("hello", metadata={"k": "v"}))
        self.assertEqual(out, {"id": "m1"})
        path, payload = fake.calls[0]
        self.assertEqual(path, f"/v1/default/banks/{DEFAULT_BANK_ID}/memories")
        self.assertEqual(
            payload, {"items": [{"content": "hello", "metadata": {"k": "v"}}]}
        )

    def test_aretain_no_metadata(self):
        fake = _FakeAsyncClient(response=_FakeResponse(200, {}))
        c = _client_with(fake)
        _run(c.aretain("x"))
        self.assertEqual(fake.calls[0][1], {"items": [{"content": "x"}]})

    def test_aretain_bank_override(self):
        fake = _FakeAsyncClient(response=_FakeResponse(200, {}))
        c = _client_with(fake)
        _run(c.aretain("x", bank_id="other"))
        self.assertIn("/banks/other/memories", fake.calls[0][0])

    def test_arecall_payload_with_limit(self):
        fake = _FakeAsyncClient(response=_FakeResponse(200, {"hits": []}))
        c = _client_with(fake)
        _run(c.arecall("q", limit=3))
        path, payload = fake.calls[0]
        self.assertTrue(path.endswith("/memories/recall"))
        self.assertEqual(payload, {"query": "q", "top_k": 3})

    def test_arecall_without_limit_omits_top_k(self):
        fake = _FakeAsyncClient(response=_FakeResponse(200, {}))
        c = _client_with(fake)
        _run(c.arecall("q"))
        self.assertEqual(fake.calls[0][1], {"query": "q"})

    def test_areflect_payload(self):
        fake = _FakeAsyncClient(response=_FakeResponse(200, {"answer": "a"}))
        c = _client_with(fake)
        out = _run(c.areflect("why"))
        self.assertEqual(out, {"answer": "a"})
        path, payload = fake.calls[0]
        self.assertTrue(path.endswith("/reflect"))
        self.assertEqual(payload, {"query": "why"})


class TestLifecycle(unittest.TestCase):
    def test_aclose_closes_and_clears(self):
        fake = _FakeAsyncClient(response=_FakeResponse(200, {}))
        c = _client_with(fake)
        _run(c.aclose())
        self.assertTrue(fake.is_closed)
        self.assertIsNone(c._client)

    def test_aclose_noop_without_client(self):
        c = HindsightClient()
        _run(c.aclose())  # must not raise

    def test_context_manager(self):
        async def go():
            c = HindsightClient(base_url="https://hs.example")
            fake = _FakeAsyncClient(response=_FakeResponse(200, {}))
            c._client = fake
            async with c as entered:
                self.assertIs(entered, c)
            self.assertTrue(fake.is_closed)

        _run(go())


class TestToolHandlers(unittest.TestCase):
    def test_retain_shape(self):
        fake = _FakeAsyncClient(response=_FakeResponse(200, {"id": "m1"}))
        c = _client_with(fake)
        out = _run(retain("mem", client=c))
        self.assertEqual(
            out, {"ok": True, "operation": "retain", "result": {"id": "m1"}}
        )

    def test_recall_shape(self):
        fake = _FakeAsyncClient(response=_FakeResponse(200, {"hits": [1]}))
        c = _client_with(fake)
        out = _run(recall("q", limit=2, client=c))
        self.assertEqual(out["operation"], "recall")
        self.assertEqual(fake.calls[0][1], {"query": "q", "top_k": 2})

    def test_reflect_shape(self):
        fake = _FakeAsyncClient(response=_FakeResponse(200, {"answer": "a"}))
        c = _client_with(fake)
        out = _run(reflect("q", client=c))
        self.assertEqual(
            out, {"ok": True, "operation": "reflect", "result": {"answer": "a"}}
        )


class TestToolSpecs(unittest.TestCase):
    def test_three_specs_in_order(self):
        specs = build_hindsight_tools(client=HindsightClient())
        self.assertEqual(
            [s.name for s in specs],
            ["hindsight_retain", "hindsight_recall", "hindsight_reflect"],
        )
        for s in specs:
            self.assertIsInstance(s, HindsightToolSpec)
            self.assertTrue(callable(s.handler))
            self.assertEqual(s.schema["type"], "object")

    def test_required_fields(self):
        specs = {s.name: s for s in build_hindsight_tools(client=HindsightClient())}
        self.assertEqual(specs["hindsight_retain"].schema["required"], ["content"])
        self.assertEqual(specs["hindsight_recall"].schema["required"], ["query"])
        self.assertEqual(specs["hindsight_reflect"].schema["required"], ["query"])

    def test_injected_client_is_used_by_handler(self):
        fake = _FakeAsyncClient(response=_FakeResponse(200, {"id": "m1"}))
        c = _client_with(fake)
        specs = {s.name: s for s in build_hindsight_tools(client=c)}
        out = _run(specs["hindsight_retain"].handler("mem"))
        self.assertEqual(out["result"], {"id": "m1"})
        self.assertEqual(len(fake.calls), 1)


if __name__ == "__main__":
    unittest.main()
