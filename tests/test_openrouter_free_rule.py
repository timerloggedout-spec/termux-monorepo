"""Focused tests for OpenRouter free-by-pricing rule (stealth/ox-alpha)."""

import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import scripts.model_router as mr


def test_is_free_openrouter_model_zero_price_and_suffix():
    assert mr.is_free_openrouter_model("stealth/ox-alpha", {"prompt": "0", "completion": "0"})
    assert mr.is_free_openrouter_model("stealth/ox-alpha")  # static allow-list
    assert mr.is_free_openrouter_model("meta-llama/llama-3.3-70b-instruct:free")
    assert not mr.is_free_openrouter_model("openai/gpt-4o", {"prompt": "5", "completion": "15"})


def test_fetch_includes_zero_price_without_free_suffix(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps(
                {
                    "data": [
                        {
                            "id": "stealth/ox-alpha",
                            "pricing": {"prompt": "0", "completion": "0"},
                        },
                        {
                            "id": "paid/model",
                            "pricing": {"prompt": "1", "completion": "1"},
                        },
                        {
                            "id": "x:free",
                            "pricing": {"prompt": "0", "completion": "0"},
                        },
                    ]
                }
            ).encode()

    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **k: FakeResponse())
    models = mr.fetch_openrouter_free_models()
    assert "stealth/ox-alpha" in models
    assert "x:free" in models
    assert "paid/model" not in models


def test_legacy_models_include_ox_alpha():
    assert "stealth/ox-alpha" in mr.LEGACY_MODELS
