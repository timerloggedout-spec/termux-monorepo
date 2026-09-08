#!/usr/bin/env python3
"""Generate and validate the autonomous-automation documentation catalog.

This utility treats workflow/configuration files as text data. It never executes
workflow YAML, imports repository modules, reads secrets, or interpolates event
content. The generated catalog is stable: it has no timestamp and uses a
content fingerprint for the enumerated control-plane sources.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_JSON = ROOT / "docs/ops/generated/automation-workflow-catalog.json"
OUTPUT_MD = ROOT / "docs/ops/generated/automation-workflow-catalog.md"
OUTPUT_ASSETS = ROOT / "docs/ops/generated/automation-diagram-assets.json"
DIAGRAM_DIR = ROOT / "docs/ops/diagrams"
GENERATED_DIR = ROOT / "docs/ops/generated"
SCHEMA_VERSION = 1

WORKFLOW_DIR = Path(".github/workflows")
CONTROL_PLANE_EXTRAS = (
    Path(".github/actions/model-router/action.yml"),
    Path(".github/actions/http-llm-invoke/action.yml"),
    Path("scripts/model_router.py"),
    Path("docs/schemas/model-success-matrix.yaml"),
    Path("docs/schemas/llm-leaderboard-matrix.yaml"),
    Path("docs/schemas/model-rotation.yaml"),
    Path("docs/schemas/routing-priority.yaml"),
    Path("docs/ops/OPERATOR_INTERACTIVE_ACTIONS.md"),
)

MATERIAL_PREFIXES = (
    ".github/workflows/",
    ".github/actions/",
    "scripts/model_router.py",
    "scripts/ci/automation_docs.py",
    "docs/schemas/model-success-matrix.yaml",
    "docs/schemas/llm-leaderboard-matrix.yaml",
    "docs/schemas/model-rotation.yaml",
    "docs/schemas/routing-priority.yaml",
    "docs/ops/OPERATOR_INTERACTIVE_ACTIONS.md",
    "docs/ops/automation-decision-tree.md",
    "docs/ops/diagrams/",
    "docs/proposals/active/actions-refinements/",
    "docs/proposals/active/rate-limit-rotation/",
)
GENERATED_PREFIX = "docs/ops/generated/"


@dataclass(frozen=True)
class WorkflowRecord:
    path: str
    name: str
    domain: str
    triggers: tuple[str, ...]
    schedules: tuple[str, ...]
    concurrency: str
    authority: str
    jobs: tuple[str, ...]
    action_pins: tuple[str, ...]


def normalize_path(value: str) -> str:
    """Return a safe repository-relative POSIX path or raise ValueError."""
    if not isinstance(value, str) or not value:
        raise ValueError("path must be a non-empty string")
    candidate = value.replace("\\", "/")
    path = PurePosixPath(candidate)
    if path.is_absolute() or ".." in path.parts or candidate.startswith("./"):
        raise ValueError(f"path must be repository-relative: {value!r}")
    return path.as_posix()


def classify_material_paths(values: Iterable[str]) -> dict[str, object]:
    """Classify changed repository paths without resolving or executing them."""
    normalized = [normalize_path(value) for value in values]
    material = [
        value
        for value in normalized
        if any(value == prefix or value.startswith(prefix) for prefix in MATERIAL_PREFIXES)
    ]
    generated = [value for value in normalized if value.startswith(GENERATED_PREFIX)]
    high_impact = [
        value
        for value in material
        if value.startswith(".github/workflows/")
        or value.startswith(".github/actions/")
        or value in {
            "scripts/model_router.py",
            "docs/schemas/model-success-matrix.yaml",
            "docs/schemas/llm-leaderboard-matrix.yaml",
            "docs/schemas/model-rotation.yaml",
            "docs/schemas/routing-priority.yaml",
            "docs/ops/OPERATOR_INTERACTIVE_ACTIONS.md",
        }
    ]
    if high_impact:
        status = "high-impact control-plane review required"
    elif material:
        status = "documentation update required"
    elif generated:
        status = "generated-documentation-only"
    else:
        status = "no diagram impact"
    return {
        "status": status,
        "material_paths": material,
        "high_impact_paths": high_impact,
    }


def _section(lines: list[str], key: str) -> list[str]:
    """Return indented YAML-looking lines below a top-level key, text only."""
    result: list[str] = []
    active = False
    prefix = f"{key}:"
    for line in lines:
        if line.startswith(prefix):
            active = True
            continue
        if active and line and not line.startswith((" ", "\t", "#")):
            break
        if active:
            result.append(line)
    return result


def _top_scalar(lines: list[str], key: str) -> str:
    pattern = re.compile(rf"^{re.escape(key)}:\s*(.*?)\s*(?:#.*)?$")
    for line in lines:
        match = pattern.match(line)
        if match:
            return match.group(1).strip(" '\"")
    return ""


def _domain(path: str, name: str) -> str:
    value = f"{path} {name}".lower()
    if any(token in value for token in ("scorecard", "codeql", "dependency", "actionlint", "repo-gate", "termux-smoke", "integrity")):
        return "validation-security"
    if "context-relationship" in value or "proposal" in value:
        return "governance-relationships"
    if any(token in value for token in ("wiki", "reconcile", "fork-sync", "repository-surface", "workflow-surface")):
        return "reconciliation-publishing"
    if any(token in value for token in ("peer", "provider", "gemini", "pull request review", "pr review")):
        return "peer-provider-review"
    if any(token in value for token in ("jules", "deepseek", "agentic", "agent-", "hub")):
        return "agentic-development"
    return "repository-automation"


def _authority(text: str) -> str:
    if re.search(r"(?:contents|pull-requests):\s*write", text):
        return "writer"
    if re.search(r"issues:\s*write|checks:\s*write", text):
        return "bounded-state-write"
    if re.search(r"security-events:\s*write|id-token:\s*write", text):
        return "advisory-publisher"
    return "read-only-or-advisory"


def _triggers(lines: list[str]) -> tuple[str, ...]:
    on_lines = _section(lines, "on")
    values: list[str] = []
    for line in on_lines:
        match = re.match(r"^\s{2}([A-Za-z0-9_]+):(?:\s|$)", line)
        if match:
            values.append(match.group(1))
    return tuple(sorted(set(values)))


def _schedules(lines: list[str]) -> tuple[str, ...]:
    return tuple(sorted(re.findall(r"cron:\s*[\"']?([^\"'#]+)", "\n".join(lines))))


def _jobs(lines: list[str]) -> tuple[str, ...]:
    jobs = _section(lines, "jobs")
    values = [match.group(1) for line in jobs if (match := re.match(r"^  ([A-Za-z0-9_-]+):\s*$", line))]
    return tuple(sorted(set(values)))


def _pins(text: str) -> tuple[str, ...]:
    values = re.findall(r"uses:\s*([^\s#]+@[0-9a-f]{40})", text)
    return tuple(sorted(set(values)))


def parse_workflow(path: Path, root: Path = ROOT) -> WorkflowRecord:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    relative = path.relative_to(root).as_posix()
    name = _top_scalar(lines, "name") or path.stem
    concurrency = ""
    concurrency_lines = _section(lines, "concurrency")
    if concurrency_lines:
        concurrency = " ".join(line.strip() for line in concurrency_lines if line.strip())
    return WorkflowRecord(
        path=relative,
        name=name,
        domain=_domain(relative, name),
        triggers=_triggers(lines),
        schedules=_schedules(lines),
        concurrency=concurrency,
        authority=_authority(text),
        jobs=_jobs(lines),
        action_pins=_pins(text),
    )


def control_plane_paths(root: Path = ROOT) -> list[Path]:
    paths = sorted((root / WORKFLOW_DIR).glob("*.yml"))
    paths.extend(root / item for item in CONTROL_PLANE_EXTRAS if (root / item).exists())
    return sorted(paths)


def fingerprint(paths: Iterable[Path], root: Path = ROOT) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def diagram_asset_manifest(root: Path = ROOT) -> dict[str, object]:
    """Return stable source/render hashes for every committed decision-tree asset."""
    diagram_dir = root / "docs/ops/diagrams"
    generated_dir = root / "docs/ops/generated"
    assets: list[dict[str, str]] = []
    for source in sorted(diagram_dir.glob("*.mmd")):
        render = generated_dir / f"{source.stem}.png"
        if not render.exists():
            raise ValueError(f"missing rendered diagram for {source.relative_to(root).as_posix()}")
        assets.append(
            {
                "source": source.relative_to(root).as_posix(),
                "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "render": render.relative_to(root).as_posix(),
                "render_sha256": hashlib.sha256(render.read_bytes()).hexdigest(),
            }
        )
    if not assets:
        raise ValueError("no Mermaid decision-tree sources found")
    return {"schema_version": SCHEMA_VERSION, "assets": assets}


def build_catalog(root: Path = ROOT) -> dict[str, object]:
    workflow_paths = sorted((root / WORKFLOW_DIR).glob("*.yml"))
    records = [asdict(parse_workflow(path, root)) for path in workflow_paths]
    paths = control_plane_paths(root)
    return {
        "schema_version": SCHEMA_VERSION,
        "source_fingerprint": fingerprint(paths, root),
        "workflow_count": len(records),
        "workflows": records,
        "material_change_rules": {
            "high_impact": [
                ".github/workflows/**",
                ".github/actions/**",
                "scripts/model_router.py",
                "docs/schemas/model-success-matrix.yaml",
                "docs/schemas/llm-leaderboard-matrix.yaml",
                "docs/schemas/model-rotation.yaml",
                "docs/schemas/routing-priority.yaml",
                "docs/ops/OPERATOR_INTERACTIVE_ACTIONS.md",
            ],
            "documentation_required": list(MATERIAL_PREFIXES),
        },
    }


def markdown_catalog(catalog: dict[str, object]) -> str:
    lines = [
        "# Generated Automation Workflow Catalog",
        "",
        "This file is generated by `scripts/ci/automation_docs.py`; do not edit it manually.",
        "",
        f"- Schema version: `{catalog['schema_version']}`",
        f"- Control-plane fingerprint: `{catalog['source_fingerprint']}`",
        f"- Workflow count: `{catalog['workflow_count']}`",
        "",
        "| Workflow | Domain | Triggers | Schedule | Authority | Jobs |",
        "|---|---|---|---|---|---|",
    ]
    for item in catalog["workflows"]:
        lines.append(
            "| `{path}` | {domain} | {triggers} | {schedules} | {authority} | {jobs} |".format(
                path=item["path"],
                domain=item["domain"],
                triggers=", ".join(item["triggers"]) or "manual/reusable",
                schedules=", ".join(item["schedules"]) or "—",
                authority=item["authority"],
                jobs=", ".join(item["jobs"]) or "—",
            )
        )
    lines.extend(
        [
            "",
            "## Freshness interpretation",
            "",
            "A change to a material path requires catalog regeneration and diagram review. A high-impact path additionally requires a control-plane review signal. The classifier is deterministic and treats paths as data only.",
            "",
        ]
    )
    return "\n".join(lines)


def rendered_outputs(root: Path = ROOT) -> tuple[str, str, str]:
    catalog = build_catalog(root)
    assets = diagram_asset_manifest(root)
    json_text = json.dumps(catalog, indent=2, sort_keys=True) + "\n"
    asset_text = json.dumps(assets, indent=2, sort_keys=True) + "\n"
    return json_text, markdown_catalog(catalog), asset_text


def write_outputs(root: Path = ROOT) -> None:
    json_text, markdown_text, asset_text = rendered_outputs(root)
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json_text, encoding="utf-8")
    OUTPUT_MD.write_text(markdown_text, encoding="utf-8")
    OUTPUT_ASSETS.write_text(asset_text, encoding="utf-8")


def check_outputs(root: Path = ROOT) -> bool:
    json_text, markdown_text, asset_text = rendered_outputs(root)
    expected = {OUTPUT_JSON: json_text, OUTPUT_MD: markdown_text, OUTPUT_ASSETS: asset_text}
    stale: list[str] = []
    for path, value in expected.items():
        if path.exists() and path.read_text(encoding="utf-8") == value:
            continue
        try:
            stale.append(path.relative_to(root).as_posix())
        except ValueError:
            stale.append(path.as_posix())
    if stale:
        print("documentation update required: " + ", ".join(stale), file=sys.stderr)
        return False
    print("automation documentation catalog is current")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write normalized catalog outputs")
    parser.add_argument("--check", action="store_true", help="fail when generated outputs are stale")
    parser.add_argument("--classify-path", action="append", default=[], help="classify a repository-relative changed path")
    args = parser.parse_args()
    if sum(bool(value) for value in (args.write, args.check, args.classify_path)) != 1:
        parser.error("select exactly one of --write, --check, or --classify-path")
    try:
        if args.classify_path:
            print(json.dumps(classify_material_paths(args.classify_path), sort_keys=True))
            return 0
        if args.write:
            write_outputs()
            return 0
        return 0 if check_outputs() else 1
    except ValueError as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
