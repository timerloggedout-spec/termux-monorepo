"""SHE P0.2 — normalize termux-smoke gate results → Incident.

Observer only. stdlib-only. No network.
"""
from __future__ import annotations

from typing import Any, Mapping

from she.incident import Incident


def _str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def fingerprint_termux_smoke(
    *,
    check_name: str,
    conclusion: str,
    head_sha: str,
) -> str:
    parts = [
        "termux-smoke",
        check_name.strip().lower().replace(" ", "-") or "smoke",
        conclusion.strip().lower() or "unknown",
        (head_sha or "")[:12],
    ]
    return ":".join(parts)


def normalize_termux_smoke_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Extract Incident fields from termux-smoke result / check payload."""
    if not isinstance(payload, Mapping):
        raise TypeError("payload must be a mapping")

    src = payload
    for key in ("result", "smoke", "check_run"):
        nested = payload.get(key)
        if isinstance(nested, Mapping):
            src = nested
            break

    check_name = _str(
        src.get("name") or src.get("check") or payload.get("name") or "termux-smoke"
    )
    conclusion = _str(
        src.get("conclusion")
        or src.get("status")
        or ("failure" if src.get("ok") is False else "")
        or "unknown"
    )
    head_sha = _str(src.get("head_sha") or src.get("sha") or payload.get("sha") or "")
    repo_full = _str(src.get("repository") or payload.get("repository") or "")
    if isinstance(payload.get("repository"), Mapping):
        repo_full = _str(payload["repository"].get("full_name")) or repo_full

    ref = _str(src.get("ref") or payload.get("ref") or "")
    if ref and not ref.startswith("refs/"):
        ref = f"refs/heads/{ref}"

    failures = src.get("failures") or payload.get("failures") or []
    if not isinstance(failures, list):
        failures = [failures]

    fp = fingerprint_termux_smoke(
        check_name=check_name, conclusion=conclusion, head_sha=head_sha
    )

    evidence: list[str] = []
    html_url = _str(src.get("html_url") or payload.get("html_url") or "")
    if html_url:
        evidence.append(html_url)
    for f in failures[:8]:
        evidence.append(f"smoke://failure/{_str(f)[:120]}")

    cl = conclusion.lower()
    severity = "high" if cl in {"failure", "failed", "error"} or src.get("ok") is False else "medium"
    if src.get("ok") is False and cl == "unknown":
        conclusion = "failure"
        cl = "failure"

    return {
        "source": "github.termux-smoke",
        "event_provenance": f"termux_smoke:{check_name}:{conclusion}",
        "repository": repo_full or "unknown/unknown",
        "ref": ref or "refs/heads/unknown",
        "sha": head_sha or "0" * 40,
        "severity": severity,
        "classification": "smoke-failure" if cl in {"failure", "failed"} else f"smoke-{cl}",
        "evidence_refs": evidence,
        "authority_scope": ["L0-observe"],
        "allowed_actions": ["observe", "triage"],
        "fingerprint": fp,
        "metadata": {
            "check_name": check_name,
            "conclusion": conclusion,
            "failure_count": len(failures),
            "failures_sample": [_str(f)[:200] for f in failures[:5]],
            "ok": src.get("ok"),
        },
    }


def incident_from_termux_smoke(
    payload: Mapping[str, Any],
    *,
    incident_id: str | None = None,
) -> Incident:
    fields = normalize_termux_smoke_payload(payload)
    return Incident.create(incident_id=incident_id, **fields)
