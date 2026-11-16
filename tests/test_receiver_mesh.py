"""Offline unit tests for the Receiver Mesh envelope module.

Run: python3 -m pytest tests/test_receiver_mesh.py
"""
import hashlib
import hmac
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ops" / "receiver-mesh" / "processor"))

from envelope import envelope_from_dispatch, ip_in_ranges, validate_envelope, verify_github_signature

# The three ranges added by the 2026-10-29 GitHub changelog, plus a legacy one.
META_HOOKS = ["192.30.252.0/22", "9.234.98.160/28", "9.234.98.176/28", "9.234.106.48/28", "2a0a:a440::/29"]


def test_signature_roundtrip():
    body = b'{"action":"opened"}'
    sig = "sha256=" + hmac.new(b"s3cret", body, hashlib.sha256).hexdigest()
    assert verify_github_signature("s3cret", body, sig)
    assert not verify_github_signature("wrong", body, sig)
    assert not verify_github_signature("s3cret", body, "")


def test_new_meta_ranges_accepted():
    assert ip_in_ranges("9.234.98.165", META_HOOKS)
    assert ip_in_ranges("9.234.98.180", META_HOOKS)
    assert ip_in_ranges("9.234.106.55", META_HOOKS)
    assert ip_in_ranges("192.30.252.10", META_HOOKS)


def test_foreign_ip_rejected():
    assert not ip_in_ranges("203.0.113.9", META_HOOKS)
    assert not ip_in_ranges("not-an-ip", META_HOOKS)


def test_envelope_validation():
    good = {"source": "github", "event": "issues", "delivery_id": "d1", "received_at": "2026-10-29T00:00:00Z"}
    assert validate_envelope(good) == []
    assert "missing:event" in validate_envelope({"source": "github", "delivery_id": "d1", "received_at": "x"})
    assert any(f.startswith("unexpected_fields") for f in validate_envelope({**good, "raw_payload": {}}))


def test_dispatch_extraction():
    payload = {"envelope": {"source": "github", "event": "ping", "delivery_id": "d9", "received_at": "t"}}
    assert envelope_from_dispatch(payload)["delivery_id"] == "d9"
