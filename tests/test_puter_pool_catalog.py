from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from scripts import puter_pool_catalog


def test_catalog_url_accepts_only_loopback():
    assert puter_pool_catalog._catalog_url("http://127.0.0.1:3000") == "http://127.0.0.1:3000/v1/models"
    assert puter_pool_catalog._catalog_url("http://localhost:3000/") == "http://localhost:3000/v1/models"
    with pytest.raises(ValueError):
        puter_pool_catalog._catalog_url("https://example.com")
    with pytest.raises(ValueError):
        puter_pool_catalog._catalog_url("http://127.0.0.1:3000/path")


def test_fetch_models_normalizes_and_deduplicates():
    payload = {"data": [
        {"id": "claude-test", "name": "Claude Test", "context_length": 8192},
        {"id": "claude-test", "name": "duplicate"},
        {"id": "bad\nmodel"},
        {"id": 12},
        {"id": "gemini-test", "max_output_tokens": 2048},
    ]}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def read(self, size):
            return json.dumps(payload).encode()

    class Opener:
        def open(self, request, timeout):
            assert request.full_url == "http://127.0.0.1:3000/v1/models"
            assert timeout == 8.0
            return Response()

    with patch("urllib.request.build_opener", return_value=Opener()):
        rows = puter_pool_catalog.fetch_models("http://127.0.0.1:3000")

    assert [row["id"] for row in rows] == ["claude-test", "gemini-test"]
    assert rows[0]["provider"] == "g4f/Puter"
    assert rows[0]["pricing_classification"] == "unknown"
    assert rows[0]["entitlement_verification"] == "unknown"


def test_fetch_models_rejects_invalid_shape():
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def read(self, size):
            return b'{"models": []}'

    class Opener:
        def open(self, request, timeout):
            return Response()

    with patch("urllib.request.build_opener", return_value=Opener()):
        with pytest.raises(RuntimeError, match="invalid_response_shape"):
            puter_pool_catalog.fetch_models("http://127.0.0.1:3000")


def test_catalog_reader_refuses_redirects():
    import urllib.error

    class Opener:
        def open(self, request, timeout):
            raise urllib.error.HTTPError(request.full_url, 302, "redirect", {}, None)

    with patch("urllib.request.build_opener", return_value=Opener()):
        with pytest.raises(RuntimeError, match="puter_pool_http_302"):
            puter_pool_catalog.fetch_models("http://127.0.0.1:3000")


def test_catalog_reader_sends_optional_local_api_key():
    payload = {"data": [{"id": "synthetic-model"}]}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def read(self, size):
            return json.dumps(payload).encode()

    class Opener:
        def open(self, request, timeout):
            assert request.get_header("X-api-key") == "local-test-key"
            return Response()

    with patch("urllib.request.build_opener", return_value=Opener()):
        rows = puter_pool_catalog.fetch_models("http://127.0.0.1:3000", api_key="local-test-key")
    assert [row["id"] for row in rows] == ["synthetic-model"]
