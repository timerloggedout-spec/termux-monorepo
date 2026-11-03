import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import provider_consumption_reconcile as pcr  # noqa: E402


def snapshot(at, used, reset="r1", scope="app:1", unit="requests"):
    return {"provider": "github", "scope": scope, "resource": "core",
            "unit": unit, "reset_epoch": reset, "observed_at": at,
            "used": used, "snapshot_id": "s-" + at}


def event(at, value, reset="r1", scope="app:1", unit="requests",
          match="exact", status="established"):
    return {"provider": "github", "scope": scope, "resource": "core",
            "unit": unit, "reset_epoch": reset, "occurred_at": at,
            "usage_value": value, "match": match, "status": status,
            "event_id": "e-" + at}


def coverage(start, end, reset="r1", scope="app:1", unit="requests",
             status="complete"):
    return {"provider": "github", "scope": scope, "resource": "core",
            "unit": unit, "reset_epoch": reset, "window_start": start,
            "window_end": end, "coverage_status": status,
            "source_ref": "coverage-fixture"}


def doc(events=None, cov=None, snaps=None):
    start, end = "2026-11-02T10:00:00Z", "2026-11-02T10:05:00Z"
    return {"snapshots": snaps or [snapshot(start, 10), snapshot(end, 15)],
            "events": events or [event("2026-11-02T10:02:00Z", 5)],
            "coverage": cov or [coverage(start, end)]}


def test_exact_delta_reconciles_and_is_deterministic():
    first = pcr.reconcile(doc())
    assert first == pcr.reconcile(doc())
    assert first["findings"][0]["kind"] == "reconciled"
    assert first["findings"][0]["residual"] == 0


def test_positive_residual_is_not_allocated():
    result = pcr.reconcile(doc(events=[event("2026-11-02T10:02:00Z", 2)]))
    finding = result["findings"][0]
    assert finding["kind"] == "positive_residual"
    assert finding["residual"] == 3
    assert "consumer" not in finding


def test_negative_residual_is_distinct():
    result = pcr.reconcile(doc(events=[event("2026-11-02T10:02:00Z", 8)]))
    finding = result["findings"][0]
    assert finding["kind"] == "negative_residual"
    assert finding["residual"] == -3


def test_reset_epoch_boundary_is_not_subtracted():
    start, end = "2026-11-02T10:00:00Z", "2026-11-02T10:05:00Z"
    result = pcr.reconcile(doc(snaps=[snapshot(start, 90, "r1"),
                                     snapshot(end, 3, "r2")]))
    assert result["findings"][0]["kind"] == "reset_boundary"


def test_unexplained_counter_decrease_is_regression():
    start, end = "2026-11-02T10:00:00Z", "2026-11-02T10:05:00Z"
    result = pcr.reconcile(doc(snaps=[snapshot(start, 90), snapshot(end, 3)]))
    assert result["findings"][0]["kind"] == "counter_regression"


def test_scope_mismatch_is_not_compared():
    start, end = "2026-11-02T10:00:00Z", "2026-11-02T10:05:00Z"
    result = pcr.reconcile(doc(cov=[coverage(start, end, scope="app:2")]))
    finding = result["findings"][0]
    assert finding["kind"] == "scope_mismatch"
    assert "residual" not in finding


def test_incomplete_coverage_keeps_delta_unattributed():
    start, end = "2026-11-02T10:00:00Z", "2026-11-02T10:05:00Z"
    result = pcr.reconcile(doc(cov=[coverage(start, end, status="partial")]))
    finding = result["findings"][0]
    assert finding["kind"] == "incomplete_event_coverage"
    assert "residual" not in finding


def test_activity_proxy_is_excluded_from_consumption():
    result = pcr.reconcile(doc(events=[event(
        "2026-11-02T10:02:00Z", 5, match="activity-proxy", status="activity-only")]))
    finding = result["findings"][0]
    assert finding["kind"] == "positive_residual"
    assert finding["attributed_total"] == 0
    assert finding["activity_events_excluded"] == 1


def test_missing_baseline_is_explicit():
    result = pcr.reconcile(doc(snaps=[snapshot("2026-11-02T10:00:00Z", 10)]))
    assert result["findings"][0]["kind"] == "missing_baseline"


def test_stale_snapshot_is_explicit():
    result = pcr.reconcile(doc(), now="2026-11-02T11:00:00Z",
                          stale_after_seconds=60)
    assert result["findings"][0]["kind"] == "stale_reading"


def test_duplicate_events_are_idempotent():
    repeated = event("2026-11-02T10:02:00Z", 5)
    result = pcr.reconcile(doc(events=[repeated, repeated]))
    finding = result["findings"][0]
    assert finding["kind"] == "reconciled"
    assert finding["attributed_total"] == 5


def test_conflicting_event_replay_is_rejected():
    first = event("2026-11-02T10:02:00Z", 5)
    replay = dict(first, usage_value=7)
    try:
        pcr.reconcile(doc(events=[first, replay]))
    except ValueError as exc:
        assert "conflicting replay" in str(exc)
    else:
        raise AssertionError("conflicting replay must be rejected")


def test_invalid_naive_timestamp_rejected():
    bad = doc()
    bad["snapshots"][0]["observed_at"] = "2026-11-02T10:00:00"
    try:
        pcr.reconcile(bad)
    except ValueError as exc:
        assert "timezone" in str(exc)
    else:
        raise AssertionError("naive timestamp must be rejected")
