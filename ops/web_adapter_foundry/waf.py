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
import re
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


def load_taxonomy() -> dict:
    """The reconciled umbrella taxonomy: Foundry catalog + browser-lane
    imports folded into one nested placement (taxonomy.json)."""
    return json.loads((HERE / "taxonomy.json").read_text(encoding="utf-8"))


def taxonomy_node(taxonomy: dict, repo: str) -> dict | None:
    for n in taxonomy.get("nodes", []):
        if n["repo"].lower() == repo.lower():
            return n
    return None


# ------------------------------------------------------- streaming (SSE)

def sse_encode(data, event: str | None = None, event_id: int | None = None) -> str:
    """Encode one Server-Sent Events frame. `data` may be a dict (JSON) or
    a string; multi-line strings are split into repeated data: lines, per
    the SSE spec. SSE is the one-way streaming facade for Foundry results
    (poller/queue patterns); bidirectional control belongs to WebSocket /
    CDP-over-WebSocket. See taxonomy.json `transports`."""
    lines = []
    if event_id is not None:
        lines.append(f"id: {event_id}")
    if event:
        lines.append(f"event: {event}")
    payload = data if isinstance(data, str) else json.dumps(data, sort_keys=True)
    for line in payload.splitlines() or [""]:
        lines.append(f"data: {line}")
    return "\n".join(lines) + "\n\n"


class EventBus:
    """Minimal in-process pub/sub for streaming facades: invoke results are
    published once and every SSE/WebSocket subscriber receives the same
    frame — streaming never re-executes the operation."""

    def __init__(self) -> None:
        import queue as _queue
        self._queue = _queue
        self._subs: list = []
        self._seq = 0

    def subscribe(self):
        q = self._queue.Queue()
        self._subs.append(q)
        return q

    def unsubscribe(self, q) -> None:
        if q in self._subs:
            self._subs.remove(q)

    def publish(self, data, event: str | None = None) -> str:
        self._seq += 1
        frame = sse_encode(data, event=event, event_id=self._seq)
        for q in list(self._subs):
            q.put(frame)
        return frame


# ---------------------------------------------------------------- intake
# A Target Brief is how a collaborator aims the stack at one target with one
# purpose. Intake validates authorisation/scope and deterministically maps
# purpose -> taxonomy categories -> a stack plan with execution sites.

PURPOSES = {
    "api-extraction": ["capture-and-recon", "contract-synthesis", "verification"],
    "cli-adapter": ["adapter-systems", "drivers-and-clients", "verification"],
    "data-extraction": ["extraction-and-discovery", "engines", "verification"],
    "session-reuse": ["adapter-systems", "capture-and-recon"],
    "deobfuscation": ["code-recovery", "capture-and-recon"],
    "monitoring": ["extraction-and-discovery", "engines"],
    "full-reverse": ["engines", "drivers-and-clients", "capture-and-recon",
                     "code-recovery", "contract-synthesis", "adapter-systems",
                     "verification", "agent-layers", "extraction-and-discovery",
                     "substrate"],
}
DEVICE_CLASSES = ("b160v-on-device", "remote-service", "ci", "local")


def _brief_domain(brief: dict) -> str | None:
    target = brief.get("target") or ""
    host = urllib.parse.urlparse(target if "://" in target else f"//{target}").hostname
    return host.lower() if host else None


def validate_brief(brief: dict) -> list[str]:
    errs: list[str] = []
    if not isinstance(brief, dict):
        return ["brief must be a JSON object"]
    if not isinstance(brief.get("target_id"), str) or not brief["target_id"]:
        errs.append("target_id: required non-empty string")
    domain = _brief_domain(brief)
    if not domain:
        errs.append("target: required URL or domain")
    if brief.get("purpose") not in PURPOSES:
        errs.append(f"purpose must be one of {sorted(PURPOSES)}")
    auth = brief.get("authorization") or {}
    if not isinstance(auth, dict) or not auth.get("basis"):
        errs.append("authorization.basis: required (why this target may be automated)")
    scope = auth.get("scope_domains") or []
    if domain and scope and domain not in [s.lower() for s in scope]:
        errs.append(f"target domain {domain} is outside authorization.scope_domains {scope}")
    if not scope:
        errs.append("authorization.scope_domains: required non-empty list")
    if brief.get("side_effect", "read") not in SIDE_EFFECTS:
        errs.append("side_effect must be read|write")
    if brief.get("side_effect") == "write" and auth.get("state_changing") is not True:
        errs.append("write briefs require authorization.state_changing: true")
    budget = brief.get("probe_budget", 24)
    if not isinstance(budget, int) or not (1 <= budget <= 200):
        errs.append("probe_budget must be an integer in 1..200")
    if brief.get("device_class", "remote-service") not in DEVICE_CLASSES:
        errs.append(f"device_class must be one of {DEVICE_CLASSES}")
    return errs


def _execution_site(node: dict, device_class: str) -> str:
    tier = node.get("b160v_tier") or ""
    if device_class != "b160v-on-device":
        return device_class
    if tier.startswith(("on-device", "substrate", "thin client")):
        return "b160v-on-device"
    if tier.startswith("handset"):
        return "b160v-gui"
    if tier.startswith("offload"):
        return "remote-service (offload — B160V law)"
    return "remote-service (default for unassessed)"


def plan_from_brief(brief: dict, taxonomy: dict) -> dict:
    errs = validate_brief(brief)
    if errs:
        raise ValueError("invalid brief: " + "; ".join(errs))
    cats = PURPOSES[brief["purpose"]]
    device_class = brief.get("device_class", "remote-service")
    stack = []
    for node in taxonomy.get("nodes", []):
        if node["category_path"][1] in cats:
            stack.append({"repo": node["repo"], "category": "/".join(node["category_path"][1:]),
                          "execution_site": _execution_site(node, device_class),
                          "sources": node["sources"]})
    transports = ["cli", "stdin-jsonl"]
    if any(n["category"].startswith(("engines", "drivers")) for n in stack):
        transports.append("cdp-websocket")
    if brief["purpose"] == "monitoring":
        transports.append("sse")
    slug = brief["target_id"]
    return {
        "target_id": slug, "purpose": brief["purpose"],
        "domain": _brief_domain(brief),
        "side_effect": brief.get("side_effect", "read"),
        "probe_budget": brief.get("probe_budget", 24),
        "device_class": device_class,
        "stages": ["scope-and-capture", "recover-semantics", "bounded-probes",
                   "synthesize-contract", "generate-and-verify", "promote-monitor-repair"],
        "stack": stack,
        "transports": transports,
        "probes": [p["id"] for p in PROBES],
        "registry_skeleton": {
            "provider": slug,
            "operations": [
                {"operation_id": f"{slug}.discover", "status": "discovered",
                 "side_effect": "read", "executor": "browser-context-request",
                 "evidence_label": "unknown", "fallback": {"allowed": []}},
                {"operation_id": f"{slug}.primary", "status": "discovered",
                 "side_effect": brief.get("side_effect", "read"),
                 "executor": "browser-context-request",
                 "evidence_label": "unknown", "fallback": {"allowed": []}},
            ],
        },
        "artifact_placement": {
            "registry": f"ops/web_adapter_foundry/providers/{slug}/registry.json",
            "evidence_sanitized": f"ops/web_adapter_foundry/providers/{slug}/evidence/",
            "notes": "docs/ops/ (campaign doc section or target note)",
            "coordination": "GitHub: PR + [MUSEai]@{role:{moniker}} comments",
        },
    }


# ------------------------------------------------------- issue-form input
# One brief schema, many surfaces (T.A.K. input layer): a GitHub Issue filed
# from .github/ISSUE_TEMPLATE/target-brief.yml renders as markdown sections;
# this parses that body back into the exact brief `validate_brief` expects,
# so an issue, a CLI file, a JSONL call and a chat message all converge on
# the same intake. Nothing surface-specific leaks past this function.

_FORM_FIELDS = {
    "target id": "target_id",
    "target url or domain": "target",
    "purpose": "purpose",
    "authorization basis": "basis",
    "scope domains": "scope_domains",
    "side effect": "side_effect",
    "probe budget": "probe_budget",
    "execution venue": "device_class",
    "state-changing authorization": "state_changing",
}


def parse_issue_form(body: str) -> dict:
    sections: dict[str, str] = {}
    current: str | None = None
    for line in (body or "").splitlines():
        if line.startswith("### "):
            current = line[4:].strip().lower()
            sections[current] = ""
        elif current is not None:
            sections[current] += line + "\n"

    def val(key: str) -> str:
        raw = ""
        for heading, field in _FORM_FIELDS.items():
            if field == key and heading in sections:
                raw = sections[heading].strip()
                break
        return "" if raw in ("_No response_", "None") else raw

    brief: dict = {}
    if val("target_id"):
        brief["target_id"] = val("target_id").split()[0]
    if val("target"):
        brief["target"] = val("target").split()[0]
    if val("purpose"):
        brief["purpose"] = val("purpose").strip()
    if val("side_effect"):
        brief["side_effect"] = val("side_effect").strip().lower()
    if val("device_class"):
        brief["device_class"] = val("device_class").strip()
    budget = val("probe_budget")
    if budget:
        try:
            brief["probe_budget"] = int(budget.split()[0])
        except ValueError:
            brief["probe_budget"] = budget  # validate_brief will flag it
    scope = [s.strip().strip(",") for s in re.split(r"[,\s]+", val("scope_domains")) if s.strip()]
    sc_raw = val("state_changing")
    checked = (bool(re.search(r"-\s*\[x\]", sc_raw, re.IGNORECASE))
               or sc_raw.strip().lower() == "yes")
    brief["authorization"] = {"basis": val("basis"), "scope_domains": scope,
                              "state_changing": checked}
    return brief


def render_plan_markdown(plan: dict) -> str:
    lines = [f"## 🎯 Target plan — `{plan['target_id']}`", "",
             f"- **Purpose:** {plan['purpose']} · **Domain:** {plan['domain']} · "
             f"**Venue:** {plan['device_class']} · **Side effect:** {plan['side_effect']} · "
             f"**Probe budget:** {plan['probe_budget']}",
             f"- **Transports:** {', '.join(plan['transports'])}",
             f"- **Stages:** {' → '.join(plan['stages'])}", "", "**Stack (taxonomy-mapped):**"]
    by_cat: dict[str, list[dict]] = {}
    for node in plan["stack"]:
        by_cat.setdefault(node["category"], []).append(node)
    for cat, nodes in by_cat.items():
        lines.append(f"- `{cat}`")
        for n in nodes:
            lines.append(f"  - `{n['repo']}` → {n['execution_site']}")
    lines += ["", "**Registry skeleton:** " +
              ", ".join(f"`{op['operation_id']}` ({op['status']})"
                        for op in plan["registry_skeleton"]["operations"]),
              "", "**Artifact placement:**"]
    for k, v in plan["artifact_placement"].items():
        lines.append(f"- {k}: `{v}`" if k != "coordination" else f"- {k}: {v}")
    return "\n".join(lines) + "\n"


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
    if op_name == "foundry.intake":
        try:
            tax = load_taxonomy()
        except Exception:
            return _resp(rid, False, error={"code": "no_taxonomy",
                                            "message": "taxonomy.json not available"})
        errs = validate_brief(inp.get("brief") or {})
        if errs:
            return _resp(rid, False, error={"code": "bad_brief", "message": "; ".join(errs)})
        return _resp(rid, True, plan_from_brief(inp["brief"], tax))
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


def _host_is_public(host: str) -> bool:
    """SSRF guard: every address the host resolves to must be public.
    (TOCTOU/DNS-rebinding between this check and connect remains a known
    residual — the allowlist is the primary barrier; this stops the
    allowlisted-name -> internal-address pivot.)"""
    import ipaddress
    import socket
    try:
        infos = socket.getaddrinfo(host, None)
    except Exception:
        return False
    for info in infos:
        try:
            ip = ipaddress.ip_address(info[4][0])
        except ValueError:
            return False
        if (ip.is_private or ip.is_loopback or ip.is_link_local
                or ip.is_reserved or ip.is_multicast or ip.is_unspecified):
            return False
    return True


def _validate_fetch_url(url, allow) -> str | None:
    """None when the fetch may proceed, else the refusal reason. Barrier
    chain: http(s) scheme only -> host present -> host in the operation's
    declared allowlist -> host resolves only to public addresses."""
    if not url or not isinstance(url, str):
        return "url: required string"
    parts = urllib.parse.urlparse(url)
    if parts.scheme not in ("http", "https"):
        return f"scheme {parts.scheme!r} refused (http/https only)"
    host = parts.hostname
    if not host:
        return "url: no host"
    if host not in (allow or []):
        return f"url host {host!r} not in allowlist {allow}"
    if not _host_is_public(host):
        return f"url host {host!r} resolves to a non-public address"
    return None


class _AllowlistRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Re-validate every redirect hop against the same barrier chain —
    an allowlisted URL must not 30x the fetch somewhere internal."""

    def __init__(self, allow):
        super().__init__()
        self._allow = allow
        self._hops = 0

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self._hops += 1
        if self._hops > 3:
            raise urllib.error.URLError("too many redirects")
        problem = _validate_fetch_url(newurl, self._allow)
        if problem:
            raise urllib.error.URLError(f"redirect refused: {problem}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _direct_http(rid, op, inp, req):
    if op["side_effect"] != "read":
        return _resp(rid, False, error={"code": "write_via_core_refused",
                                        "message": "core direct-http executor is read-only"})
    url = inp.get("url")
    allow = op.get("allowlist") or []
    problem = _validate_fetch_url(url, allow)
    if problem:
        return _resp(rid, False, error={"code": "not_allowlisted",
                                        "message": problem})
    # Full-URL barrier, inline at the sink: when the operation declares
    # url_prefixes, the fetch target must begin with one of them — the
    # target is then chosen from an author-declared set, not free-form
    # caller input (the canonical full-SSRF remediation). Without
    # prefixes, the host-allowlist + public-address chain above is the
    # barrier, and the URL is rebuilt from its validated components.
    prefixes = op.get("url_prefixes") or []
    if prefixes and not any(url.startswith(p) for p in prefixes):
        return _resp(rid, False, error={"code": "not_allowlisted",
                                        "message": f"url {url!r} matches no declared url_prefix"})
    parts = urllib.parse.urlparse(url)
    if parts.hostname not in allow:
        return _resp(rid, False, error={"code": "not_allowlisted",
                                        "message": f"url host {parts.hostname!r} not in allowlist {allow}"})
    url = urllib.parse.urlunparse((parts.scheme, parts.netloc, parts.path,
                                   "", parts.query, ""))
    deadline = ((req.get("execution") or {}).get("deadline_ms") or 15000) / 1000
    request = urllib.request.Request(url, headers={"User-Agent": f"waf/{VERSION}"})
    opener = urllib.request.build_opener(_AllowlistRedirectHandler(allow))
    try:
        with opener.open(request, timeout=deadline) as r:
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
    p_tx = sub.add_parser("taxonomy", help="print the reconciled umbrella taxonomy (or one repo's placement)")
    p_tx.add_argument("repo", nargs="?")
    p_val = sub.add_parser("validate", help="validate a registry file")
    p_val.add_argument("registry")
    p_pr = sub.add_parser("plan-probes", help="probe plan for an operation in a registry")
    p_pr.add_argument("registry"); p_pr.add_argument("operation_id")
    p_sv = sub.add_parser("serve", help="JSONL stdin/stdout transport")
    p_sv.add_argument("--registry")
    p_in = sub.add_parser("intake", help="validate a Target Brief and print its stack plan")
    p_in.add_argument("brief")
    p_ii = sub.add_parser("issue-intake", help="parse a GitHub issue-form body into a brief, then plan it")
    p_ii.add_argument("body")
    p_ii.add_argument("--markdown", action="store_true", help="emit the plan (or errors) as markdown")
    a = ap.parse_args(argv)
    if a.cmd == "catalog":
        print(json.dumps(load_catalog(), indent=1)); return 0
    if a.cmd == "taxonomy":
        tax = load_taxonomy()
        if a.repo:
            node = taxonomy_node(tax, a.repo)
            print(json.dumps(node, indent=1) if node else json.dumps({"error": "not in taxonomy"}))
            return 0 if node else 1
        print(json.dumps(tax, indent=1)); return 0
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
    if a.cmd == "intake":
        brief = json.loads(Path(a.brief).read_text())
        errs = validate_brief(brief)
        if errs:
            print(json.dumps({"valid": False, "errors": errs}, indent=1)); return 1
        print(json.dumps(plan_from_brief(brief, load_taxonomy()), indent=1)); return 0
    if a.cmd == "issue-intake":
        brief = parse_issue_form(Path(a.body).read_text())
        errs = validate_brief(brief)
        if errs:
            if a.markdown:
                print("## 🎯 Target brief — needs fixes\n\n" +
                      "\n".join(f"- {e}" for e in errs) +
                      "\n\nEdit the issue to correct the fields above; intake re-runs on edit.")
            else:
                print(json.dumps({"valid": False, "errors": errs, "brief": brief}, indent=1))
            return 1
        plan = plan_from_brief(brief, load_taxonomy())
        print(render_plan_markdown(plan) if a.markdown else json.dumps(plan, indent=1))
        return 0
    if a.cmd == "serve":
        reg = load_registry(a.registry) if a.registry else None
        serve(reg, sys.stdin, sys.stdout); return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
