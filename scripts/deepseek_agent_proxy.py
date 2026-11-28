"""Use the authenticated Origin/Pinggy Termux agent API; never call a provider directly.

The read-only preflight checks GET /v1/agent/list. Work is submitted only with
POST /v1/agent, then observed through GET /v1/agent/status/{invocation_id}.
Unreachable tunnel conditions are reported as a skip; authentication and API
contract errors remain failures.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import socket
import ssl
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

OFFLINE_HTTP_STATUSES = {502, 503, 504}
_NETWORK_FAILURES = (
    socket.gaierror,
    socket.timeout,
    TimeoutError,
    ConnectionRefusedError,
    ConnectionResetError,
    ConnectionAbortedError,
    BrokenPipeError,
)


class ProxyUnavailable(RuntimeError):
    """The Origin/Pinggy route is unavailable, so the DeepSeek-only task must skip."""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


class ProxyContractError(RuntimeError):
    """The configured proxy is reachable but its credentials or API contract failed."""


def _base_url(value: str) -> tuple[str, str, int]:
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as exc:
        raise ProxyContractError("invalid_agent_url") from exc
    if parsed.scheme not in {"https", "http"} or not parsed.hostname or parsed.username or parsed.password:
        raise ProxyContractError("invalid_agent_url")
    port = port or (443 if parsed.scheme == "https" else 80)
    return value.rstrip("/"), parsed.hostname, port


def _request_json(
    base_url: str,
    token: str,
    path: str,
    *,
    body: dict[str, Any] | None = None,
    timeout: float = 20,
) -> tuple[int, Any]:
    data = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8") if body is not None else None
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = Request(f"{base_url}{path}", data=data, headers=headers, method="POST" if body is not None else "GET")
    try:
        with urlopen(request, timeout=timeout) as response:
            status_code = getattr(response, "status", None) or response.getcode()
            raw = response.read(1_048_577)
    except HTTPError as exc:
        if exc.code in OFFLINE_HTTP_STATUSES:
            raise ProxyUnavailable(f"proxy-http-{exc.code}") from None
        raise ProxyContractError(f"proxy-http-{exc.code}") from None
    except URLError as exc:
        reason = exc.reason
        if isinstance(reason, _NETWORK_FAILURES) or (isinstance(reason, OSError) and not isinstance(reason, ssl.SSLError)):
            raise ProxyUnavailable("proxy-unreachable") from None
        raise ProxyContractError("proxy-request-failed") from None
    except _NETWORK_FAILURES:
        raise ProxyUnavailable("proxy-unreachable") from None
    except ssl.SSLError:
        raise ProxyContractError("proxy-tls-error") from None
    except OSError:
        raise ProxyContractError("proxy-request-failed") from None

    if len(raw) > 1_048_576:
        raise ProxyContractError("proxy_response_too_large")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ProxyContractError("proxy_invalid_json") from None
    return int(status_code), payload


def check_proxy(url: str | None, token: str | None) -> tuple[bool, str]:
    """Verify that the authenticated, read-only API route is reachable."""
    if not url:
        return False, "proxy-url-unset"
    if not token:
        raise ProxyContractError("agent-token-unset")
    base_url, hostname, port = _base_url(url)
    try:
        socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    except _NETWORK_FAILURES:
        return False, "proxy-dns-unresolved"
    except OSError:
        return False, "proxy-dns-unresolved"
    try:
        status_code, payload = _request_json(base_url, token, "/v1/agent/list")
    except ProxyUnavailable as exc:
        return False, exc.reason
    if status_code != 200 or not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list):
        raise ProxyContractError("proxy_list_contract_invalid")
    return True, "available"


def _skipped(reason: str, invocation_id: str | None = None) -> dict[str, Any]:
    skipped_status = {"phase": "skipped", "reason": reason}
    start = {"phase": "skipped", "reason": reason}
    if invocation_id:
        start["invocation_id"] = invocation_id
        skipped_status["invocation_id"] = invocation_id
    return {"skipped": True, "reason": reason, "start": start, "status": skipped_status}


def run_agent(
    url: str | None,
    token: str | None,
    payload: dict[str, Any],
    *,
    max_polls: int = 180,
    poll_interval: float = 10,
) -> dict[str, Any]:
    """Submit and poll a task using only the Origin/Pinggy agent endpoint."""
    if not isinstance(payload, dict) or not isinstance(payload.get("task"), str) or not payload["task"].strip():
        raise ProxyContractError("invalid_agent_payload")
    if "context" in payload and not isinstance(payload["context"], dict):
        raise ProxyContractError("invalid_agent_payload")
    if max_polls < 1 or poll_interval < 0:
        raise ProxyContractError("invalid_poll_configuration")

    available, reason = check_proxy(url, token)
    if not available:
        return _skipped(reason)
    base_url, _, _ = _base_url(url or "")

    try:
        status_code, response = _request_json(base_url, token or "", "/v1/agent", body=payload, timeout=30)
    except ProxyUnavailable as exc:
        return _skipped(exc.reason)
    if status_code != 202 or not isinstance(response, dict):
        raise ProxyContractError("proxy_start_contract_invalid")
    invocation_id = response.get("invocation_id")
    if not isinstance(invocation_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", invocation_id):
        raise ProxyContractError("proxy_invocation_id_invalid")
    if response.get("phase") != "running":
        raise ProxyContractError("proxy_start_phase_invalid")

    start = {"invocation_id": invocation_id, "phase": "running"}
    final_status: dict[str, Any] = {"invocation_id": invocation_id, "phase": "timeout"}
    for attempt in range(max_polls):
        try:
            poll_code, status = _request_json(
                base_url,
                token or "",
                f"/v1/agent/status/{invocation_id}",
                timeout=15,
            )
        except ProxyUnavailable as exc:
            return _skipped("proxy-lost", invocation_id)
        if poll_code != 200 or not isinstance(status, dict) or status.get("invocation_id") != invocation_id:
            raise ProxyContractError("proxy_status_contract_invalid")
        phase = status.get("phase")
        if not isinstance(phase, str):
            raise ProxyContractError("proxy_status_phase_invalid")
        final_status = status
        if phase in {"done", "error"}:
            break
        if attempt + 1 < max_polls:
            time.sleep(poll_interval)

    return {"skipped": False, "reason": "", "start": start, "status": final_status}


def _write_json(path: str, value: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_outputs(values: dict[str, str]) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as stream:
        for name, value in values.items():
            if "\n" in value or "\r" in value:
                raise ProxyContractError("unsafe_github_output")
            stream.write(f"{name}={value}\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="perform an authenticated read-only proxy check")
    mode.add_argument("--run", action="store_true", help="submit a task and poll its status")
    parser.add_argument("--payload", help="JSON task payload for --run")
    parser.add_argument("--start-output", default="agent_start.json")
    parser.add_argument("--status-output", default="agent_status_final.json")
    parser.add_argument("--max-polls", type=int, default=180)
    parser.add_argument("--poll-interval", type=float, default=10)
    args = parser.parse_args(argv)
    url = os.environ.get("DEEPSEEK_AGENT_URL")
    token = os.environ.get("DEEPSEEK_AGENT_TOKEN")

    try:
        if args.check:
            available, reason = check_proxy(url, token)
            _write_outputs({"available": str(available).lower(), "reason": reason})
            if available:
                print("::notice::Origin/Pinggy agent API is reachable.")
            else:
                print(f"::notice::DeepSeek proxy unavailable ({reason}); the DeepSeek-only job will be skipped.")
            return 0

        if not args.payload:
            raise ProxyContractError("payload_path_required")
        payload = json.loads(Path(args.payload).read_text(encoding="utf-8"))
        result = run_agent(url, token, payload, max_polls=args.max_polls, poll_interval=args.poll_interval)
        _write_json(args.start_output, result["start"])
        _write_json(args.status_output, result["status"])
        if result["skipped"]:
            _write_outputs({"skipped": result["reason"]})
            print(f"::notice::Origin/Pinggy agent route became unavailable ({result['reason']}); skipping DeepSeek-only work.")
            return 0
        _write_outputs({"invocation_id": result["start"]["invocation_id"]})
        phase = result["status"].get("phase")
        print(f"Origin agent completed with phase={phase}.")
        if phase != "done" or result["status"].get("rc") not in (None, 0):
            return 1
        return 0
    except (ProxyContractError, OSError, json.JSONDecodeError) as exc:
        print(f"::error::Origin agent request failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
