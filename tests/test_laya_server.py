from __future__ import annotations

import importlib.util
import json
import os
import sys
import threading
import types
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = ROOT / "deploy" / "laya" / "server.py"


class FakeRouter:
    def __init__(self, preload=False):
        self.preload = preload

    def predict(self, state, questions):
        return {"answers": {"route": {"choice": "general", "confidence": 0.8}}}


class LayaServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fake_laya = types.ModuleType("laya")
        cls.fake_laya.Router = FakeRouter
        cls.old_laya = sys.modules.get("laya")
        sys.modules["laya"] = cls.fake_laya
        with patch.dict(os.environ, {"LAYA_API_TOKEN": "unit-test-secret", "LAYA_REQUIRE_AUTH": "1"}):
            spec = importlib.util.spec_from_file_location("laya_test_server", SERVER_PATH)
            cls.module = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(cls.module)
        cls.httpd = cls.module.ThreadingHTTPServer(("127.0.0.1", 0), cls.module.Handler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.httpd.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=2)
        if cls.old_laya is None:
            sys.modules.pop("laya", None)
        else:
            sys.modules["laya"] = cls.old_laya

    def request(self, path, body=None, token=None):
        data = None if body is None else json.dumps(body).encode()
        headers = {}
        if data is not None:
            headers["Content-Type"] = "application/json"
        if token:
            headers["Authorization"] = "Bearer " + token
        req = Request(self.base + path, data=data, headers=headers, method="GET" if body is None else "POST")
        try:
            with urlopen(req, timeout=3) as response:
                return response.status, json.loads(response.read())
        except HTTPError as exc:
            return exc.code, json.loads(exc.read())

    def test_health_is_public(self):
        status, payload = self.request("/healthz")
        self.assertEqual(status, 200)
        self.assertTrue(payload["ok"])

    def test_decide_requires_bearer_token(self):
        status, payload = self.request("/decide", {"state": {}, "questions": {"route": {}}})
        self.assertEqual(status, 401)
        self.assertEqual(payload["error"], "unauthorized")

    def test_decide_validates_shape_and_returns_decision(self):
        status, _ = self.request("/decide", {"state": [], "questions": {}}, "unit-test-secret")
        self.assertEqual(status, 400)
        status, payload = self.request(
            "/decide", {"state": {"body": "hello"}, "questions": {"route": {"type": "choice"}}},
            "unit-test-secret",
        )
        self.assertEqual(status, 200)
        self.assertEqual(payload["answers"]["route"]["choice"], "general")

    def test_unknown_path_is_not_found(self):
        status, payload = self.request("/not-a-route")
        self.assertEqual(status, 404)
        self.assertEqual(payload["error"], "not_found")


if __name__ == "__main__":
    unittest.main()
