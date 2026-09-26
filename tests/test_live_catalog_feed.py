"""Unit tests for scripts/live_catalog_feed.py classification + ranking."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "live_catalog_feed", ROOT / "scripts" / "live_catalog_feed.py"
)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(mod)


def test_is_free_suffix_and_zero_price() -> None:
    assert mod._is_free("meta/llama-3:free", {"prompt": "1", "completion": "1"}) is True
    assert mod._is_free("ox-alpha", None) is True
    assert mod._is_free("paid/model", {"prompt": "0.1", "completion": "0"}) is False
    assert mod._is_free("trial/x", None, access="free_trial") is True


def test_pricing_classification() -> None:
    assert mod._pricing_classification("x:free", True, None) == "free_suffix"
    assert mod._pricing_classification("ox-alpha", True, "free_trial") == "free_trial"
    assert mod._pricing_classification("zero", True, None) == "free_zero_price"
    assert mod._pricing_classification("paid", False, None) == "other"


def test_catalog_ttl_sec(monkeypatch) -> None:
    monkeypatch.delenv("CATALOG_TTL_SEC", raising=False)
    assert mod.catalog_ttl_sec() == 3600
    monkeypatch.setenv("CATALOG_TTL_SEC", "0")
    assert mod.catalog_ttl_sec() == 0
    monkeypatch.setenv("CATALOG_TTL_SEC", "nope")
    assert mod.catalog_ttl_sec() == 3600
    monkeypatch.setenv("CATALOG_TTL_SEC", "-5")
    assert mod.catalog_ttl_sec() == 0


def test_catalog_peer_limit(monkeypatch) -> None:
    monkeypatch.delenv("CATALOG_PEER_LIMIT", raising=False)
    assert mod.catalog_peer_limit() == 24
    monkeypatch.setenv("CATALOG_PEER_LIMIT", "3")
    assert mod.catalog_peer_limit() == 3
    monkeypatch.setenv("CATALOG_PEER_LIMIT", "0")
    assert mod.catalog_peer_limit() == 0
    monkeypatch.setenv("CATALOG_PEER_LIMIT", "nope")
    assert mod.catalog_peer_limit() == 24
    monkeypatch.setenv("CATALOG_PEER_LIMIT", "-2")
    assert mod.catalog_peer_limit() == 0


def test_load_eligible_one_pass_grouping(tmp_path, monkeypatch) -> None:
    def fake_poll(provider: str):
        if provider == "openrouter":
            return [
                mod._row("openrouter", "qwen/coder:free", True, None, 8_000, "openrouter:/v1/models"),
                mod._row("openrouter", "paid/gpt", False, None, 8_000, "openrouter:/v1/models"),
            ], "live"
        if provider == "felo":
            return [mod._row("felo", "ox-alpha", True, "free_trial", 1_000_000, "felo:documented-trial")], "live"
        return [], "missing_secret"

    monkeypatch.setattr(mod, "poll_provider", fake_poll)
    feed = mod.load_eligible(providers=["openrouter", "felo", "omni"], cache_dir=str(tmp_path))
    assert feed["catalog_state"] == "live"
    assert [r["id"] for r in feed["eligible"]] == ["qwen/coder:free", "ox-alpha"]
    assert feed["eligible_ids_by_provider"] == {
        "openrouter": ["qwen/coder:free"],
        "felo": ["ox-alpha"],
    }
    assert feed["provider_states"]["omni"] == "missing_secret"
    assert feed["ttl_sec"] == 3600
    assert feed["peer_limit"] == 24


def test_load_eligible_respects_zero_ttl(tmp_path, monkeypatch) -> None:
    cache = tmp_path / "live_catalog_feed.json"
    cache.write_text(json.dumps({"timestamp": 9_999_999_999, "eligible": []}), encoding="utf-8")

    def fake_poll(provider: str):
        return [mod._row(provider, f"{provider}/fresh:free", True, None, 1, f"{provider}:/v1/models")], "live"

    monkeypatch.setenv("CATALOG_TTL_SEC", "0")
    monkeypatch.setattr(mod, "poll_provider", fake_poll)
    feed = mod.load_eligible(providers=["openrouter"], cache_dir=str(tmp_path))
    assert feed["catalog_state"] == "live"
    assert feed["eligible"][0]["id"] == "openrouter/fresh:free"


def test_peer_score_code_roles() -> None:
    coder = {"provider": "openrouter", "id": "qwen/coder:free"}
    llama = {"provider": "openrouter", "id": "meta/llama-3:free"}
    assert mod.peer_score("review", coder) > mod.peer_score("review", llama)
    assert mod.peer_score("code", coder) == mod.peer_score("review", coder)
    assert mod.peer_score("implement", coder) == mod.peer_score("review", coder)


def test_peer_candidates_prefer_coder(monkeypatch) -> None:
    monkeypatch.setattr(mod, "_token", lambda _p: None)
    feed = {
        "eligible": [
            {"provider": "openrouter", "id": "meta/llama-3:free"},
            {"provider": "felo", "id": "ox-alpha"},
            {"provider": "openrouter", "id": "qwen/coder:free"},
        ]
    }
    peers = mod.peer_candidates_for_role("review", feed)
    assert peers[0] == ("openrouter", "qwen/coder:free")
    assert ("felo", "ox-alpha") in peers
    peers_code = mod.peer_candidates_for_role("code", feed)
    assert peers_code[0] == ("openrouter", "qwen/coder:free")


def test_peer_candidates_honor_limit(monkeypatch) -> None:
    monkeypatch.setattr(mod, "_token", lambda _p: None)
    feed = {
        "peer_limit": 2,
        "eligible": [
            {"provider": "openrouter", "id": "qwen/coder:free"},
            {"provider": "felo", "id": "ox-alpha"},
            {"provider": "openrouter", "id": "meta/llama-3:free"},
            {"provider": "omni", "id": "gemma-free"},
        ],
    }
    peers = mod.peer_candidates_for_role("review", feed)
    assert len(peers) == 2
    assert peers[0] == ("openrouter", "qwen/coder:free")
