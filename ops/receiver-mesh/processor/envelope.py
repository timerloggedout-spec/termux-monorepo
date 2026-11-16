"""Receiver Mesh — envelope validation shared by the Actions processor.

Design of record: docs/ops/RECEIVER-MESH.md. Offline, stdlib only.
The Cloudflare/Vercel legs normalize; this module is the processor-side
re-check so a dispatch is never trusted on shape alone.
"""
from __future__ import annotations

import hashlib
import hmac
import ipaddress
import json

ENVELOPE_FIELDS = (
    "source", "event", "delivery_id", "received_at",
    "repo", "action", "actor", "object_id",
)
REQUIRED = ("source", "event", "delivery_id", "received_at")


def verify_github_signature(secret: str, raw_body: bytes, header_value: str) -> bool:
    expected = "sha256=" + hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header_value or "")


def ip_in_ranges(ip: str, ranges: list[str]) -> bool:
    """True if `ip` falls in any CIDR. IPv6 ranges are supported here;
    unparsable input is False (caller decides fail-open/closed)."""
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False
    for cidr in ranges:
        try:
            if addr in ipaddress.ip_network(cidr, strict=False):
                return True
        except ValueError:
            continue
    return False


def validate_envelope(envelope: dict) -> list[str]:
    """Return a list of faults; empty list = valid."""
    faults: list[str] = []
    if not isinstance(envelope, dict):
        return ["envelope_not_object"]
    for field in REQUIRED:
        if not envelope.get(field):
            faults.append(f"missing:{field}")
    extra = set(envelope) - set(ENVELOPE_FIELDS)
    if extra:
        faults.append(f"unexpected_fields:{','.join(sorted(extra))}")
    return faults


def envelope_from_dispatch(payload: dict) -> dict:
    """Extract the envelope from a repository_dispatch client_payload."""
    env = (payload or {}).get("envelope")
    if env is None:
        raise ValueError("dispatch payload carries no envelope")
    faults = validate_envelope(env)
    if faults:
        raise ValueError("invalid envelope: " + ";".join(faults))
    return env


if __name__ == "__main__":  # tiny CLI for the workflow: validate stdin JSON
    import sys

    data = json.load(sys.stdin)
    try:
        print(json.dumps(envelope_from_dispatch(data)))
    except ValueError as exc:
        print(f"::error::{exc}")
        raise SystemExit(1)
