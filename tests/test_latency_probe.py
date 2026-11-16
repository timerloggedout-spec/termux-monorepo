"""Tests for ops/latency/probe.py — canned curl output only, no live network."""

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "latency_probe", REPO_ROOT / "ops" / "latency" / "probe.py"
)
probe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(probe)


# --- curl output parsing ---------------------------------------------------

def test_parse_curl_output_segments():
    # namelookup, connect, appconnect, starttransfer, total (s), http_code
    rec = probe.parse_curl_output("0.012000 0.045000 0.089000 0.150000 0.151000 200")
    assert rec["dns_ms"] == 12.0
    assert rec["tcp_ms"] == 33.0  # segment: connect - namelookup
    assert rec["tls_ms"] == 44.0  # segment: appconnect - connect
    assert rec["ttfb_ms"] == 150.0  # absolute from request start
    assert rec["total_ms"] == 151.0
    assert rec["http_status"] == 200


def test_parse_curl_output_no_tls():
    rec = probe.parse_curl_output("0.010000 0.030000 0.000000 0.080000 0.081000 200")
    assert rec["tls_ms"] == 0.0


def test_parse_curl_output_rejects_garbage():
    with pytest.raises(ValueError):
        probe.parse_curl_output("not a timing line")
    with pytest.raises(ValueError):
        probe.parse_curl_output("")


def test_parse_curl_output_rejects_no_response():
    with pytest.raises(ValueError):
        probe.parse_curl_output("0.010000 0.000000 0.000000 0.000000 0.010000 000")


# --- median math -------------------------------------------------------------

def _run(total, ttfb=0.0, status=200):
    return {"dns_ms": 1.0, "tcp_ms": 1.0, "tls_ms": 1.0,
            "ttfb_ms": ttfb, "total_ms": total, "http_status": status}


def test_median_record_picks_middle_values():
    med = probe.median_record([_run(100.0), _run(300.0), _run(200.0)])
    assert med["total_ms"] == 200.0


def test_median_record_status_from_median_run():
    med = probe.median_record([_run(100.0, status=200),
                               _run(300.0, status=503),
                               _run(200.0, status=404)])
    assert med["http_status"] == 404  # status of the median-total run


def test_median_record_ignores_errors_and_all_error_is_none():
    med = probe.median_record([{"error": "boom"}, _run(100.0), _run(300.0)])
    assert med["total_ms"] == 200.0  # median of the two successful runs
    assert probe.median_record([{"error": "a"}, {"error": "b"}]) is None


# --- state gate --------------------------------------------------------------

def _rec(name, total, ok=True):
    if not ok:
        return {"name": name, "ok": False, "error": "unreachable",
                "median": None, "http_status": None}
    return {"name": name, "ok": True, "http_status": 200,
            "median": {"dns_ms": 1.0, "tcp_ms": 1.0, "tls_ms": 1.0,
                       "ttfb_ms": total, "total_ms": total}}


def test_gate_below_threshold_commits_nothing():
    deltas = probe.gate_deltas([_rec("a", 1200.0)], [_rec("a", 1000.0)])
    assert deltas == []  # +20% is not >50%


def test_gate_above_threshold_flags_delta():
    deltas = probe.gate_deltas([_rec("a", 1601.0)], [_rec("a", 1000.0)])
    assert len(deltas) == 1
    assert deltas[0]["kind"] == "delta"
    assert deltas[0]["target"] == "a"


def test_gate_absolute_floor_blocks_small_surface_noise():
    # +100% relative but only +100 ms absolute: the AND condition must hold.
    deltas = probe.gate_deltas([_rec("a", 200.0)], [_rec("a", 100.0)])
    assert deltas == []


def test_gate_improvement_also_counts():
    deltas = probe.gate_deltas([_rec("a", 300.0)], [_rec("a", 1000.0)])
    assert len(deltas) == 1 and deltas[0]["kind"] == "delta"


def test_gate_error_surface_flags():
    deltas = probe.gate_deltas([_rec("a", 0.0, ok=False)], [_rec("a", 1000.0)])
    assert len(deltas) == 1 and deltas[0]["kind"] == "error"


def test_gate_recovered_surface_flags_state_change():
    deltas = probe.gate_deltas([_rec("a", 500.0)], [_rec("a", 0.0, ok=False)])
    assert len(deltas) == 1 and deltas[0]["kind"] == "state-change"


def test_gate_new_target_without_baseline_is_ignored():
    deltas = probe.gate_deltas([_rec("new", 5000.0)], [_rec("a", 1000.0)])
    assert deltas == []
