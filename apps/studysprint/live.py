"""Opt-in live mode for the StudySprint surfaces (branch (a)).

The surfaces render from the deterministic core by default. Live
mode is OPT-IN (env STRANDS_LIVE=1 for the TUI; a persisted
toggle for the web bundle -- see web/live.js, the mirror of this
module) and calls the deployed Strands endpoint under the
strands-aws contract (strands-aws/schemas/endpoint.schema.json):

  GET  {endpoint}/health  -> {status, strands_agent_available,
                              deployment, model_id}
  POST {endpoint}/plan    -> ALWAYS a receipt (HTTP 200). On any
      {syllabus_ref}         agent/model error the ENDPOINT runs
                             its deterministic gate loop and the
                             receipt carries execution_class=
                             offline-gate + fail_closed=true --
                             there is no 5xx /plan shape.

Fail-closed floor on THIS side: if the endpoint is UNREACHABLE
(transport error, platform 5xx, malformed body -- e.g. the host
container asleep past the wake envelope), the surface falls back
to its local deterministic core and stamps a local receipt
{execution_class: offline-gate, fail_closed: true,
deployment: false, source: surface-local}. A fallback receipt is
never dressed as a live one: production receipts are
execution_class=live-production with deployment=true and the
Bedrock model block, per receipt.schema.json policy.

Wake-ping (spec addendum A2): enabling live mode fires GET
/health on load. Host B's cold wake measured 34.2s; the health
timeout (70s) covers the ~60s wake envelope.
"""
from __future__ import annotations

import json
import os
import urllib.request

ENDPOINT = os.environ.get(
    "STRANDS_ENDPOINT",
    "https://hostb-fit-test-5b9d7.containers.snapdeploy.app")
HEALTH_TIMEOUT_S = 70    # A2 wake envelope (~60s) + margin
PLAN_TIMEOUT_S = 120     # wake + a live invocation


def enabled() -> bool:
    return os.environ.get("STRANDS_LIVE", "") in ("1", "true", "yes")


def _default_opener(method, url, body, timeout):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()


def fallback_receipt(error: str) -> dict:
    """The surface-local fail-closed receipt: the deterministic
    core produced the visible result; this stamps WHY, honestly."""
    return {
        "execution_class": "offline-gate",
        "fail_closed": True,
        "deployment": False,
        "model": None,
        "source": "surface-local",
        "error": error,
    }


def health(opener=None) -> dict:
    """GET /health. Raises on transport failure (the caller
    decides the fallback stamp); returns the parsed body."""
    opener = opener or _default_opener
    st, raw = opener("GET", ENDPOINT + "/health", None,
                     HEALTH_TIMEOUT_S)
    if st != 200:
        raise RuntimeError(f"health: HTTP {st}")
    return json.loads(raw)


def wake(opener=None) -> dict:
    """A2 wake-ping: health, with failure folded into a stamp
    (waking is best-effort; a failed ping never blocks the core)."""
    try:
        h = health(opener)
        return {"awake": True, "health": h}
    except Exception as exc:
        return {"awake": False,
                "error": f"{type(exc).__name__}: {exc}"}


def plan(syllabus_ref: str = "examples/syllabus.json",
         opener=None) -> dict:
    """POST /plan. Returns the endpoint's receipt verbatim on
    success (deployment=true, Bedrock model block,
    execution_class as the endpoint stamped it). ANY transport-
    class failure returns fallback_receipt() -- the caller renders
    the local core plan, which is already the surface's default."""
    if not enabled():
        return fallback_receipt("live mode off (opt-in not set)")
    opener = opener or _default_opener
    try:
        st, raw = opener("POST", ENDPOINT + "/plan",
                         {"syllabus_ref": syllabus_ref},
                         PLAN_TIMEOUT_S)
        if st != 200:
            raise RuntimeError(f"plan: HTTP {st}")
        receipt = json.loads(raw)
        if not isinstance(receipt, dict) or "execution_class" not in receipt:
            raise RuntimeError("plan: malformed receipt body")
        return receipt
    except Exception as exc:
        return fallback_receipt(f"{type(exc).__name__}: {exc}")
