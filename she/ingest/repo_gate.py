"""SHE P0.2 — normalize repo-gate / CI gate failure signals → Incident.

Observer only: pure functions. Accepts either a structured gate-result
dict (from scripts/ci/repo_gate.py or a workflow job summary) or a
minimal check-run-like payload. No network, no persistence.
"""
from __future__ import annotations

from typing import Any, Mapping

from she.incident import Incident


def _str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def fingerprint_repo_gate(
    *,
    check_name: str,
    conclusion: str,
    head_sha: str,
) -> str:
    """Stable fingerprint for gate failures (dedupe / known-fix)."""
    parts = [
        "repo-gate",
        check_name.strip().lower().replace(" ", "-") or "gate",
        conclusion.strip().lower() or "unknown",
        (head_sha or "")[:12],
    ]
    return ":".join(parts)


def normalize_repo_gate_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Extract Incident.create fields from a repo-gate / check result.

    Recognized shapes:
    - ``{"ok": False, "failures": [...], "sha": ..., "repository": ...}``
    - check-run-like: ``name``, ``conclusion``, ``head_sha``, ``html_url``
    - nested under ``check_run`` or ``gate`` keys
    """
    if not isinstance(payload, Mapping):
        raise TypeError("payload must be a mapping")

    src = payload
    for key in ("check_run", "gate", "result"):
        nested = payload.get(key)
        if isinstance(nested, Mapping):
            src = nested
            break

    check_name = _str(
        src.get("name")
        or src.get("check")
        or src.get("gate_name")
        or payload.get("name")
        or "repo-gate"
    )
    conclusion = _str(
        src.get("conclusion")
        or src.get("status")
        or ("failure" if src.get("ok") is False else "")
        or payload.get("conclusion")
        or "unknown"
    )
    head_sha = _str(
        src.get("head_sha")
        or src.get("sha")
        or payload.get("sha")
        or payload.get("head_sha")
        or ""
    )
    repo_full = _str(
        src.get("repository")
        or payload.get("repository")
        or ""
    )
    if isinstance(payload.get("repository"), Mapping):
        repo_full = _str(payload["repository"].get("full_name")) or repo_full

    ref = _str(src.get("ref") or payload.get("ref") or "")
    if ref and not ref.startswith("refs/"):
        ref = f"refs/heads/{ref}"

    html_url = _str(src.get("html_url") or payload.get("html_url") or "")
    failures = src.get("failures") or payload.get("failures") or []
    if not isinstance(failures, list):
        failures = [failures]

    fp = fingerprint_repo_gate(
        check_name=check_name,
        conclusion=conclusion,
        head_sha=head_sha,
    )

    evidence: list[str] = []
    if html_url:
        evidence.append(html_url)
    for f in failures[:8]:
        evidence.append(f"gate://failure/{_str(f)[:120]}")

    cl = conclusion.lower()
    severity = "high" if cl in {"failure", "failed", "error"} else "medium"
    if src.get("ok") is False:
        severity = "high"
        if cl == "unknown":
            conclusion = "failure"
            cl = "failure"

    classification = "gate-failure" if cl in {"failure", "failed"} else f"gate-{cl}"

    return {
        "source": "github.repo-gate",
        "event_provenance": f"repo_gate:{check_name}:{conclusion}",
        "repository": repo_full or "unknown/unknown",
        "ref": ref or "refs/heads/unknown",
        "sha": head_sha or "0" * 40,
        "severity": severity,
        "classification": classification,
        "evidence_refs": evidence,
        "authority_scope": ["L0-observe"],
        "allowed_actions": ["observe", "triage"],
        "fingerprint": fp,
        "metadata": {
            "check_name": check_name,
            "conclusion": conclusion,
            "failure_count": len(failures),
            "failures_sample": [_str(f)[:200] for f in failures[:5]],
            "html_url": html_url or None,
            "ok": src.get("ok"),
        },
    }


def incident_from_repo_gate(
    payload: Mapping[str, Any],
    *,
    incident_id: str | None = None,
) -> Incident:
    """Create a DETECTED Incident from a repo-gate / check payload."""
    fields = normalize_repo_gate_payload(payload)
    return Incident.create(incident_id=incident_id, **fields)
