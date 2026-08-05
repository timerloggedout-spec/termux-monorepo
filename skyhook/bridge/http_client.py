"""Minimal Jules HTTP helpers — stdlib only (B160V-safe).

Rewrites the *protocol* of jules-dispatch-cli / jules-mcp-server without Bun,
FastMCP, or cargo. Optional: only used when JULES_API_KEY is set.
Does not call the network unless invoke_* is used.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

DEFAULT_BASE = "https://jules.googleapis.com/v1alpha"


def _api_key() -> str:
    """Returns the Jules API key from environment variables if present."""
    for name in ("JULES_API_KEY", "GOOGLE_JULES_API_KEY"):
        val = os.environ.get(name, "").strip()
        if val:
            return val
    return ""


def _headers() -> Dict[str, str]:
    """Generates standard request headers including API key authentication."""
    key = _api_key()
    if not key:
        raise RuntimeError("JULES_API_KEY not set")
    return {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": key,
        "Accept": "application/json",
    }


def request_json(
    method: str,
    path: str,
    *,
    body: Optional[Dict[str, Any]] = None,
    base: Optional[str] = None,
    timeout: float = 60.0,
) -> Dict[str, Any]:
    """Low-level JSON request. path is relative (e.g. 'sessions').

    Args:
        method: HTTP request method (e.g. 'GET', 'POST').
        path: Path relative to the base URL.
        body: JSON request payload body.
        base: Custom base URL override.
        timeout: Network timeout in seconds.

    Returns:
        The decoded response JSON as a dictionary.
    """
    url = (base or os.environ.get("JULES_API_BASE", DEFAULT_BASE)).rstrip("/") + "/" + path.lstrip("/")
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=_headers(), method=method.upper())
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Jules API {method} {path}: HTTP {e.code}: {err_body[:500]}") from e


def build_create_session_body(
    prompt: str,
    source: str,
    *,
    starting_branch: Optional[str] = None,
    title: Optional[str] = None,
    require_plan_approval: bool = False,
) -> Dict[str, Any]:
    """Map skyhook plan fields → API-ish body (exact schema may evolve).

    Args:
        prompt: Task prompt instructions.
        source: Jules source id (e.g. sources/...).
        starting_branch: Base branch name.
        title: Task session title.
        require_plan_approval: If True, halts for plan approval.

    Returns:
        A formatted JSON payload dictionary.
    """
    body: Dict[str, Any] = {
        "prompt": prompt,
        "source": source,
        "requirePlanApproval": require_plan_approval,
    }
    if starting_branch:
        body["startingBranch"] = starting_branch
    if title:
        body["title"] = title
    return body


# Session states mirrored from jules-dispatch-cli_fork agent guide (protocol).
TERMINAL_OR_WAIT = frozenset(
    {
        "COMPLETED",
        "FAILED",
        "AWAITING_PLAN_APPROVAL",
        "AWAITING_USER_FEEDBACK",
        "PAUSED",
    }
)
