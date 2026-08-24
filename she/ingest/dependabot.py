"""SHE P0.2 — normalize Dependabot alerts / security-update PRs → Incident.

Observer only. stdlib-only. No network.
"""
from __future__ import annotations

from typing import Any, Mapping

from she.incident import Incident


def _str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def fingerprint_dependabot(
    *,
    package: str,
    severity: str,
    ecosystem: str = "",
    alert_number: str = "",
) -> str:
    parts = [
        "dependabot",
        ecosystem.strip().lower() or "pkg",
        package.strip().lower().replace(" ", "-") or "unknown",
        severity.strip().lower() or "unknown",
    ]
    if alert_number:
        parts.append(str(alert_number))
    return ":".join(parts)


def normalize_dependabot_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Extract Incident fields from Dependabot alert or security PR payload."""
    if not isinstance(payload, Mapping):
        raise TypeError("payload must be a mapping")

    alert = payload.get("alert") if isinstance(payload.get("alert"), Mapping) else payload
    dependency = alert.get("dependency") if isinstance(alert.get("dependency"), Mapping) else {}
    pkg = dependency.get("package") if isinstance(dependency.get("package"), Mapping) else {}
    security = (
        alert.get("security_advisory")
        if isinstance(alert.get("security_advisory"), Mapping)
        else {}
    )

    package_name = _str(pkg.get("name") or alert.get("package") or payload.get("package") or "unknown")
    ecosystem = _str(pkg.get("ecosystem") or alert.get("ecosystem") or "")
    severity = _str(
        security.get("severity")
        or alert.get("severity")
        or payload.get("severity")
        or "medium"
    ).lower()
    alert_number = _str(alert.get("number") or payload.get("number") or "")
    state = _str(alert.get("state") or payload.get("state") or "open")

    repo_obj = payload.get("repository") or {}
    repo_full = ""
    if isinstance(repo_obj, Mapping):
        repo_full = _str(repo_obj.get("full_name"))
    if not repo_full:
        repo_full = _str(payload.get("repository") or "unknown/unknown")

    html_url = _str(alert.get("html_url") or payload.get("html_url") or "")
    ghsa = _str(security.get("ghsa_id") or "")
    cve = _str(
        (security.get("cve_id") if isinstance(security.get("cve_id"), str) else "")
        or ""
    )

    fp = fingerprint_dependabot(
        package=package_name,
        severity=severity,
        ecosystem=ecosystem,
        alert_number=alert_number,
    )

    evidence: list[str] = []
    if html_url:
        evidence.append(html_url)
    if ghsa:
        evidence.append(f"ghsa://{ghsa}")
    if cve:
        evidence.append(f"cve://{cve}")

    she_severity = "medium"
    if severity in {"critical", "high"}:
        she_severity = "high"
    elif severity in {"low", "info"}:
        she_severity = "low"

    return {
        "source": "github.dependabot",
        "event_provenance": f"dependabot:{ecosystem or 'pkg'}:{package_name}:{severity}",
        "repository": repo_full or "unknown/unknown",
        "ref": _str(payload.get("ref") or "refs/heads/master"),
        "sha": _str(payload.get("sha") or payload.get("head_sha") or "0" * 40),
        "severity": she_severity,
        "classification": f"dependabot-{severity}",
        "evidence_refs": evidence,
        "authority_scope": ["L0-observe"],
        "allowed_actions": ["observe", "triage"],
        "fingerprint": fp,
        "metadata": {
            "package": package_name,
            "ecosystem": ecosystem or None,
            "severity": severity,
            "state": state,
            "alert_number": alert_number or None,
            "ghsa_id": ghsa or None,
            "cve_id": cve or None,
            "html_url": html_url or None,
        },
    }


def incident_from_dependabot(
    payload: Mapping[str, Any],
    *,
    incident_id: str | None = None,
) -> Incident:
    fields = normalize_dependabot_payload(payload)
    return Incident.create(incident_id=incident_id, **fields)
