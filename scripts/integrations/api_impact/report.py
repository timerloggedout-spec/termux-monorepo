"""Pure API Impact Mapper report normalization and validation."""
from __future__ import annotations

import fnmatch
import re
from pathlib import PurePosixPath
from typing import Any, Iterable, Optional

DEFAULT_API_PATH_PATTERNS = (
    "llm_api_hub/server/**", "llm_api_hub/clients/**", "llm_api_hub/schemas/**",
    "hub_mcp/**", "commingle-swarm/web/src/api/**",
    "apps/listinglens/src/schemas.mjs", "apps/listinglens/tests/schemas.test.mjs",
    "deepcli/investigator/api_map.py", "deepseek-cli/test/api_probe.test.js",
    "_1-Projects/a/yobitrageswap/api/**",
)
CATEGORIES = {
    "removed_endpoint", "removed_operation", "changed_parameter",
    "changed_parameter_requiredness", "changed_parameter_type",
    "changed_response_field", "changed_response_type", "changed_status_code",
    "changed_authentication", "changed_semantics", "non_breaking_change",
    "cannot_determine",
}
CONFIDENCE = {"confirmed", "partial", "insufficient"}
PRIORITIES = {"high", "medium", "low", "unknown"}
IMPACT_STATUSES = {"confirmed", "partial", "unknown"}
STAGE_STATUSES = {"success", "partial", "error"}
SHA_RE = re.compile(r"^[0-9a-f]{7,64}$")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SECRET_RE = re.compile(
    r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
    r"sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|Bearer\\s+[A-Za-z0-9._~+/-]{20,})"
)
PROHIBITED_KEYS = (
    "prompt", "completion", "cookie", "token", "secret", "authorization",
    "transcript", "raw_diff", "source_text", "api_key", "access_key",
)


def _safe_path(value: Any) -> str:
    if not isinstance(value, str) or not value or "\\\\" in value or "\\x00" in value:
        raise ValueError("unsafe changed path")
    if any(part in {"", ".", ".."} for part in value.split("/")):
        raise ValueError("unsafe changed path")
    path = PurePosixPath(value)
    if path.is_absolute():
        raise ValueError("unsafe changed path")
    return path.as_posix()


def classify_changed_paths(changed_paths: Iterable[str], patterns: Optional[Iterable[str]] = None) -> list[str]:
    """Match changed files against the explicit, reviewed API path policy."""
    selected = tuple(patterns or DEFAULT_API_PATH_PATTERNS)
    normalized = {_safe_path(path) for path in changed_paths}
    return sorted(path for path in normalized if any(fnmatch.fnmatchcase(path, p) for p in selected))


def _mapping(value: Any, label: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _list(value: Any, label: str) -> list:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be an array")
    return value


def _string(value: Any, label: str, limit: int = 2000) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f"{label} must be a non-empty string (max {limit})")
    return value.strip()


def _reject_private_fields(value: Any, path: str = "input") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            name = str(key).lower()
            allowed_attestation = path.endswith(".privacy") and name in {
                "contains_raw_prompt", "contains_secret", "redaction_applied"
            }
            if not allowed_attestation and any(part in name for part in PROHIBITED_KEYS):
                raise ValueError(f"prohibited field: {path}.{key}")
            _reject_private_fields(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _reject_private_fields(nested, f"{path}[{index}]")
    elif isinstance(value, str) and SECRET_RE.search(value):
        raise ValueError(f"credential-shaped value rejected at {path}")


def _evidence(results: dict) -> list[dict[str, str]]:
    found: dict[str, dict[str, str]] = {}
    for stage_name in ("extraction", "classification", "impact_map"):
        stage = _mapping(results.get(stage_name), f"results.{stage_name}")
        for index, item in enumerate(_list(stage.get("evidence", []), f"{stage_name}.evidence")):
            item = _mapping(item, f"{stage_name}.evidence[{index}]")
            evidence_id = _string(item.get("evidence_id"), "evidence_id", 120)
            record = {
                "evidence_id": evidence_id,
                "quote": _string(item.get("quote"), "evidence.quote"),
                "source": _string(item.get("source"), "evidence.source", 500),
            }
            if evidence_id in found and found[evidence_id] != record:
                raise ValueError(f"conflicting evidence_id: {evidence_id}")
            found[evidence_id] = record
    return [found[key] for key in sorted(found)]


def _evidence_refs(item: dict, label: str, evidence_ids: set[str]) -> list[str]:
    refs = _list(item.get("evidence_ids", []), f"{label}.evidence_ids")
    if not refs:
        raise ValueError(f"{label} must cite evidence")
    if any(not isinstance(ref, str) or ref not in evidence_ids for ref in refs):
        raise ValueError(f"unknown evidence_id in {label}")
    return sorted(set(refs))


def normalize_mapper_input(payload: Any, repository: str, base_sha: str, head_sha: str, pull_request: int) -> dict:
    """Validate the explicit identity/privacy envelope and normalize three mapper outputs."""
    payload = _mapping(payload, "mapper input")
    _reject_private_fields(payload)
    required = {"repository", "pull_request", "base_sha", "head_sha", "privacy", "results"}
    if required - payload.keys():
        raise ValueError("mapper input missing required fields")
    for key, expected, label in (
        ("repository", repository, "repository"),
        ("pull_request", pull_request, "pull request"),
        ("base_sha", base_sha, "base SHA"),
        ("head_sha", head_sha, "head SHA"),
    ):
        if payload[key] != expected:
            raise ValueError(f"{label} mismatch")
    privacy = _mapping(payload["privacy"], "privacy")
    if privacy.get("contains_raw_prompt") is not False or privacy.get("contains_secret") is not False:
        raise ValueError("privacy attestation must explicitly exclude raw prompts and secrets")

    results = _mapping(payload["results"], "results")
    for name in ("extraction", "classification", "impact_map"):
        if _mapping(results.get(name), f"results.{name}").get("status") not in STAGE_STATUSES:
            raise ValueError(f"invalid {name} status")
    evidence = _evidence(results)
    evidence_ids = {item["evidence_id"] for item in evidence}

    changes, change_ids = [], set()
    for item in _list(results["extraction"].get("api_changes_items", []), "api_changes_items"):
        item = _mapping(item, "api change")
        change_id = _string(item.get("change_id"), "change_id", 120)
        if change_id in change_ids:
            raise ValueError(f"duplicate change_id: {change_id}")
        change_ids.add(change_id)
        refs = _evidence_refs(item, f"change {change_id}", evidence_ids)
        before, after = item.get("before", ""), item.get("after", "")
        if not isinstance(before, str) or not isinstance(after, str):
            raise ValueError(f"before/after must be strings for {change_id}")
        changes.append({
            "change_id": change_id,
            "change_type": _string(item.get("change_type"), "change_type", 120),
            "location": _string(item.get("location"), "location", 500),
            "before": before[:2000], "after": after[:2000],
            "description": _string(item.get("description"), "description"),
            "evidence_ids": refs,
        })

    classifications, classified_ids, unresolved = [], set(), False
    for item in _list(results["classification"].get("classifications", []), "classifications"):
        item = _mapping(item, "classification")
        change_id = _string(item.get("change_id"), "classification.change_id", 120)
        if change_id not in change_ids:
            raise ValueError(f"classification references unknown change_id: {change_id}")
        if change_id in classified_ids:
            raise ValueError(f"duplicate classification for change_id: {change_id}")
        classified_ids.add(change_id)
        category, confidence = item.get("category"), item.get("confidence")
        if category not in CATEGORIES or confidence not in CONFIDENCE:
            raise ValueError(f"invalid classification for {change_id}")
        unresolved = unresolved or category == "cannot_determine" or confidence != "confirmed"
        classifications.append({
            "change_id": change_id, "category": category, "confidence": confidence,
            "rationale": _string(item.get("rationale"), "classification.rationale"),
            "evidence_ids": _evidence_refs(item, f"classification {change_id}", evidence_ids),
        })

    impacts, impact_ids = [], set()
    deliverable = _mapping(results["impact_map"].get("deliverable"), "impact_map.deliverable")
    for item in _list(deliverable.get("impact_items", []), "impact_items"):
        item = _mapping(item, "impact")
        impact_id = _string(item.get("impact_id"), "impact_id", 120)
        if impact_id in impact_ids:
            raise ValueError(f"duplicate impact_id: {impact_id}")
        impact_ids.add(impact_id)
        change_id = _string(item.get("change_id"), "impact.change_id", 120)
        if change_id not in change_ids:
            raise ValueError(f"impact references unknown change_id: {change_id}")
        priority, status = item.get("priority"), item.get("status")
        if priority not in PRIORITIES or status not in IMPACT_STATUSES:
            raise ValueError(f"invalid impact priority/status: {impact_id}")
        unresolved = unresolved or status != "confirmed" or priority == "unknown"
        impacts.append({
            "impact_id": impact_id, "change_id": change_id,
            "affected_object": _string(item.get("affected_object"), "affected_object", 500),
            "impact_type": _string(item.get("impact_type"), "impact_type", 120),
            "recommended_action": _string(item.get("recommended_action"), "recommended_action"),
            "priority": priority, "status": status,
            "evidence_ids": _evidence_refs(item, f"impact {impact_id}", evidence_ids),
        })

    missing, limitations, errors = set(), set(), []
    for name in ("extraction", "classification", "impact_map"):
        stage = results[name]
        missing.update(str(x) for x in _list(stage.get("missing_fields", []), f"{name}.missing_fields"))
        for error in _list(stage.get("errors", []), f"{name}.errors"):
            error = error if isinstance(error, dict) else {}
            errors.append({"stage": name, "code": str(error.get("code", "unknown")), "field": str(error.get("field", ""))})
        unresolved = unresolved or stage["status"] != "success"
    for value in _list(results["impact_map"].get("limitations", []), "limitations"):
        limitations.add(str(value))
    for item in _list(results["classification"].get("unclassified_items", []), "unclassified_items"):
        unresolved = True
        limitations.add(str(item.get("reason", "unclassified API change")) if isinstance(item, dict) else "unclassified API change")
    if len(classified_ids) != len(change_ids):
        unresolved = True
        limitations.add("one or more extracted API changes lack a classification")
    if not changes:
        unresolved = True
        limitations.add("no API changes were extracted from the changed API surface")
    if missing or errors:
        unresolved = True
    return {
        "changes": sorted(changes, key=lambda x: x["change_id"]),
        "classifications": sorted(classifications, key=lambda x: x["change_id"]),
        "impacts": sorted(impacts, key=lambda x: x["impact_id"]),
        "evidence": evidence, "missing_fields": sorted(missing),
        "limitations": sorted(limitations),
        "errors": sorted(errors, key=lambda x: (x["stage"], x["code"], x["field"])),
        "state": "partial" if unresolved else "validated",
    }


def build_report(repository: str, base_sha: str, head_sha: str, pull_request: int,
                 changed_paths: Iterable[str], mapper_input: Optional[dict] = None,
                 patterns: Optional[Iterable[str]] = None) -> dict:
    if not REPO_RE.fullmatch(repository):
        raise ValueError("repository must be owner/name")
    if not SHA_RE.fullmatch(base_sha) or not SHA_RE.fullmatch(head_sha):
        raise ValueError("base/head SHA must be 7-64 lowercase hexadecimal characters")
    if not isinstance(pull_request, int) or isinstance(pull_request, bool) or pull_request < 1:
        raise ValueError("pull_request must be a positive integer")
    changed = sorted({_safe_path(path) for path in changed_paths})
    api_files = classify_changed_paths(changed, patterns)
    report = {
        "schema_version": "1.0.0", "repository": repository, "pull_request": pull_request,
        "base_sha": base_sha, "head_sha": head_sha, "state": "not_applicable",
        "changed_files": changed, "api_surface_files": api_files,
        "changes": [], "classifications": [], "impacts": [], "evidence": [],
        "missing_fields": [], "limitations": [], "errors": [],
        "provenance": {"provider": "repository-detector", "capture_method": "git_diff_path_policy", "attribution": "direct"},
        "privacy": {"contains_raw_prompt": False, "contains_secret": False},
    }
    if not api_files:
        if mapper_input is not None:
            raise ValueError("mapper results supplied but no configured API surface changed")
        return report
    report["provenance"] = {
        "provider": "API Impact Mapper",
        "capture_method": "assistant_supplied_mcp_result",
        "attribution": "provider_reported",
    }
    if mapper_input is None:
        report["state"] = "analysis_required"
        report["limitations"] = ["API surface changed; mapper results not supplied for this exact PR head."]
        return report
    report.update(normalize_mapper_input(mapper_input, repository, base_sha, head_sha, pull_request))
    return report
