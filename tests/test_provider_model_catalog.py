import json
import pytest
from unittest.mock import patch
from scripts import provider_model_catalog


def test_resolve_secret():
    with patch.dict("os.environ", {"HUGGINGFACE_TOKEN": "hf_test_123"}, clear=True):
        tok, env = provider_model_catalog.resolve_secret("huggingface")
        assert tok == "hf_test_123"
        assert env == "HUGGINGFACE_TOKEN"

    with patch.dict("os.environ", {"HF_API_TOKEN": "hf_alias_456"}, clear=True):
        tok, env = provider_model_catalog.resolve_secret("huggingface")
        assert tok == "hf_alias_456"
        assert env == "HF_API_TOKEN"

    with patch.dict("os.environ", {}, clear=True):
        tok, env = provider_model_catalog.resolve_secret("openrouter")
        assert tok is None
        assert env == "OPENROUTER_API_KEY"


def test_price_classification():
    # Fast path zero price checks
    assert provider_model_catalog.price_classification({"pricing": {"prompt": "0", "completion": "0"}}) == "free_zero_price"
    assert provider_model_catalog.price_classification({"pricing": {"prompt": 0, "completion": 0}}) == "free_zero_price"
    assert provider_model_catalog.price_classification({"pricing": {"prompt": "0.0", "completion": "0.0"}}) == "free_zero_price"

    # Float conversions
    assert provider_model_catalog.price_classification({"pricing": {"prompt": "0.000", "completion": "0.000"}}) == "free_zero_price"
    assert provider_model_catalog.price_classification({"pricing": {"prompt": "0.001", "completion": "0.002"}}) == "paid"

    # Invalid or non-dict pricing
    assert provider_model_catalog.price_classification({"pricing": {}}) == "unknown"
    assert provider_model_catalog.price_classification({"pricing": "invalid"}) == "unknown"
    assert provider_model_catalog.price_classification({"pricing": {"prompt": "abc", "completion": "0"}}) == "unknown"


def test_get_json():
    class MockHeaders(dict):
        def items(self):
            return [("X-RateLimit-Remaining", "100"), ("User-Agent", "Ignored"), ("Retry-After", "10")]

    class MockResponse:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        @property
        def headers(self):
            return MockHeaders()
        def read(self):
            return b'{"data": []}'

    with patch("urllib.request.urlopen", return_value=MockResponse()):
        data, headers = provider_model_catalog.get_json("https://example.com", token="tok")
        assert data == {"data": []}
        assert headers == {"x-ratelimit-remaining": "100", "retry-after": "10"}


def test_poll():
    mock_payload = {
        "data": [
            {
                "id": "test/free-model",
                "name": "Test Free Model",
                "pricing": {"prompt": "0", "completion": "0"},
                "context_length": 4096,
                "max_output_tokens": 2048,
            },
            {
                "id": "ox-alpha",
                "name": "OX Alpha Live",
                "pricing": {"prompt": "0", "completion": "0"},
            }
        ]
    }
    with patch("scripts.provider_model_catalog.get_json", return_value=(mock_payload, {"x-ratelimit-limit": "1000"})):
        rows, headers = provider_model_catalog.poll("felo", "dummy_token")
        assert len(rows) == 2
        assert rows[0]["id"] == "test/free-model"
        assert rows[0]["pricing_classification"] == "free_zero_price"
        assert rows[0]["access_classification"] == "catalog_pricing_only"

        # Test trial model overrides and hoisting
        assert rows[1]["id"] == "ox-alpha"
        assert rows[1]["access_classification"] == "free_trial"
        assert rows[1]["cadence"] == "trial"
        assert headers == {"x-ratelimit-limit": "1000"}


def test_main(tmp_path):
    output_file = tmp_path / "catalog.json"
    mock_payload = {
        "data": [
            {
                "id": "openrouter/free",
                "pricing": {"prompt": "0", "completion": "0"},
            }
        ]
    }
    with patch.dict("os.environ", {"OPENROUTER_API_KEY": "sk-test"}, clear=True), \
         patch("scripts.provider_model_catalog.get_json", return_value=(mock_payload, {})):
        ret = provider_model_catalog.main(["--providers", "openrouter", "--output", str(output_file)])
        # Verify exit code 0 when catalog rows are parsed
        assert ret == 0
        assert output_file.exists()
