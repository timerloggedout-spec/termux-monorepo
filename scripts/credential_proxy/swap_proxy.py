#!/usr/bin/env python3
"""Credential-swap proxy — fleet-native reference core (ACE mirror).

Implements, in dependency-free Python, the one move Agent Compute
Engine's Agent Gateway makes at Google scale (see
docs/ops/AGENT-COMPUTE-ENGINE-COMPARISON-2026-10-26.md §6, mirror
proposal 2) and that the Web Adapter Foundry already makes at the
wrapper layer (`account_ref`: the handle crosses, the backing never
does):

  * The agent side holds ONLY an opaque handle (`X-Fleet-Handle`) and
    a per-handle egress policy. It never sees the real credential.
  * The proxy — a separate process the agent cannot read through —
    validates the handle, the target host, and the path against the
    policy, then swaps the real credential onto the outbound request
    at egress time.
  * Credential-shaped material arriving FROM the agent is refused:
    an agent that could supply the credential could also leak it.
  * Every decision is audit-logged WITHOUT credential values
    (names/handles only), so the log is safe to commit or ship.

This is a reference core, not a deployed service: `translate()` is
the pure decision function (unit-tested in
tests/test_credential_proxy.py); `serve()` is a minimal
http.server adapter for local evaluation. Production use requires a
real transport, TLS, and a credential source wired to the fleet's
vault route — none of which this file invents.

Config (JSON):
{
  "handles": {
    "gh-route-deepseek-cli": {
      "credential_env": "FLEET_PROXY_CRED_GH_ROUTE",
      "credential_header": "Authorization",
      "credential_prefix": "Bearer ",
      "allowed_hosts": ["api.github.com"],
      "allowed_path_prefixes": ["/repos/"]
    }
  }
}
The credential VALUE comes from the named environment variable of the
proxy process at swap time. It is never in the config file, never in
the request, and never in the audit log.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from dataclasses import dataclass, field

# Headers an agent may never use to smuggle credential material past
# the swap. Matched case-insensitively, as prefixes or exact names.
FORBIDDEN_AGENT_HEADERS = (
    "authorization",
    "proxy-authorization",
    "x-api-key",
    "api-key",
    "cookie",
)

# Value shapes that are credential-shaped wherever they appear in an
# agent-supplied header or body sample: known token prefixes and
# bearer schemes. Names are not values; this matches value shapes.
CREDENTIAL_SHAPE = re.compile(
    r"(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|gho_[A-Za-z0-9]{20,}"
    r"|sk-[A-Za-z0-9\-_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|[Bb]earer\s+[A-Za-z0-9\-_\.=]{20,})"
)


@dataclass
class Decision:
    allowed: bool
    reason: str
    outbound_headers: dict = field(default_factory=dict)
    audit: dict = field(default_factory=dict)


def load_config(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        cfg = json.load(fh)
    handles = cfg.get("handles")
    if not isinstance(handles, dict) or not handles:
        raise ValueError("config must define a non-empty 'handles' map")
    for name, h in handles.items():
        for key in ("credential_env", "credential_header", "allowed_hosts"):
            if key not in h:
                raise ValueError(f"handle {name!r} missing {key!r}")
        if CREDENTIAL_SHAPE.search(json.dumps(h)):
            raise ValueError(
                f"handle {name!r}: config carries credential-shaped material; "
                "config names the env var, never the value"
            )
    return cfg


def _audit(handle, host, path, allowed, reason):
    return {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "handle": handle,
        "host": host,
        "path": path,
        "allowed": allowed,
        "reason": reason,
    }


def translate(cfg: dict, handle: str, method: str, host: str, path: str,
              agent_headers: dict, body_sample: str = "",
              environ=None) -> Decision:
    """Decide one agent request and, if allowed, build outbound headers.

    Pure: the credential value is read from `environ` (default
    os.environ) only after every policy check passes, and is returned
    only inside `outbound_headers` — never in the audit record.
    """
    environ = os.environ if environ is None else environ
    spec = cfg.get("handles", {}).get(handle)
    if spec is None:
        return Decision(False, "unknown_handle",
                        audit=_audit(handle, host, path, False, "unknown_handle"))

    lowered = {k.lower(): v for k, v in agent_headers.items()}
    for name in lowered:
        if name in FORBIDDEN_AGENT_HEADERS:
            return Decision(False, f"agent_supplied_credential_header:{name}",
                            audit=_audit(handle, host, path, False,
                                         "agent_supplied_credential_header"))
    for value in list(lowered.values()) + [body_sample or ""]:
        if value and CREDENTIAL_SHAPE.search(str(value)):
            return Decision(False, "credential_shaped_input",
                            audit=_audit(handle, host, path, False,
                                         "credential_shaped_input"))

    if host not in spec["allowed_hosts"]:
        return Decision(False, "host_not_allowed",
                        audit=_audit(handle, host, path, False, "host_not_allowed"))
    prefixes = spec.get("allowed_path_prefixes") or ["/"]
    if not any(path.startswith(p) for p in prefixes):
        return Decision(False, "path_not_allowed",
                        audit=_audit(handle, host, path, False, "path_not_allowed"))

    value = environ.get(spec["credential_env"])
    if not value:
        # Fail closed, and say which NAME is unprovisioned — provisioning
        # is an owner act (phantom-secrets rule); never invent a value.
        return Decision(False, f"credential_unprovisioned:{spec['credential_env']}",
                        audit=_audit(handle, host, path, False,
                                     "credential_unprovisioned"))

    outbound = {k: v for k, v in agent_headers.items()
                if k.lower() not in FORBIDDEN_AGENT_HEADERS
                and k.lower() != "x-fleet-handle"}
    outbound[spec["credential_header"]] = (
        spec.get("credential_prefix", "") + value)
    return Decision(True, "swapped", outbound_headers=outbound,
                    audit=_audit(handle, host, path, True, "swapped"))


def serve(cfg: dict, port: int) -> None:  # pragma: no cover - eval adapter
    """Minimal local-evaluation HTTP adapter around translate().

    The agent calls this proxy with header X-Fleet-Handle and a
    Host/path of the target; the proxy performs the swap and forwards
    over HTTPS. Deliberately small: no pooling, no streaming.
    """
    import http.client
    import ssl
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class Handler(BaseHTTPRequestHandler):
        def _go(self):
            handle = self.headers.get("X-Fleet-Handle", "")
            host = self.headers.get("X-Fleet-Target-Host", "")
            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length) if length else b""
            headers = {k: v for k, v in self.headers.items()}
            decision = translate(cfg, handle, self.command, host, self.path,
                                 headers, body[:4096].decode(errors="replace"))
            print(json.dumps(decision.audit), file=sys.stderr)
            if not decision.allowed:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(json.dumps(
                    {"error": decision.reason}).encode())
                return
            ctx = ssl.create_default_context()
            conn = http.client.HTTPSConnection(host, 443, context=ctx, timeout=30)
            conn.request(self.command, self.path, body=body,
                         headers=decision.outbound_headers)
            resp = conn.getresponse()
            data = resp.read()
            self.send_response(resp.status)
            for k, v in resp.getheaders():
                if k.lower() not in ("transfer-encoding", "connection"):
                    self.send_header(k, v)
            self.end_headers()
            self.wfile.write(data)

        do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = _go

        def log_message(self, *args):
            pass

    HTTPServer(("127.0.0.1", port), Handler).serve_forever()


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) < 1:
        print(__doc__)
        return 2
    cfg = load_config(argv[0])
    port = int(argv[1]) if len(argv) > 1 else 8765
    print(f"credential-swap proxy (reference) on 127.0.0.1:{port}, "
          f"handles: {', '.join(sorted(cfg['handles']))}", file=sys.stderr)
    serve(cfg, port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
