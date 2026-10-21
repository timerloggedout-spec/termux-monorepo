"""Optional pinned swarms-rs worker boundary (THUB-015).

No cargo invocation, SDK import, or model request occurs during a dry-run.
This is process/state isolation for a trusted SDK, not a security sandbox.
"""
from __future__ import annotations

import ipaddress
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Mapping
from urllib.parse import urlsplit

from src.swarms_adapter import validate_config

DEFAULT_BASE = "http://127.0.0.1:8787/v1"


def validate_base(base: str) -> str:
    """Require TLS off loopback; never accept URL-embedded credentials."""
    try:
        parsed = urlsplit(base)
        port = parsed.port  # Validate malformed ports before spawning the worker.
        host = parsed.hostname
        if not host or parsed.username is not None or parsed.password is not None:
            raise ValueError
        if parsed.query or parsed.fragment or parsed.scheme not in {"http", "https"}:
            raise ValueError
        if port is not None and not 1 <= port <= 65535:
            raise ValueError
        loopback = host == "localhost"
        try:
            loopback = loopback or ipaddress.ip_address(host).is_loopback
        except ValueError:
            pass
        if parsed.scheme == "http" and not loopback:
            raise ValueError
        if any(char.isspace() for char in base) or "\\" in base:
            raise ValueError
    except (ValueError, TypeError, AttributeError):
        raise ValueError("LLM_API_HUB_BASE must be HTTPS (or HTTP loopback), without credentials, query, or fragment") from None
    return base.rstrip("/") + "/"


def _positive_integer(name: str, value: Any) -> int:
    if type(value) is not int or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


def run(config: Mapping[str, Any], *, binary: str | os.PathLike[str] | None = None,
        timeout_seconds: int = 120, max_tokens: int = 8192) -> dict[str, Any]:
    """Execute only an explicitly installed trusted worker in a fresh private cwd.

    Upstream prints on stdout despite quiet settings, so result.json is a separate
    child-to-parent channel. Both child diagnostic streams are forwarded to stderr.
    The outer deadline includes a small grace period for the worker's own deadline.
    """
    cfg = validate_config(config)
    timeout_seconds = _positive_integer("timeout_seconds", timeout_seconds)
    max_tokens = _positive_integer("max_tokens", max_tokens)
    result: dict[str, Any] = {
        "status": "dry_run", "backend": "swarms-rs", **cfg,
        "timeout_seconds": timeout_seconds, "max_tokens": max_tokens,
        "state_policy": "temporary subprocess workspace, removed after execution",
    }
    if not cfg["execute"]:
        result["note"] = "Offline dry-run; an installed worker, execute=true, and explicit model are required for model calls."
        return result

    base = validate_base(os.environ.get("LLM_API_HUB_BASE", DEFAULT_BASE))
    requested = os.fspath(binary) if binary is not None else os.environ.get("SWARMS_RS_BINARY", "")
    if not requested:
        raise ValueError("Set SWARMS_RS_BINARY or --binary to an explicitly installed Rust worker; no automatic build or download")
    located = shutil.which(requested)
    if located is None:
        raise ValueError("Rust worker is missing or not executable")
    executable = str(Path(located).resolve())
    payload = {**cfg, "timeout_seconds": timeout_seconds, "max_tokens": max_tokens}
    with tempfile.TemporaryDirectory(prefix="termux-swarms-rs-") as state:
        env = dict(os.environ)
        env.update({"LLM_API_HUB_BASE": base, "HOME": state, "TMPDIR": state})
        try:
            proc = subprocess.run([executable], input=json.dumps(payload), text=True,
                                  capture_output=True, cwd=state, env=env,
                                  timeout=timeout_seconds + 5, check=False)
        except subprocess.TimeoutExpired:
            raise RuntimeError("Rust worker exceeded its execution deadline and was terminated") from None
        for stream in (proc.stdout, proc.stderr):
            if stream:
                print(stream, file=sys.stderr, end="" if stream.endswith("\n") else "\n")
        path = Path(state) / "result.json"
        try:
            response = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            raise RuntimeError(f"Rust worker returned no valid JSON result (exit {proc.returncode})") from None
        if not isinstance(response, dict):
            raise RuntimeError("Rust worker returned an invalid result object")
        if proc.returncode != 0 or response.get("status") != "complete":
            error = response.get("error")
            raise RuntimeError(error if isinstance(error, str) and error else f"Rust worker failed (exit {proc.returncode})")
        if response.get("backend") != "swarms-rs" or "output" not in response:
            raise RuntimeError("Rust worker returned an incomplete success result")
        result.update(response)
        result["provider"] = "llm_api_hub OpenAI-compatible endpoint"
    return result
