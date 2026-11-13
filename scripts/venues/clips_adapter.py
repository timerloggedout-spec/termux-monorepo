#!/usr/bin/env python3
"""Clips (agent-native) venue adapter (QUE #5254).

Surfaces, established firsthand 2026-11-12:
- READ (no auth): the public agent HTTP API —
  /api/agent-context.json?id=<clip> (+ transcript/frame siblings).
  This powers the verify/read leg for an existing clip.
- CREATE/UPLOAD: the fleet-account authenticated surface (MCP
  connect, https://clips.agent-native.com/mcp/connect). No
  unauthenticated upload endpoint exists. The upload leg therefore
  requires the fleet credential as a SEALED SECRET, named by the
  binding (`credential_env`, name of record only — the value never
  enters the repo). Absent the credential the adapter returns a
  NAMED refusal (venue_auth_missing) — fail-visible per the filing,
  never a silent seat-browser fallback.
"""
from __future__ import annotations

import json
import os
import urllib.request

BASE = "https://clips.agent-native.com"


def read_context(clip_id: str, opener=None) -> dict:
    """Unauthenticated agent-context read for one clip."""
    req = urllib.request.Request(
        f"{BASE}/api/agent-context.json?id={clip_id}", method="GET")
    open_fn = opener or urllib.request.urlopen
    with open_fn(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))


def public_url_for(clip_id: str) -> str:
    return f"{BASE}/share/{clip_id}"


def execute(binding: dict, artifact: str | None, transport=None) -> dict:
    """Upload leg. With an existing clip id + no new artifact, the
    requirement is the publication/verify of that clip (read leg).
    A fresh upload requires the fleet credential."""
    clip_id = binding.get("clip_id")
    if clip_id and not artifact:
        try:
            ctx = read_context(clip_id, opener=transport)
        except Exception as exc:
            return {"status": "refused", "reason": "venue_read_failed",
                    "detail": f"{type(exc).__name__}: {exc}"[:200]}
        if (ctx.get("clip") or {}).get("publicPageUrl"):
            return {"status": "executed",
                    "public_url": ctx["clip"]["publicPageUrl"],
                    "detail": "existing clip verified via agent-context"}
        return {"status": "refused", "reason": "clip_not_public",
                "detail": "agent-context carries no publicPageUrl"}
    cred_env = binding.get("credential_env", "CLIPS_FLEET_TOKEN")
    if not os.environ.get(cred_env):
        return {"status": "refused", "reason": "venue_auth_missing",
                "detail": f"upload requires the fleet credential "
                          f"(sealed secret {cred_env}, name of record); "
                          f"no unauthenticated upload endpoint exists "
                          f"on this venue and no seat fallback is taken"}
    return {"status": "refused", "reason": "upload_route_unbuilt",
            "detail": "credential present but the authenticated "
                      "upload route (MCP connect) is not yet wired; "
                      "refusing rather than improvising a route"}
