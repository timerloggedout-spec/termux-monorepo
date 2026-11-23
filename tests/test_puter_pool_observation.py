from __future__ import annotations

from scripts import puter_pool_observation as observer


def test_collect_observation_projects_only_aggregate_runtime_fields(monkeypatch):
    monkeypatch.setattr(observer, "fetch_models", lambda *a: [{"id": "model-a"}, {"id": "model-b"}])
    snapshots = {
        "/api/stats": {"totalAccounts": 4, "activeAccounts": 3, "totalRequests": 19, "successfulRequests": 17, "failedRequests": 2, "averageLatency": 220, "strategy": "least-used", "apiKey": "secret", "accountTokens": ["secret"]},
        "/api/queue": {"queuedRequests": 2, "activeRequests": 1, "prompt": "private"},
        "/healthz": {"status": "ok", "timestamp": "2026-11-23T00:00:00Z"},
        "/readyz": {"status": "ready", "activeAccounts": 3},
    }
    monkeypatch.setattr(observer, "_fetch_json", lambda _base, path, _timeout, _key: snapshots[path])
    result = observer.collect_observation(api_key="test-key")
    assert result["provider_id"] == "g4f.puter"
    assert result["pool"]["counters"]["totalRequests"] == 19
    assert result["pool"]["counters"]["queuedRequests"] == 2
    assert result["pool"]["model_ids"] == ["model-a", "model-b"]
    assert result["quota"]["status"] == "unknown"
    assert result["quota"]["used"] is None
    assert "secret" not in str(result)
    assert "private" not in str(result)
    assert result["privacy"]["request_history_collected"] is False


def test_invalid_counters_are_omitted_as_null(monkeypatch):
    monkeypatch.setattr(observer, "fetch_models", lambda *a: [])
    snapshots = {path: {} for path in observer.PATHS}
    snapshots["/api/stats"] = {"totalRequests": -1, "activeAccounts": True}
    monkeypatch.setattr(observer, "_fetch_json", lambda _base, path, _timeout, _key: snapshots[path])
    result = observer.collect_observation()
    assert result["pool"]["counters"]["totalRequests"] is None
    assert result["pool"]["counters"]["activeAccounts"] is None

