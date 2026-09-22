"""Project replay evidence into the canonical longitudinal experiment contract.

The projection is pure: it does not execute providers, mutate repositories,
or infer Action→Effect causality. It converts bounded replay observations into
the existing DOE/MVT experiment record shape.
"""

from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any

from scripts.agent_evolution.replay_simulator import ExplorationPolicy, ReplayResult

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def to_experiment_record(*, experiment_id: str, observed_at: str, baseline_sha: str,
                        candidate_sha: str, suite: str, policy: ExplorationPolicy,
                        result: ReplayResult, cohort: str | None = None,
                        provider: str | None = None, model: str | None = None,
                        status: str = "observed", outcome: str | None = None,
                        provenance: str = "github", confidence: str = "medium",
                        evidence_refs: list[str] | None = None) -> dict[str, Any]:
    """Return a schema-shaped experiment record for one replay observation."""
    if not experiment_id or not suite:
        raise ValueError("experiment_id and suite must not be empty")
    for name, value in (("baseline_sha", baseline_sha), ("candidate_sha", candidate_sha)):
        if not _SHA_RE.fullmatch(value):
            raise ValueError(f"{name} must be a 40-character lowercase SHA")
    if status not in {"observed", "running", "passed", "failed", "skipped", "blocked", "superseded"}:
        raise ValueError("unsupported experiment status")
    if provenance not in {"github", "linear", "notion", "hex", "vercel", "forensic", "manual", "other"}:
        raise ValueError("unsupported experiment provenance")
    if confidence not in {"high", "medium", "low"}:
        raise ValueError("unsupported experiment confidence")
    datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
    return {
        "schema_version": "1.0",
        "experiment_id": experiment_id,
        "observed_at": observed_at,
        "baseline_sha": baseline_sha,
        "candidate_sha": candidate_sha,
        "merge_base_sha": None,
        "suite": suite,
        "cohort": cohort,
        "treatment": {"manager_policy_id": policy.policy_id, "provider": provider, "model": model, "arm": "replay"},
        "status": status,
        "outcome": outcome,
        "metrics": {
            "replay_score": result.score,
            "covered_nodes": len(result.covered_nodes),
            "replay_cost": result.replay_cost,
            "terminal_count": result.terminal_count,
            "max_active": policy.max_active,
            "min_score": policy.min_score,
            "stop_after_terminal": policy.stop_after_terminal,
        },
        "provenance": provenance,
        "confidence": confidence,
        "evidence_refs": list(evidence_refs or []),
    }


def utc_observed_at() -> str:
    """Return a canonical UTC timestamp suitable for a new observation."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
