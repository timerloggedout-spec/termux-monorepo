#!/usr/bin/env python3
"""Generate a source-derived GitHub Actions event and selector index."""
from __future__ import annotations

import argparse
import hashlib
import json
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


def source_authority(permission_data: dict[str, Any]) -> str:
    groups = [mapping(permission_data.get("workflow"))]
    groups.extend(mapping(value) for value in mapping(permission_data.get("jobs")).values())
    if any(value == "write-all" for group in groups for value in group.values()):
        return "writer"
    if any(scope in {"contents", "pull-requests"} and value == "write"
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
    events = event_config(document.get("on"))
    permission_data = permissions(document)
    jobs = mapping(document.get("jobs"))
    pins = sorted({
        str(step["uses"])
        for job in jobs.values()
        for step in mapping(job).get("steps", []) or []
        if isinstance(step, dict) and "uses" in step and "@" in str(step["uses"])
    })
    return {
        "path": path,
        "name": str(document.get("name") or Path(path).stem),
        "events": sorted(events),
        "event_config": events,
        "workflow_dispatch_inputs": dispatch_inputs(events),
        "permissions": permission_data,
        "job_selectors": job_selectors(document),
        "jobs": sorted(str(name) for name in jobs),
        "action_pins": pins,
        "source_authority": source_authority(permission_data),
    }


def git_blob_sha(content: bytes) -> str:
    header = f"blob {len(content)}\\0".encode("ascii")
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
        "workflows": records,
    }


def markdown_index(index: dict[str, Any]) -> str:
    counts = index["reconciliation"]
    lines = [
        "# Workflow event index", "",
        "Generated by `scripts/ci/workflow_registry.py`; workflow YAML is the source for event filters, dispatch inputs, permissions, and job selectors.", "",
        "| Coverage | Count |", "|---|---:|",
        f"| Workflow YAML files | {counts['directory_count']} |",
        f"| Generated catalog records | {counts['catalog_count']} |",
        f"| Indexed records | {counts['indexed_count']} |",
        f"| Reconciliation | `{counts['status']}` |", "",
        f"Catalog source fingerprint: `{index.get('source_fingerprint')}`.", "",
        f"Authority conflicts: {len(index['authority_conflicts'])}.", "",
        "| Workflow | Events | Dispatch inputs | Job selectors | Source authority |",
        "|---|---|---|---|---|",
    ]
    for item in index["workflows"]:
        inputs = ", ".join(item["workflow_dispatch_inputs"]) or "—"
        selectors = ", ".join(name for name, value in item["job_selectors"].items() if value.get("if")) or "—"
        authority = item["source_authority"]
        if item["authority_conflict"]:
            authority += f" (catalog: {item['catalog_authority']})"
        lines.append(f"| `{item['path']}` | {', '.join(item['events']) or '—'} | {inputs} | {selectors} | {authority} |")
    lines.extend([
        "", "## Coverage semantics", "",
        "The JSON record preserves each event's complete YAML configuration, including activity types and branch/path/tag/workflow filters. It also preserves workflow_dispatch inputs, workflow/job permissions, job conditions, dependencies, runners, environments, matrices, action references, and source blob SHAs.", "",
        "The index describes configured behavior. Workflow-run evidence establishes execution; job conclusions and artifacts establish outcomes.", "",
        "Machine-readable index: `docs/ops/generated/workflow-event-index.json`.", "",
    ])
    return "\\n".join(lines)


def rendered_outputs(root: Path = ROOT) -> tuple[str, str]:
    index = build_index(root)
    return (
        json.dumps(index, indent=2, sort_keys=True, ensure_ascii=False) + "\\n",
        markdown_index(index),
    )


def write_outputs(root: Path = ROOT) -> None:
    json_text, markdown_text = rendered_outputs(root)
    for relative, content in ((OUTPUT_JSON, json_text), (OUTPUT_MD, markdown_text)):
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")


def check_outputs(root: Path = ROOT) -> bool:
    json_text, markdown_text = rendered_outputs(root)
    stale = [
        relative.as_posix()
        for relative, expected in ((OUTPUT_JSON, json_text), (OUTPUT_MD, markdown_text))
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
