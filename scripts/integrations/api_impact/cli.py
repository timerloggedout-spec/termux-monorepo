"""CLI for deterministic API Impact Mapper report generation."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from .report import DEFAULT_API_PATH_PATTERNS, build_report


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# API Impact Review — PR #{report['pull_request']}", "",
        f"- **State:** `{report['state']}`",
        f"- **Repository:** `{report['repository']}`",
        f"- **Base:** `{report['base_sha']}`",
        f"- **Head:** `{report['head_sha']}`",
        f"- **API surface files:** {len(report['api_surface_files'])}",
        f"- **Extracted changes:** {len(report['changes'])}",
        f"- **Impacts:** {len(report['impacts'])}", "",
        "> Advisory only: this report does not approve compatibility, merge, deploy, or replace human review and repository gates.",
        "", "## Changed API surface",
    ]
    lines.extend(f"- `{path}`" for path in report["api_surface_files"])
    if not report["api_surface_files"]:
        lines.append("- None detected by configured path policy.")
    lines.extend(["", "## API changes", ""])
    if report["changes"]:
        lines.extend(["| Change | Type | Location | Description |", "|---|---|---|---|"])
        for item in report["changes"]:
            cells = [item[k] for k in ("change_id", "change_type", "location", "description")]
            lines.append("| " + " | ".join(str(v).replace("|", "\\|").replace("\n", " ") for v in cells) + " |")
    else:
        lines.append("No extracted changes supplied.")
    lines.extend(["", "## Breaking-change classifications", ""])
    if report["classifications"]:
        lines.extend(["| Change | Category | Confidence | Rationale |", "|---|---|---|---|"])
        for item in report["classifications"]:
            cells = [item[k] for k in ("change_id", "category", "confidence", "rationale")]
            lines.append("| " + " | ".join(str(v).replace("|", "\\|").replace("\n", " ") for v in cells) + " |")
    else:
        lines.append("No classifications supplied.")
    lines.extend(["", "## Consumer, test, and documentation impacts", ""])
    if report["impacts"]:
        lines.extend(["| Impact | Change | Affected object | Priority | Status | Recommended action |", "|---|---|---|---|---|---|"])
        for item in report["impacts"]:
            cells = [item[k] for k in ("impact_id", "change_id", "affected_object", "priority", "status", "recommended_action")]
            lines.append("| " + " | ".join(str(v).replace("|", "\\|").replace("\n", " ") for v in cells) + " |")
    else:
        lines.append("No impact items supplied.")
    for title, key in (("Missing fields", "missing_fields"), ("Limitations", "limitations"), ("Sanitized provider errors", "errors")):
        lines.extend(["", f"## {title}", ""])
        lines.extend(f"- {value}" for value in report[key]) if report[key] else lines.append("- None reported.")
    lines.extend([
        "", "## Provenance", "",
        f"- Provider: {report['provenance']['provider']}",
        f"- Capture: {report['provenance']['capture_method']}",
        f"- Attribution: {report['provenance']['attribution']}",
        f"- Evidence records: {len(report['evidence'])}",
        "- Privacy attestation: normalized report excludes raw prompts and secrets.", "",
    ])
    return "\n".join(lines)


def _git_changed_paths(base: str, head: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACMR", "-z", f"{base}...{head}"],
        check=True, capture_output=True,
    )
    return [path.decode("utf-8") for path in result.stdout.split(b"\0") if path]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--pr-number", required=True, type=int)
    parser.add_argument("--changed-path", action="append", default=[])
    parser.add_argument("--mapper-input")
    parser.add_argument("--config", default="config/integrations/api-impact-paths.json")
    parser.add_argument("--output-json", default="api-impact-report.json")
    parser.add_argument("--output-markdown", default="api-impact-report.md")
    args = parser.parse_args(argv)
    try:
        changed = args.changed_path or _git_changed_paths(args.base, args.head)
        config_path = Path(args.config)
        patterns = list(DEFAULT_API_PATH_PATTERNS)
        if config_path.is_file():
            config = json.loads(config_path.read_text(encoding="utf-8"))
            if config.get("schema_version") != "1.0.0" or not isinstance(config.get("api_surface_patterns"), list) or not config["api_surface_patterns"]:
                raise ValueError("invalid API surface path configuration")
            patterns = config["api_surface_patterns"]
        mapper = json.loads(Path(args.mapper_input).read_text(encoding="utf-8")) if args.mapper_input else None
        report = build_report(args.repository, args.base, args.head, args.pr_number, changed, mapper, patterns)
        json_path, md_path = Path(args.output_json), Path(args.output_markdown)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        md_path.write_text(render_markdown(report), encoding="utf-8")
        print(f"API impact report: {report['state']} ({len(report['api_surface_files'])} API surface files)")
        return 0
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"api-impact-review: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
