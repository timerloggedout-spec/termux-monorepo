#!/usr/bin/env python3
"""Generate a source-derived GitHub Actions event and selector index."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise RuntimeError("Install PyYAML with: python -m pip install PyYAML") from exc

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_DIR = Path(".github/workflows")
CATALOG_PATH = Path("docs/ops/generated/automation-workflow-catalog.json")
OUTPUT_JSON = Path("docs/ops/generated/workflow-event-index.json")
OUTPUT_MD = Path("docs/ops/WORKFLOW-EVENT-INDEX.md")
REGISTRY_PATH = Path("docs/ops/TRIGGER-WORKFLOW-REGISTRY.json")
SCHEMA_VERSION = "workflow-event-index/v2"


class WorkflowLoader(yaml.BaseLoader):
    """Preserve GitHub's literal 'on' key and scalar values."""


def mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def event_config(value: Any) -> dict[str, dict[str, Any]]:
    if isinstance(value, dict):
        return {str(key): mapping(config) for key, config in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, list):
        return {str(key): {} for key in sorted(set(value))}
    if isinstance(value, str):
        return {value: {}}
    return {}


def permissions(document: dict[str, Any]) -> dict[str, Any]:
    raw = document.get("permissions")
    workflow = dict(mapping(raw))
    if isinstance(raw, str):
        workflow = {"_all": raw}
    jobs: dict[str, Any] = {}
    for name, raw_job in sorted(mapping(document.get("jobs")).items()):
        raw_permissions = mapping(raw_job).get("permissions")
        if isinstance(raw_permissions, dict):
            jobs[str(name)] = dict(raw_permissions)
        elif isinstance(raw_permissions, str):
            jobs[str(name)] = {"_all": raw_permissions}
    return {"workflow": workflow, "jobs": jobs}


def source_authority(permission_data: dict[str, Any], job_names: list[str]) -> str:
    workflow = mapping(permission_data.get("workflow"))
    job_permissions = mapping(permission_data.get("jobs"))
    groups = [
        mapping(job_permissions.get(name, workflow))
        for name in job_names
    ] if job_names else [workflow, *[mapping(value) for value in job_permissions.values()]]
    if any(value == "write-all" for group in groups for value in group.values()):
        return "writer"
    if any(value == "write" and scope not in {"issues", "checks", "security-events", "id-token"}
           for group in groups for scope, value in group.items()):
        return "writer"
    if any(scope in {"issues", "checks"} and value == "write"
           for group in groups for scope, value in group.items()):
        return "bounded-state-write"
    if any(scope in {"security-events", "id-token"} and value == "write"
           for group in groups for scope, value in group.items()):
        return "advisory-publisher"
    return "read-only-or-advisory"


def dispatch_inputs(events: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    raw_inputs = mapping(mapping(events.get("workflow_dispatch")).get("inputs"))
    result: dict[str, dict[str, Any]] = {}
    for name, raw in sorted(raw_inputs.items()):
        item = dict(mapping(raw))
        required = item.get("required")
        if isinstance(required, str):
            item["required"] = required.lower() == "true"
        result[str(name)] = item
    return result


def job_selectors(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for name, raw in sorted(mapping(document.get("jobs")).items()):
        job = mapping(raw)
        selected = {key: job[key] for key in ("if", "needs", "runs-on", "environment") if key in job}
        strategy = mapping(job.get("strategy"))
        if "matrix" in strategy:
            selected["matrix"] = strategy["matrix"]
        result[str(name)] = selected
    return result


def parse_workflow_text(source: str, path: str) -> dict[str, Any]:
    try:
        document = yaml.load(source, Loader=WorkflowLoader) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"{path}: YAML parse failure: {exc}") from exc
    if not isinstance(document, dict):
        raise ValueError(f"{path}: YAML root must be a mapping")
    if "on" not in document or not event_config(document.get("on")):
        raise ValueError(f"{path}: missing top-level on event declaration")
    events = event_config(document.get("on"))
    permission_data = permissions(document)
    jobs = mapping(document.get("jobs"))
    if not jobs:
        raise ValueError(f"{path}: workflow must define at least one job")
    action_refs = {
        str(step["uses"])
        for job in jobs.values()
        for step in mapping(job).get("steps", []) or []
        if isinstance(step, dict) and "uses" in step and "@" in str(step["uses"])
    }
    action_refs.update(
        str(job["uses"])
        for job in jobs.values()
        if isinstance(job, dict) and "uses" in job and "@" in str(job["uses"])
    )
    action_pins = sorted(
        reference for reference in action_refs
        if re.fullmatch(r"[0-9a-fA-F]{40}", reference.rsplit("@", 1)[1])
    )
    declared_permission_authority = source_authority(permission_data, [str(name) for name in jobs])
    api_write_methods = sorted({
        method.upper()
        for method in re.findall(
            r"\bgh\s+api\s+(?:--method(?:=|\s+)|-X\s+)(POST|PATCH|PUT|DELETE)\b",
            source,
            flags=re.IGNORECASE,
        )
    })
    source_level_authority = "writer" if api_write_methods else declared_permission_authority
    authority_basis = "declared GitHub workflow/job permissions"
    if api_write_methods:
        authority_basis += " + explicit gh api write methods"
    return {
        "path": path,
        "name": str(document.get("name") or Path(path).stem),
        "events": sorted(events),
        "event_config": events,
        "workflow_dispatch_inputs": dispatch_inputs(events),
        "permissions": permission_data,
        "job_selectors": job_selectors(document),
        "jobs": sorted(str(name) for name in jobs),
        "concurrency": document.get("concurrency") or {},
        "action_refs": sorted(action_refs),
        "action_pins": action_pins,
        "source_authority": source_level_authority,
        "declared_permission_authority": declared_permission_authority,
        "api_write_methods": api_write_methods,
        "authority_basis": authority_basis,
    }


def git_blob_sha(content: bytes) -> str:
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def workflow_paths(root: Path) -> list[Path]:
    base = root / WORKFLOW_DIR
    return sorted([*base.glob("*.yml"), *base.glob("*.yaml")])


def build_index(root: Path = ROOT, catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    catalog_data = catalog if catalog is not None else json.loads((root / CATALOG_PATH).read_text(encoding="utf-8"))
    catalog_records = {
        str(item["path"]): item
        for item in catalog_data.get("workflows", [])
        if isinstance(item, dict) and item.get("path")
    }
    paths = workflow_paths(root)
    directory_paths = {path.relative_to(root).as_posix() for path in paths}
    catalog_paths = set(catalog_records)
    records: list[dict[str, Any]] = []
    for path in paths:
        relative = path.relative_to(root).as_posix()
        content = path.read_bytes()
        source = parse_workflow_text(content.decode("utf-8"), relative)
        catalog_record = catalog_records.get(relative, {})
        catalog_authority = catalog_record.get("authority")
        source_level = source["source_authority"]
        records.append({
            **source,
            "source_blob_sha": git_blob_sha(content),
            "catalog_present": relative in catalog_records,
            "catalog_authority": catalog_authority,
            "catalog_domain": catalog_record.get("domain"),
            "authority_conflict": bool(catalog_authority and catalog_authority != source_level),
            "catalog_source": CATALOG_PATH.as_posix(),
        })
    missing_from_catalog = sorted(directory_paths - catalog_paths)
    missing_from_directory = sorted(catalog_paths - directory_paths)
    status = "IN_SYNC" if not missing_from_catalog and not missing_from_directory and len(records) == len(catalog_records) else "DRIFT"
    return {
        "schema_version": SCHEMA_VERSION,
        "source_fingerprint": catalog_data.get("source_fingerprint"),
        "catalog_source": CATALOG_PATH.as_posix(),
        "reconciliation": {
            "directory_count": len(paths),
            "catalog_count": len(catalog_records),
            "indexed_count": len(records),
            "status": status,
            "missing_from_catalog": missing_from_catalog,
            "missing_from_directory": missing_from_directory,
        },
        "authority_conflicts": [item["path"] for item in records if item["authority_conflict"]],
        "uncatalogued_source_writers": sorted(
            item["path"] for item in records
            if not item["catalog_present"] and item["source_authority"] == "writer"
        ),
        "workflows": records,
    }


def markdown_index(index: dict[str, Any]) -> str:
    counts = index["reconciliation"]
    lines = [
        "# Workflow event index", "",
        "Generated by scripts/ci/workflow_registry.py from workflow YAML source.", "",
        "| Coverage | Count |", "|---|---:|",
        f"| Workflow YAML files | {counts['directory_count']} |",
        f"| Generated catalog records | {counts['catalog_count']} |",
        f"| Indexed records | {counts['indexed_count']} |",
        f"| Reconciliation | {counts['status']} |", "",
        f"Catalog source fingerprint: {index.get('source_fingerprint')}.", "",
        f"Authority conflicts: {len(index['authority_conflicts'])}.",
        f"Uncatalogued source writers: {len(index['uncatalogued_source_writers'])}.", "",
        "| Workflow | Events | Dispatch inputs | Job selectors | Declared permission authority | API write methods |",
        "|---|---|---|---|---|---|",
    ]
    for item in index["workflows"]:
        inputs = ", ".join(item["workflow_dispatch_inputs"]) or "—"
        selectors = ", ".join(name for name, value in item["job_selectors"].items() if value.get("if")) or "—"
        authority = item["source_authority"]
        if item["authority_conflict"]:
            authority += f" (catalog: {item['catalog_authority']})"
        methods = ", ".join(item["api_write_methods"]) or "—"
        lines.append(f"| {item['path']} | {', '.join(item['events']) or '—'} | {inputs} | {selectors} | {authority} | {methods} |")
    if counts["missing_from_catalog"] or counts["missing_from_directory"]:
        lines.extend(["", "## Catalog drift", ""])
        lines.extend(f"- Missing from catalog: {path}" for path in counts["missing_from_catalog"])
        lines.extend(f"- Missing from directory: {path}" for path in counts["missing_from_directory"])
    if index["uncatalogued_source_writers"]:
        lines.extend(["", "## Uncatalogued source writers", ""])
        lines.extend(f"- {path}" for path in index["uncatalogued_source_writers"])
    lines.extend([
        "", "## Coverage semantics", "",
        "The JSON record preserves complete event configuration, activity types, branch/path/tag/workflow filters, workflow_dispatch inputs, workflow/job permissions, job conditions, dependencies, runners, environments, matrices, concurrency, action references, immutable SHA pins, and source blob SHAs.", "",
        "Authority is inferred from declared workflow/job permission scopes plus explicit gh api write methods. Indirect external-token effects still require source review. The index describes configured behavior; workflow-run evidence establishes execution, while job conclusions and artifacts establish outcomes.", "",
        "Machine-readable index: docs/ops/generated/workflow-event-index.json.", "",
    ])
    return "\n".join(lines)


def rendered_registry(root: Path, index: dict[str, Any]) -> str | None:
    path = root / REGISTRY_PATH
    if not path.exists():
        return None
    registry = json.loads(path.read_text(encoding="utf-8"))
    sources = registry.setdefault("sources", [])
    catalog_source = next((item for item in sources if item.get("id") == "workflow-catalog"), None)
    index_source = next((item for item in sources if item.get("id") == "workflow-event-index"), None)
    catalog_bytes = (root / CATALOG_PATH).read_bytes()
    counts = index["reconciliation"]

    if catalog_source is not None:
        catalog_source["observed_workflow_count"] = counts["catalog_count"]
        catalog_source["source_fingerprint"] = index.get("source_fingerprint")
        catalog_source["blob_sha"] = git_blob_sha(catalog_bytes)
        catalog_source["freshness"] = "generated; refreshed through the trusted automation-docs lane"
    if index_source is not None:
        index_source["schema"] = SCHEMA_VERSION
        index_source["workflow_count"] = counts["indexed_count"]
        index_source["generator"] = "scripts/ci/workflow_registry.py"
        index_source["authority_basis"] = "Declared workflow/job permissions plus explicit gh api write methods"
        index_source["refresh"] = "Generated by the trusted master refresh after catalog generation"
        index_source.pop("next_schema", None)

    event_catalog = registry.setdefault("workflow_event_catalog", {})
    event_catalog["observed_workflow_count"] = counts["catalog_count"]
    if counts["missing_from_catalog"]:
        event_catalog["rule"] = (
            f"The generated catalog lists {counts['catalog_count']} workflows while the workflow directory contains "
            f"{counts['directory_count']}; missing from catalog: {', '.join(counts['missing_from_catalog'])}. "
            "The source-derived index preserves all directory workflows."
        )
    else:
        event_catalog["rule"] = (
            f"The generated catalog and workflow directory are in sync at {counts['directory_count']} workflows. "
            "The source-derived index preserves all workflow YAML details."
        )

    reconciliation = registry.setdefault("reconciliation", {})
    inventory = reconciliation.setdefault("workflow_inventory", {})
    inventory.update({
        "directory_yaml_count": counts["directory_count"],
        "catalog_record_count": counts["catalog_count"],
        "indexed_record_count": counts["indexed_count"],
        "status": counts["status"],
        "catalog_fingerprint": index.get("source_fingerprint"),
        "workflow_index": OUTPUT_JSON.as_posix(),
        "missing_from_catalog": counts["missing_from_catalog"],
        "missing_from_directory": counts["missing_from_directory"],
        "missing_from_index": [],
        "uncatalogued_source_writers": index["uncatalogued_source_writers"],
    })

    records = {item["path"]: item for item in index["workflows"]}
    previous_conflicts = {
        item.get("workflow"): item
        for item in reconciliation.get("workflow_authority_conflicts", [])
        if isinstance(item, dict) and item.get("workflow")
    }
    conflicts = []
    for workflow in index["authority_conflicts"]:
        item = records[workflow]
        conflicts.append({
            **previous_conflicts.get(workflow, {}),
            "workflow": workflow,
            "catalog_authority": item["catalog_authority"],
            "source_authority": item["source_authority"],
            "source_blob_sha": item["source_blob_sha"],
            "status": "SOURCE_VERIFIED_CONFLICT",
        })
    reconciliation["workflow_authority_conflicts"] = conflicts

    previous_overrides = {
        item.get("workflow"): item
        for item in registry.get("workflow_source_authority_overrides", [])
        if isinstance(item, dict) and item.get("workflow")
    }
    overrides = []
    for workflow in index["uncatalogued_source_writers"]:
        item = records[workflow]
        overrides.append({
            **previous_overrides.get(workflow, {}),
            "workflow": workflow,
            "source_blob_sha": item["source_blob_sha"],
            "catalog_status": "NOT_IN_CATALOG",
            "declared_permission_authority": item["declared_permission_authority"],
            "source_authority": item["source_authority"],
            "api_write_methods": item["api_write_methods"],
            "authority_basis": item["authority_basis"],
            "status": "SOURCE_VERIFIED_UNCATALOGUED_WRITER",
        })
    registry["workflow_source_authority_overrides"] = overrides
    return json.dumps(registry, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_outputs(root: Path = ROOT) -> None:
    index = build_index(root)
    json_text = json.dumps(index, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    markdown_text = markdown_index(index)
    registry_text = rendered_registry(root, index)
    outputs = [(OUTPUT_JSON, json_text), (OUTPUT_MD, markdown_text)]
    if registry_text is not None:
        outputs.append((REGISTRY_PATH, registry_text))
    for relative, content in outputs:
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")


def check_outputs(root: Path = ROOT) -> bool:
    index = build_index(root)
    json_text = json.dumps(index, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    markdown_text = markdown_index(index)
    registry_text = rendered_registry(root, index)
    outputs = [(OUTPUT_JSON, json_text), (OUTPUT_MD, markdown_text)]
    if registry_text is not None:
        outputs.append((REGISTRY_PATH, registry_text))
    stale = [
        relative.as_posix()
        for relative, expected in outputs
        if not (root / relative).exists() or (root / relative).read_text(encoding="utf-8") != expected
    ]
    if stale:
        print("workflow registry update required: " + ", ".join(stale), file=sys.stderr)
        return False
    print("workflow event index is current")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--write", action="store_true", help="write generated registry files")
    modes.add_argument("--check", action="store_true", help="check generated registry freshness")
    args = parser.parse_args()
    try:
        if args.write:
            write_outputs(args.root)
            return 0
        return 0 if check_outputs(args.root) else 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"workflow registry error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
