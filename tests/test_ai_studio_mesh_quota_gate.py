"""Tests for ops/ai-studio-mesh/quota_gate.py (stdlib only)."""
import importlib.util
import pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "quota_gate", ROOT / "ops" / "ai-studio-mesh" / "quota_gate.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

NOW = datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc)


def rows(model, n, ts="2026-10-30T01:00:00Z"):
    return [{"model": model, "ts": ts} for _ in range(n)]


def test_allow_within_budget():
    d = gate.decide("gemini-3.8-flash", rows("gemini-3.8-flash", 19), NOW)
    assert d["decision"] == "ALLOW" and d["used_today"] == 19


def test_defer_at_budget():
    d = gate.decide("gemini-3.8-flash", rows("gemini-3.8-flash", 20), NOW)
    assert d["decision"] == "DEFER" and d["reason"] == "rpd_exhausted"


def test_yesterday_does_not_count():
    old = rows("gemini-3.8-flash", 20, ts="2026-10-29T23:00:00Z")
    d = gate.decide("gemini-3.8-flash", old, NOW)
    assert d["decision"] == "ALLOW" and d["used_today"] == 0


def test_paid_model_defers():
    d = gate.decide("deep-research-preview-04-2026", [], NOW)
    assert d["decision"] == "DEFER" and d["reason"] == "paid_or_zero_budget"


def test_unverified_budget_defers():
    d = gate.decide("gemini-3.1-pro-preview", [], NOW)
    assert d["decision"] == "DEFER" and d["reason"] == "budget_unverified"


def test_unknown_model_defers():
    d = gate.decide("gemini-9-nonexistent", [], NOW)
    assert d["decision"] == "DEFER" and d["reason"] == "model_unknown"


def test_other_models_do_not_count():
    d = gate.decide("gemini-3.8-flash",
                    rows("gemini-3.8-flash-tts", 50), NOW)
    assert d["decision"] == "ALLOW" and d["used_today"] == 0
