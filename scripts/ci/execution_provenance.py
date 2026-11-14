"""Privacy-safe execution-controller provenance shared by task-boundary and ATES emitters.

Artifact authorship and the process that controlled execution are separate
facts. Missing controller evidence remains explicitly unknown.
"""
from __future__ import annotations

import math
import re
from typing import Any, Mapping

ATTRIBUTION_METHODS = {
    "workflow_name_mapping", "invocation_telemetry", "task_boundary_declared",
    "session_export", "human_attested", "inferred", "unresolved",
}
EXECUTION_SURFACES = {
    "repo_owned_adapter", "external_computer", "seat_browser", "manual", "unknown",
}
EXECUTION_ROUTES = {
    "api", "mcp", "web2api", "cli", "stdin", "dom_browser",
    "seat_browser", "manual", "unknown",
}
QUE_EXECUTION_ROUTES = {"api", "mcp", "web2api", "cli", "stdin", "dom_browser"}
CONTROLLER_RE = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")
SESSION_REF_RE = re.compile(r"^session:[a-z0-9_-]+:[A-Za-z0-9._-]{1,180}$")
SAFE_REF_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/#_-]{0,255}$")
ADAPTER_VERSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,127}$")


def normalize_execution(raw: Any = None) -> dict[str, Any]:
    """Return a closed execution record; never infer QUE from author or actor metadata."""
    if raw is None:
        raw = {}
    if not isinstance(raw, Mapping):
        raise ValueError("execution must be an object")
    allowed = {
        "controller", "surface", "route", "session_ref", "adapter_version",
        "attribution_method", "confidence", "evidence_refs",
    }
    unknown = set(raw) - allowed
    if unknown:
        raise ValueError(f"unsupported execution fields: {sorted(unknown)}")

    result: dict[str, Any] = {
        "controller": "unknown",
        "surface": "unknown",
        "route": "unknown",
        "session_ref": None,
        "adapter_version": None,
        "attribution_method": "unresolved",
        "confidence": 0.0,
        "evidence_refs": [],
    }

    controller = raw.get("controller", "unknown")
    if not isinstance(controller, str) or not controller.strip() or len(controller) > 128:
        raise ValueError("execution.controller must be a non-empty identity up to 128 characters")
    result["controller"] = controller.strip().lower()
    if not CONTROLLER_RE.fullmatch(result["controller"]):
        raise ValueError("execution.controller must be a safe lowercase identity")

    for field, choices in (
        ("surface", EXECUTION_SURFACES),
        ("route", EXECUTION_ROUTES),
        ("attribution_method", ATTRIBUTION_METHODS),
    ):
        value = raw.get(field, result[field])
        if not isinstance(value, str) or value not in choices:
            raise ValueError(f"invalid execution.{field}")
        result[field] = value

    for field, limit in (("session_ref", 256), ("adapter_version", 128)):
        value = raw.get(field)
        if value is not None:
            if not isinstance(value, str) or not value.strip() or len(value) > limit:
                raise ValueError(f"execution.{field} must be a non-empty opaque reference up to {limit} characters")
            result[field] = value.strip()

    if result["session_ref"] is not None and not SESSION_REF_RE.fullmatch(result["session_ref"]):
        raise ValueError("execution.session_ref must be an opaque session:<controller>:<id> reference")
    if result["adapter_version"] is not None and not ADAPTER_VERSION_RE.fullmatch(result["adapter_version"]):
        raise ValueError("execution.adapter_version must be a safe version identifier")

    if isinstance(raw.get("confidence", 0.0), bool):
        raise ValueError("execution.confidence must be a number, not a boolean")
    try:
        confidence = float(raw.get("confidence", 0.0))
    except (TypeError, ValueError) as exc:
        raise ValueError("execution.confidence must be between 0 and 1") from exc
    if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
        raise ValueError("execution.confidence must be between 0 and 1")
    result["confidence"] = confidence

    refs = raw.get("evidence_refs", [])
    if not isinstance(refs, list) or len(refs) > 20:
        raise ValueError("execution.evidence_refs must be a list of at most 20 references")
    if any(not isinstance(ref, str) or not SAFE_REF_RE.fullmatch(ref.strip()) for ref in refs):
        raise ValueError("execution evidence references must be safe opaque references up to 256 characters")
    result["evidence_refs"] = sorted(set(ref.strip() for ref in refs))

    if result["controller"].lower() == "que":
        if result["surface"] != "repo_owned_adapter":
            raise ValueError("QUE execution requires repo_owned_adapter; external computer and seat-browser work are not QUE execution")
        if result["route"] not in QUE_EXECUTION_ROUTES:
            raise ValueError("QUE execution requires an authorized API, MCP, Web2API, CLI, stdin, or DOM adapter route")
        if not result["session_ref"] or not result["adapter_version"]:
            raise ValueError("QUE execution requires an opaque session reference and adapter version")
        if result["attribution_method"] != "invocation_telemetry":
            raise ValueError("QUE execution requires trusted invocation_telemetry attribution")
        if result["confidence"] <= 0 or not result["evidence_refs"]:
            raise ValueError("QUE execution requires positive confidence and evidence references")

    return result
