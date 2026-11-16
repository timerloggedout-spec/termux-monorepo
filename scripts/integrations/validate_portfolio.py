#!/usr/bin/env python3
"""Validate the integration portfolio, human catalog, Mintlify navigation, and sitemap."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs/integrations/registry.json"
CATALOG = ROOT / "docs/integrations/INTEGRATION-REGISTRY.md"
PORTFOLIO = ROOT / "docs/integrations/INTEGRATION-PORTFOLIO.md"
DOCS_CONFIG = ROOT / "docs.json"
SITEMAP = ROOT / "sitemap.md"

REQUIRED_FIELDS = {
    "id", "name", "category", "priority", "discovery_state",
    "session_evidence", "repo_skill_path", "repo_adapter_state",
    "authority", "write_boundary", "next_step", "sensitivity",
}


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"missing required file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")


def fail(errors: list[str]) -> int:
    for error in errors:
        print(f"FAIL: {error}", file=sys.stderr)
    return 1


def main() -> int:
    errors: list[str] = []
    registry = read_json(REGISTRY)
    docs = read_json(DOCS_CONFIG)

    if registry.get("schema_version") != "1.0.0":
        errors.append("registry schema_version must remain 1.0.0")
    entries = registry.get("integrations")
    if not isinstance(entries, list) or not entries:
        return fail(errors + ["registry.integrations must be a non-empty array"])

    ids: list[str] = []
    names: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"integrations[{index}] must be an object")
            continue
        missing = sorted(REQUIRED_FIELDS - set(entry))
        if missing:
            errors.append(f"{entry.get('id', index)} missing fields: {', '.join(missing)}")
        for key in REQUIRED_FIELDS - {"repo_skill_path"}:
            if key in entry and (not isinstance(entry[key], str) or not entry[key].strip()):
                errors.append(f"{entry.get('id', index)} has empty/non-string {key}")
        if isinstance(entry.get("id"), str):
            ids.append(entry["id"])
        if isinstance(entry.get("name"), str):
            names.add(entry["name"])
    if len(ids) != len(set(ids)):
        errors.append("registry contains duplicate integration IDs")
    if len(names) != len(entries):
        errors.append("registry contains missing or duplicate integration names")

    catalog_text = CATALOG.read_text(encoding="utf-8")
    catalog_names = set()
    for line in catalog_text.splitlines():
        if line.startswith("| ") and not line.startswith("| Integration") and not line.startswith("|---"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if cells:
                catalog_names.add(cells[0])
    if names != catalog_names:
        errors.append(
            "human catalog names do not match registry; "
            f"missing={sorted(names - catalog_names)}, extra={sorted(catalog_names - names)}"
        )

    updated_at = registry.get("updated_at")
    portfolio_text = PORTFOLIO.read_text(encoding="utf-8")
    audit = re.search(
        r"\*\*Audit performed:\*\*\s*(\d{4}-\d{2}-\d{2})\.\s*"
        r"\*\*Registry update date:\*\*\s*(\d{4}-\d{2}-\d{2})\.",
        portfolio_text,
    )
    if not audit:
        errors.append("portfolio must state separate audit and registry update dates")
    else:
        if audit.group(2) != updated_at:
            errors.append(
                f"portfolio registry update date {audit.group(2)} != registry updated_at {updated_at}"
            )

    navigation = docs.get("navigation", {})
    nav_paths: list[str] = []
    for tab in navigation.get("tabs", []):
        for group in tab.get("groups", []):
            nav_paths.extend(page for page in group.get("pages", []) if isinstance(page, str))
    for required in (
        "sitemap",
        "docs/integrations/INTEGRATION-PORTFOLIO",
        "docs/integrations/INTEGRATION-REGISTRY",
    ):
        if required not in nav_paths:
            errors.append(f"docs.json navigation missing {required}")

    for page in nav_paths:
        candidates = [
            ROOT / f"{page}.md",
            ROOT / f"{page}.mdx",
            ROOT / page / "index.md",
            ROOT / page / "index.mdx",
        ]
        if not any(candidate.is_file() for candidate in candidates):
            errors.append(f"docs.json navigation page has no source file: {page}")

    sitemap_text = SITEMAP.read_text(encoding="utf-8")
    if not sitemap_text.startswith("---\n") or "\n# Documentation sitemap\n" not in sitemap_text:
        errors.append("sitemap.md must have frontmatter and the Documentation sitemap H1")
    if len(re.findall(r"^## .+", sitemap_text, flags=re.MULTILINE)) < 2:
        errors.append("sitemap.md must contain grouped H2 sections")
    for page in nav_paths:
        if page != "sitemap" and f"](/{page})" not in sitemap_text:
            errors.append(f"sitemap.md missing navigation link: /{page}")

    if not isinstance(docs.get("description"), str) or not docs["description"].strip():
        errors.append("docs.json must define a site description")
    instructions = docs.get("markdown", {}).get("instructions")
    if not instructions or not isinstance(instructions, (str, list)):
        errors.append("docs.json markdown.instructions must provide agent guidance")

    if errors:
        return fail(errors)
    print(
        "OK: "
        f"{len(entries)} unique integrations; catalog matches; "
        f"dates aligned; {len(nav_paths)} navigation pages resolve; "
        "sitemap and agent metadata present"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
