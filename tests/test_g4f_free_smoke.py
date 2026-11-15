from scripts.ops.g4f_free_smoke import build_receipt, select_entries


def test_select_entries_uses_finite_offset_window():
    assert select_entries(list(range(10)), 3, 4) == [3, 4, 5, 6]


def test_select_entries_returns_empty_when_offset_exceeds_population():
    assert select_entries(["a", "b"], 9, 2) == []


def test_select_entries_rejects_negative_offset_or_limit():
    for offset, limit in [(-1, 1), (0, -1)]:
        try:
            select_entries([1, 2], offset, limit)
        except ValueError:
            pass
        else:
            raise AssertionError("negative batch bounds must fail")


def test_g4f_receipt_is_sanitized_and_never_dispatch_eligible():
    results = [
        {"provider": "ProviderA", "model": "model-1", "inference_ok": True, "latency_s": 1.2, "error": None},
        {"provider": "ProviderB", "model": "model-2", "inference_ok": False, "latency_s": 2.3, "error": "TimeoutError"},
    ]
    receipt = build_receipt(
        results, source="universe", offset=200, limit=200,
        source_population_total=9588, workers=6, timeout_s=45, deadline_s=1500,
        observed_at="2026-11-15T12:00:00Z",
    )
    assert receipt["attempted"] == 2
    assert receipt["inference_ok"] == 1
    assert receipt["providers_ok"] == ["ProviderA"]
    assert receipt["offset"] == 200 and receipt["limit"] == 200
    assert receipt["source_population_total"] == 9588
    assert receipt["dispatch_eligible"] is False
    assert receipt["quota_class"] == "unclassified"
    assert "response" not in receipt and "completion" not in receipt
    assert all("content" not in row and "api_key" not in row for row in receipt["results"])
