"""Unit tests for scripts/live_catalog_feed.py classification + ranking."""
from __future__ import annotations

import importlib.util
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
