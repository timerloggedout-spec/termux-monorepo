"""Operator receipt written after a cycle. Not an Issue #175 comment."""
from __future__ import annotations

from typing import Any

from ml.pipelines.command_center.session import current


def receipt(kind: str, payload: dict[str, Any]) -> dict[str, Any]:
    sess = current()
    return {
        "kind": kind,
        "session": sess.session_id,
        "agent": sess.agent,
        "version": sess.version,
        "product_sha": sess.product_sha,
        "payload": payload,
        "pulse_comment": False,
    }
