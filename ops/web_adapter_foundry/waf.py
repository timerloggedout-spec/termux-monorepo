#!/usr/bin/env python3
"""Web Adapter Foundry — runtime core.

Evidence-backed web operation discovery and adapter synthesis, upgraded
from the curated research doc (docs/ops/WEB-ADAPTER-FOUNDRY.md).

One operation is defined once in a versioned registry and exposed through
multiple transports. This module is the transport-independent core:

  * JSONL over stdin/stdout  (`waf.py serve`) — the `stdin` endpoint mapping
  * CLI arguments            (`waf.py <command>`)
  * importable Python API    (validate_registry / plan_probes / promote)

Design rules (from the iDEAL document, enforced here, not just documented):
  * stdout carries protocol output only; logs go to stderr.
  * Credentials never travel in request bodies — callers pass an
    `account_ref` and the executor resolves the session out of band.
  * Every modelled claim carries an evidence label:
    observed | inferred | reproduced | contradicted | unknown.
  * Promotion is a state machine: discovered -> captured -> modeled ->
    reproduced -> verified -> canary -> stable. No skipping.
  * Fallback is operation-aware: a write operation with an unknown outcome
    is NEVER auto-retried through another executor.
  * Browser dependence is a valid, honestly recorded result:
    direct-http | browser-context-request | browser-ui-workflow.

Stdlib only — runs on Termux, CI, and any Python 3.10+.
"""
from __future__ import annotations

import json
import sys
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
VERSION = "0.1.0"

EVIDENCE_LABELS = ("observed", "inferred", "reproduced", "contradicted", "unknown")
EXECUTORS = ("direct-http", "browser-context-request", "browser-ui-workflow", "echo")
PROMOTION = ("discovered", "captured", "modeled", "reproduced",
             "verified", "canary", "stable")
DEGRADED = "degraded"
SIDE_EFFECTS = ("read", "write")

# Bounded differential probes (iDEAL doc stage 3), in safe order.
PROBES = (
    {"id": "exact-replay", "question": "Does the captured operation still work?"},
    {"id": "single-field-change", "question": "Which input controls the behaviour?"},
    {"id": "header-removal", "question": "Which headers are actually required?"},
    {"id": "fresh-session", "question": "Is the behaviour tied to one session?"},
    {"id": "expiry", "question": "What must be refreshed, and when?"},
    {"id": "pagination-boundary", "question": "How does traversal terminate?"},
    {"id": "browser-vs-direct", "question": "Can this operation leave the browser?"},
    {"id": "controlled-error", "question": "What failure contract should the adapter expose?"},
)
WRITE_UNSAFE_PROBES = ()  # all probes above are read-safe progressions; state-
# changing fuzzing is never auto-enabled (iDEAL doc stage 3, last paragraph).


# ---------------------------------------------------------------- registry

def validate_registry(reg: dict) -> list[str]:
    """Return a list of validation errors (empty = valid)."""
    errs: list[str] = []
    if not isinstance(reg, dict):
        return ["registry must be a JSON object"]
    ops = reg.get("operations")
    if not isinstance(ops, list) or not ops:
        return ["registry.operations must be a non-empty list"]
    seen = set()
    for i, op in enumerate(ops):
        where = f"operations[{i}]"
        if not isinstance(op, dict):
            errs.append(f"{where}: must be an object")
            continue
        oid = op.get("operation_id")
        if not isinstance(oid, str) or "." not in oid:
            errs.append(f"{where}: operation_id must be a dotted string, got {oid!r}")
        elif oid in seen:
            errs.append(f"{where}: duplicate operation_id {oid!r}")
        else:
            seen.add(oid)
        if op.get("status") not in PROMOTION + (DEGRADED,):
            errs.append(f"{where} ({oid}): status must be one of {PROMOTION + (DEGRADED,)}")
        if op.get("side_effect") not in SIDE_EFFECTS:
            errs.append(f"{where} ({oid}): side_effect must be read|write")
        if op.get("executor") not in EXECUTORS:
            errs.append(f"{where} ({oid}): executor must be one of {EXECUTORS}")
        ev = op.get("evidence_label", "unknown")
        if ev not in EVIDENCE_LABELS:
            errs.append(f"{where} ({oid}): evidence_label must be one of {EVIDENCE_LABELS}")
        fb = (op.get("fallback") or {}).get("allowed", [])
        if op.get("side_effect") == "write" and fb:
            errs.append(
                f"{where} ({oid}): write operations must not declare automatic "
                "fallback executors (unknown-outcome retry is unsafe)")
        for ex in fb:
            if ex not in EXECUTORS:
                errs.append(f"{where} ({oid}): fallback executor {ex!r} not in {EXECUTORS}")
        if op.get("executor") == "direct-http" and not op.get("allowlist"):
            errs.append(f"{where} ({oid}): direct-http operations need an allowlist")
    return errs


def load_registry(path: str | Path) -> dict:
    reg = json.loads(Path(path).read_text(encoding="utf-8"))
    errs = validate_registry(reg)
    if errs:
        raise ValueError("invalid registry: " + "; ".join(errs))
    return reg


def load_catalog() -> dict:
    return json.loads((HERE / "catalog.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------- probes

def plan_probes(op: dict) -> list[dict]:
    """Ordered bounded probe plan for one operation."""
    plan = [dict(p) for p in PROBES]
    if op.get("executor") == "direct-http":
        plan = [p for p in plan if p["id"] != "browser-vs-direct"]
    if op.get("side_effect") == "write":
        for p in plan:
            p["note"] = ("authorized workflow only; no state-changing fuzzing "
                          "without explicit authorization")
    return plan


# ---------------------------------------------------------------- promotion

def can_promote(current: str, target: str) -> tuple[bool, str]:
    """Promotion only moves one step forward; stable may degrade; a degraded
    operation re-enters at investigation (= modeled) and must re-verify."""
    if current == DEGRADED:
        return (target == "modeled"), "degraded -> modeled (investigate) is the only re-entry"
    if current == "stable" and target == DEGRADED:
        return True, "stable may degrade on failure"
    if current in PROMOTION and target in PROMOTION:
        ok = PROMOTION.index(target) == PROMOTION.index(current) + 1
        return ok, "promotion moves exactly one step forward" if ok else \
            f"cannot skip: {current} -> {target}"
    return False, f"unknown state(s): {current!r} -> {target!r}"


# ---------------------------------------------------------------- envelope

def validate_envelope(req: dict) -> list[str]:
    errs = []
    if not isinstance(req, dict):
        return ["request must be a JSON object"]
    if not isinstance(req.get("id"), str) or not req["id"]:
        errs.append("id: required non-empty string")
    if not isinstance(req.get("operation"), str) or not req["operation"]:
        errs.append("operation: required non-empty string")
    if "input" in req and not isinstance(req["input"], dict):
        errs.append("input: must be an object when present")
    ex = req.get("execution") or {}
    if ex.get("mode", "auto") not in ("auto", "direct", "browser", "ui"):
        errs.append("execution.mode must be auto|direct|browser|ui")
    if "deadline_ms" in ex and not (isinstance(ex["deadline_ms"], int) and ex["deadline_ms"] > 0):
        errs.append("execution.deadline_ms must be a positive integer")
    # Credentials in request bodies are refused by construction.
    body = json.dumps(req.get("input") or {}).lower()
    for bad in ("password", "api_key", "apikey", "secret", "bearer ", "cookie:"):
        if bad in body:
            errs.append(f"input must not carry credentials ({bad!r} found); use account_ref")
            break
    return errs


def _resp(req_id, ok, data=None, error=None, meta=None):
    out = {"id": req_id, "ok": ok}
    if ok:
        out["data"] = data if data is not None else {}
    else:
        out["error"] = error or {"code": "error", "message": "unknown"}
    out["meta"] = {"adapter_version": VERSION, **(meta or {})}
    return out


def handle_request(req: dict, registry: dict | None = None) -> dict:
    """Dispatch one envelope. Built-ins are namespaced `foundry.*`;
    registry operations dispatch to their declared executor."""
    errs = validate_envelope(req)
    rid = req.get("id") if isinstance(req, dict) else None
    if errs:
        return _resp(rid, False, error={"code": "bad_envelope", "message": "; ".join(errs)})
    op_name = req["operation"]
    inp = req.get("input") or {}
    ops = {o["operation_id"]: o for o in (registry or {}).get("operations", [])}

    if op_name == "foundry.ping":
        return _resp(rid, True, {"pong": True, "version": VERSION})
    if op_name == "foundry.list_operations":
        return _resp(rid, True, {"operations": sorted(ops)})
    if op_name == "foundry.describe":
        target = inp.get("operation_id")
        if target not in ops:
            return _resp(rid, False, error={"code": "unknown_operation",
                                            "message": f"no such operation: {target!r}"})
        return _resp(rid, True, ops[target])
    if op_name == "foundry.plan_probes":
        target = inp.get("operation_id")
        if target not in ops:
            return _resp(rid, False, error={"code": "unknown_operation",
                                            "message": f"no such operation: {target!r}"})
        return _resp(rid, True, {"operation_id": target, "probes": plan_probes(ops[target])})
    if op_name == "foundry.promote":
        ok, why = can_promote(inp.get("from", ""), inp.get("to", ""))
        return _resp(rid, ok, {"from": inp.get("from"), "to": inp.get("to"), "rule": why}
                     if ok else None,
                     error=None if ok else {"code": "bad_transition", "message": why})

    if op_name not in ops:
        return _resp(rid, False, error={"code": "unknown_operation",
                                        "message": f"no such operation: {op_name!r}"})
    op = ops[op_name]
    if op["status"] not in ("verified", "canary", "stable"):
        return _resp(rid, False, error={"code": "not_promoted",
                                        "message": f"{op_name} is {op['status']}; only "
                                                   "verified/canary/stable execute"})
    executor = op["executor"]
    if executor == "echo":  # canary/testing executor: reflects validated input
        return _resp(rid, True, {"echo": inp},
                     meta={"executor": "echo", "evidence_ref": inp.get("evidence_ref")})
    if executor == "direct-http":
        return _direct_http(rid, op, inp, req)
    # Browser executors are executed by OpenCLI / rever-browser adapters in
    # the fleet; the core honestly reports the dependency instead of faking it.
    return _resp(rid, False, error={"code": "browser_executor_external",
                                    "message": f"{op_name} requires executor "
                                               f"{executor} (OpenCLI/rever-browser adapter)"},
                 meta={"executor": executor})


def _direct_http(rid, op, inp, req):
    if op["side_effect"] != "read":
        return _resp(rid, False, error={"code": "write_via_core_refused",
                                        "message": "core direct-http executor is read-only"})
    url = inp.get("url")
    allow = op.get("allowlist") or []
    host = urllib.parse.urlparse(url).hostname if url else None
    if not url or host not in allow:
        return _resp(rid, False, error={"code": "not_allowlisted",
                                        "message": f"url host {host!r} not in allowlist {allow}"})
    deadline = ((req.get("execution") or {}).get("deadline_ms") or 15000) / 1000
    request = urllib.request.Request(url, headers={"User-Agent": f"waf/{VERSION}"})
    try:
        with urllib.request.urlopen(request, timeout=deadline) as r:
            body = r.read(1_000_000).decode(errors="replace")
            try:
                data = json.loads(body)
            except Exception:
                data = {"text": body}
            return _resp(rid, True, data, meta={"executor": "direct-http", "status": r.status})
    except (urllib.error.URLError, TimeoutError) as e:
        return _resp(rid, False, error={"code": "upstream", "message": str(e)[:300]})


# ---------------------------------------------------------------- transports

def serve(registry: dict | None, instream, outstream) -> None:
    """JSONL transport: one request line in, one terminal response line out.
    Protocol output only on stdout; diagnostics on stderr."""
    for line in instream:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception as e:
            outstream.write(json.dumps(_resp(None, False, error={
                "code": "bad_json", "message": str(e)[:200]})) + "\n")
            outstream.flush()
            continue
        print(f"waf: {req.get('operation')}", file=sys.stderr)
        outstream.write(json.dumps(handle_request(req, registry)) + "\n")
        outstream.flush()


def main(argv: list[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="waf", description="Web Adapter Foundry core")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("catalog", help="print the verified upstream catalog")
    p_val = sub.add_parser("validate", help="validate a registry file")
    p_val.add_argument("registry")
    p_pr = sub.add_parser("plan-probes", help="probe plan for an operation in a registry")
    p_pr.add_argument("registry"); p_pr.add_argument("operation_id")
    p_sv = sub.add_parser("serve", help="JSONL stdin/stdout transport")
    p_sv.add_argument("--registry")
    a = ap.parse_args(argv)
    if a.cmd == "catalog":
        print(json.dumps(load_catalog(), indent=1)); return 0
    if a.cmd == "validate":
        errs = validate_registry(json.loads(Path(a.registry).read_text()))
        print(json.dumps({"valid": not errs, "errors": errs}, indent=1))
        return 0 if not errs else 1
    if a.cmd == "plan-probes":
        reg = load_registry(a.registry)
        op = next((o for o in reg["operations"] if o["operation_id"] == a.operation_id), None)
        if op is None:
            print(json.dumps({"error": "unknown operation"})); return 1
        print(json.dumps(plan_probes(op), indent=1)); return 0
    if a.cmd == "serve":
        reg = load_registry(a.registry) if a.registry else None
        serve(reg, sys.stdin, sys.stdout); return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
