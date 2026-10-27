"""Tests for deepcli.llm adapters — fake transports only, no network,
no real credentials."""
import asyncio

import pytest

from deepcli.llm.adapters.gemini import Adapter as GeminiAdapter
from deepcli.llm.adapters.openrouter import Adapter as OpenRouterAdapter
from deepcli.observatory import mev, trial


def _gemini_transport(url, headers, payload):
    assert "generateContent" in url
    assert "gemini-2.5-flash" in url
    assert headers.get("x-goog-api-key") == "test-key"
    assert payload["contents"][0]["parts"][0]["text"] == "hi"
    return {
        "candidates": [{"content": {"parts": [{"text": "hello "},
                                              {"text": "world"}]}}],
        "usageMetadata": {"promptTokenCount": 5, "candidatesTokenCount": 2},
    }


def _openrouter_transport(url, headers, payload):
    assert headers["Authorization"] == "Bearer test-key"
    assert payload["model"] == "openrouter/free"
    return {
        "choices": [{"message": {"content":
                                 '{"scores": {"quality": 0.9}, '
                                 '"rationale": "fine"}'}}],
        "usage": {"prompt_tokens": 9, "completion_tokens": 4},
    }


def test_gemini_adapter_parses_response():
    a = GeminiAdapter(transport=_gemini_transport, api_key="test-key")
    r = asyncio.run(a.ask("hi"))
    assert r.text == "hello world"
    assert (r.tokens_in, r.tokens_out) == (5, 2)


def test_openrouter_adapter_parses_response():
    a = OpenRouterAdapter(transport=_openrouter_transport, api_key="test-key")
    r = asyncio.run(a.ask("judge this"))
    assert "scores" in r.text
    assert (r.tokens_in, r.tokens_out) == (9, 4)


def test_missing_key_raises_with_env_name(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    a = GeminiAdapter(transport=_gemini_transport)
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        asyncio.run(a.ask("hi"))


def test_mev_default_client_routes_and_sets_model(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "x")
    client = mev._default_client("gemini", "gemini-2.5-flash")
    assert isinstance(client, GeminiAdapter)
    assert client.model == "gemini-2.5-flash"


def test_full_trial_with_real_adapters_fake_transports(monkeypatch, tmp_path):
    """End to end Mev -> Jev -> Kev -> Laya using the real adapter classes
    with transports stubbed: the quartet's first executable wiring."""
    import deepcli.observatory.leaderboard as lb_mod
    monkeypatch.setattr(lb_mod, "_DEFAULT", tmp_path / "lb.json")
    monkeypatch.setattr(trial, "HS_URL", "http://127.0.0.1:1")

    def factory(provider, model):
        if provider == "gemini":
            ad = GeminiAdapter(transport=_gemini_transport, api_key="test-key")
        else:
            ad = OpenRouterAdapter(transport=_openrouter_transport,
                                   api_key="test-key")
        ad.model = model
        return ad

    record = asyncio.run(trial.run_trial(
        "hi", [("gemini", "gemini-2.5-flash")],
        {"quality": "0..1"}, ("openrouter", "openrouter/free"),
        client_factory=factory))
    assert record["artifacts"][0]["ok"] is True
    assert record["artifacts"][0]["text"] == "hello world"
    assert record["jevs"][0]["scores"] == {"quality": 0.9}
    assert record["winner"]["provider"] == "gemini"
