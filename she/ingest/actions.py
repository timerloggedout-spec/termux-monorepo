"""SHE P0.2 — normalize GitHub Actions workflow_run / job events → Incident.

Observer only: pure functions that construct Incident records from the
JSON-ish payloads GitHub Actions (or a future webhook receiver) supplies.
No network, no mutation of external state, no persistence.

Fingerprint is deterministic so a later store can dedupe identical
failure signatures (workflow + conclusion + head_sha + failing job name).
"""
from __future__ import annotations

from typing import Any, Mapping

from she.incident import Incident


def _str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def fingerprint_workflow_run(
    *,
    workflow_name: str,
    conclusion: str,
    head_sha: str,
    job_name: str = "",
) -> str:
    """Stable, human-readable fingerprint for dedupe / known-fix lookup."""
    parts = [
        "gha",
        workflow_name.strip().lower().replace(" ", "-"),
        conclusion.strip().lower() or "unknown",
        (head_sha or "")[:12],
    ]
    if job_name:
        parts.append(job_name.strip().lower().replace(" ", "-"))
    return ":".join(parts)


def normalize_workflow_run_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Extract the fields Incident.create needs from a workflow_run-like dict.

    Accepts either a raw GitHub webhook body (with top-level ``workflow_run``)
    or a flattened dict that already looks like a workflow_run object.
    Optional ``job`` / ``jobs`` keys supply the failing job name for fingerprint.
    """
    if not isinstance(payload, Mapping):
        raise TypeError("payload must be a mapping")

    wr = payload.get("workflow_run")
    if isinstance(wr, Mapping):
        run = wr
        repo_obj = payload.get("repository") or {}
    else:
        run = payload
        repo_obj = payload.get("repository") or {}

    if not isinstance(run, Mapping):
        raise ValueError("no workflow_run object found in payload")

    repo_full = ""
    if isinstance(repo_obj, Mapping):
        repo_full = _str(repo_obj.get("full_name"))
    if not repo_full:
        repo_full = _str(run.get("repository") or run.get("repo") or "")

    head_sha = _str(run.get("head_sha") or run.get("sha") or "")
    head_branch = _str(run.get("head_branch") or run.get("ref") or "")
    ref = head_branch if head_branch.startswith("refs/") else (
        f"refs/heads/{head_branch}" if head_branch else ""
    )

    workflow_name = _str(
        run.get("name")
        or (run.get("path") or "").rsplit("/", 1)[-1]
        or "unknown-workflow"
    )
    conclusion = _str(run.get("conclusion") or run.get("status") or "unknown")
    run_id = run.get("id") or run.get("run_id")
    html_url = _str(run.get("html_url") or "")

    job_name = ""
    job = payload.get("job") or run.get("job")
    if isinstance(job, Mapping):
        job_name = _str(job.get("name"))
    elif isinstance(payload.get("jobs"), list):
        for j in payload["jobs"]:
            if isinstance(j, Mapping) and _str(j.get("conclusion")).lower() in {
                "failure",
                "cancelled",
                "timed_out",
            }:
                job_name = _str(j.get("name"))
                break

    fp = fingerprint_workflow_run(
        workflow_name=workflow_name,
        conclusion=conclusion,
        head_sha=head_sha,
        job_name=job_name,
    )

    evidence: list[str] = []
    if run_id is not None:
        evidence.append(f"actions://run/{run_id}")
    if html_url:
        evidence.append(html_url)

    severity = "medium"
    cl = conclusion.lower()
    if cl in {"failure", "timed_out"}:
        severity = "high"
    elif cl in {"cancelled", "action_required"}:
        severity = "low"

    classification = "workflow-failure" if cl == "failure" else f"workflow-{cl}"

    return {
        "source": "github.actions",
        "event_provenance": f"workflow_run:{workflow_name}:{conclusion}",
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
            "workflow_name": workflow_name,
            "conclusion": conclusion,
            "run_id": run_id,
            "job_name": job_name or None,
            "html_url": html_url or None,
            "event": _str(payload.get("action") or run.get("event") or ""),
        },
    }


def incident_from_workflow_run(
    payload: Mapping[str, Any],
    *,
    incident_id: str | None = None,
) -> Incident:
    """Create a DETECTED Incident from a workflow_run-like payload."""
    fields = normalize_workflow_run_payload(payload)
    return Incident.create(incident_id=incident_id, **fields)
