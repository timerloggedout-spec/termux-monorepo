from unittest.mock import patch, MagicMock
import json
import pytest

from scripts import live_catalog_feed


def test_is_free():
    assert live_catalog_feed._is_free("qwen/qwen3-coder:free", {}) is True
    assert live_catalog_feed._is_free("stealth/ox-alpha", None) is True
    assert live_catalog_feed._is_free("unknown/model", None) is False
    assert live_catalog_feed._is_free("custom/model", {"prompt": 0, "completion": 0}) is True
    assert live_catalog_feed._is_free("custom/model", {"prompt": 1, "completion": 0}) is False
    assert live_catalog_feed._is_free("custom/model", None, access="free_trial") is True


def test_poll_provider_missing_secret(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    rows, state = live_catalog_feed.poll_provider("openrouter")
    assert rows == []
    assert state == "missing_secret"


def test_poll_provider_success(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    mock_response_data = json.dumps({
        "data": [
            {"id": "qwen/qwen3-coder:free", "pricing": {"prompt": 0, "completion": 0}, "context_length": 32000},
            {"id": "paid/model", "pricing": {"prompt": 0.01, "completion": 0.02}},
        ]
    }).encode("utf-8")

    mock_resp = MagicMock()
    mock_resp.read.return_value = mock_response_data
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        rows, state = live_catalog_feed.poll_provider("openrouter")
        assert state == "live"
        assert len(rows) == 2
        assert rows[0]["id"] == "qwen/qwen3-coder:free"
        assert rows[0]["free"] is True
        assert rows[1]["id"] == "paid/model"
        assert rows[1]["free"] is False


def test_load_eligible(tmp_path, monkeypatch):
    monkeypatch.setenv("COUNTER_DIR", str(tmp_path))
    monkeypatch.setenv("OPENROUTER_API_KEY", "key1")
    monkeypatch.setenv("FELO_AI_API", "key2")

    mock_or_data = json.dumps({"data": [{"id": "meta-llama/llama-3.3-70b-instruct:free", "pricing": {}}]}).encode("utf-8")
    mock_felo_data = json.dumps({"data": [{"id": "ox-alpha", "pricing": None}]}).encode("utf-8")

    def mock_urlopen(req, timeout=12):
        resp = MagicMock()
        url = req.full_url
        if "openrouter" in url:
            resp.read.return_value = mock_or_data
        else:
            resp.read.return_value = mock_felo_data
        resp.__enter__.return_value = resp
        return resp

    with patch("urllib.request.urlopen", side_effect=mock_urlopen):
        doc = live_catalog_feed.load_eligible(providers=["openrouter", "felo"], cache_dir=str(tmp_path))
        assert doc["catalog_state"] == "live"
        assert len(doc["eligible"]) >= 2
        assert "openrouter" in doc["eligible_ids_by_provider"]
        assert "felo" in doc["eligible_ids_by_provider"]


def test_peer_candidates_for_role(monkeypatch):
    monkeypatch.setenv("OMNI_API_KEY", "omni-key")
    feed = {
        "eligible": [
            {"provider": "openrouter", "id": "meta-llama/llama-3.3-70b-instruct:free"},
            {"provider": "openrouter", "id": "qwen/qwen3-coder:free"},
            {"provider": "felo", "id": "ox-alpha"},
        ]
    }
    peers_review = live_catalog_feed.peer_candidates_for_role("review", feed)
    assert ("omni", "auto/best-free") in peers_review
    assert ("openrouter", "qwen/qwen3-coder:free") in peers_review
