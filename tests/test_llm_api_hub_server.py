"""Regression tests for the local llm-api-hub contract."""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
import unittest

from fastapi.testclient import TestClient


APP_PATH = Path(__file__).parents[1] / "llm_api_hub" / "server" / "app.py"


def load_app():
    spec = importlib.util.spec_from_file_location("termux_llm_api_hub_test", APP_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load hub app from {APP_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class HubServerTests(unittest.TestCase):
    def test_health_and_models_are_available_without_provider_calls(self):
        module = load_app()
        client = TestClient(module.app)

        health = client.get("/health")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()["status"], "ok")

        models = client.get("/v1/models")
        self.assertEqual(models.status_code, 200)
        self.assertIn("wrapper/deepseek", {item["id"] for item in models.json()["data"]})

    def test_wrapper_request_is_normalized_to_openai_shape(self):
        module = load_app()
        module.runtime.complete_wrapper = lambda provider, request: f"{provider}:ok"
        client = TestClient(module.app)

        response = client.post(
            "/v1/chat/completions",
            json={
                "model": "wrapper/deepseek",
                "messages": [
                    {"role": "system", "content": "be concise"},
                    {"role": "user", "content": "hello"},
                ],
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["object"], "chat.completion")
        self.assertEqual(body["model"], "wrapper/deepseek")
        self.assertEqual(
            body["choices"][0]["message"],
            {"role": "assistant", "content": "deepseek:ok"},
        )

    def test_stream_request_emits_terminal_done_event(self):
        module = load_app()
        module.runtime.complete_wrapper = lambda provider, request: "streamed"
        client = TestClient(module.app)

        response = client.post(
            "/v1/chat/completions",
            json={
                "model": "wrapper/mistral",
                "messages": [{"role": "user", "content": "hello"}],
                "stream": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("data: [DONE]", response.text)

    def test_optional_bearer_auth_is_enforced(self):
        module = load_app()
        client = TestClient(module.app)
        original = os.environ.get("LLM_API_HUB_KEY")
        os.environ["LLM_API_HUB_KEY"] = "test-key"
        try:
            self.assertEqual(client.get("/v1/models").status_code, 401)
            self.assertEqual(
                client.get(
                    "/v1/models", headers={"Authorization": "Bearer test-key"}
                ).status_code,
                200,
            )
        finally:
            if original is None:
                os.environ.pop("LLM_API_HUB_KEY", None)
            else:
                os.environ["LLM_API_HUB_KEY"] = original


if __name__ == "__main__":
    unittest.main()
