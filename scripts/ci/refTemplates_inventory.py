#!/usr/bin/env python3
"""Inventory refTemplates slots and enforce template + sMods contracts.

Offline/stdlib-only. Gitlink validation reads the index; it never initializes
or fetches submodules.
"""

from __future__ import annotations

import argparse
import configparser
import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / "refTemplates"
SLOTS_RE = re.compile(r"^(\d{2}|[0-9]+)_")
SMODS_PREFIX = "refTemplates/smods/"
EXCLUDED_TEMPLATE_SLOTS = {"00_Index", "17_Papers"}


def slots() -> list[Path]:
    if not REF.is_dir() or REF.is_symlink():
        return []
    return [
        path for path in sorted(REF.iterdir())
        if path.is_dir() and not path.is_symlink()
        and (SLOTS_RE.match(path.name) or path.name == "smods")
    ]


def _template_child(slot: Path, child: Path) -> dict:
    if child.is_symlink():
        return {
            "name": child.name,
            "path": str(child.relative_to(ROOT)),
            "is_symlink": True,
            "has_source": False,
            "source_nonempty": False,
            "has_readme": False,
            "readme_nonempty": False,
            "has_integration_manifest": False,
            "source_preview": None,
        }
    source = child / "SOURCE.txt"
    readme = child / "README.md"
    manifest = child / "integration.json"
    manifest_valid = False
    if manifest.is_file() and not manifest.is_symlink():
        try:
            manifest_valid = isinstance(json.loads(manifest.read_text(encoding="utf-8")), dict)
        except (OSError, json.JSONDecodeError):
            manifest_valid = False
    return {
        "name": child.name,
        "path": str(child.relative_to(ROOT)),
        "is_symlink": child.is_symlink(),
        "has_source": source.is_file() and not source.is_symlink(),
        "source_nonempty": source.is_file() and not source.is_symlink() and bool(source.read_text(encoding="utf-8").strip()),
        "has_readme": readme.is_file() and not readme.is_symlink(),
        "readme_nonempty": readme.is_file() and not readme.is_symlink() and bool(readme.read_text(encoding="utf-8").strip()),
        "has_integration_manifest": manifest.is_file() and not manifest.is_symlink(),
        "integration_manifest_valid": manifest_valid,
        "source_preview": source.read_text(encoding="utf-8").strip().splitlines()[0]
        if source.is_file() and not source.is_symlink() and source.stat().st_size else None,
    }


def inventory_entry(slot: Path) -> dict:
    children = [
        child.name for child in sorted(slot.iterdir())
        if child.is_dir() or child.suffix in {".md", ".txt"}
    ]
    template_children = []
    if slot.name not in EXCLUDED_TEMPLATE_SLOTS and slot.name != "smods":
        template_children = [
            _template_child(slot, child)
            for child in sorted(slot.iterdir())
            if child.is_dir()
        ]
    research_children = template_children if slot.name.startswith("15_") else []
    return {
        "slot": slot.name,
        "path": str(slot.relative_to(ROOT)),
        "entries": children,
        "template_children": template_children,
        "research_children": research_children,
        "collected_at": datetime.now(UTC).isoformat(),
    }


def validate(entries: list[dict]) -> list[str]:
    failures: list[str] = []
    for entry in entries:
        slot = entry.get("slot", "")
        templates = entry.get("template_children")
        if templates is None:
            # Backward-compatible validation of previously emitted inventory.
            templates = entry.get("research_children", [])
        for template in templates:
            path = template.get("path") or f"{slot}/{template.get('name', '<unknown>')}"
            if template.get("is_symlink"):
                failures.append(f"{path}: template directory must not be a symlink")
                continue
            if not template.get("has_readme") or not template.get("readme_nonempty", True):
                failures.append(f"{path}: missing or empty regular README.md")
            if not template.get("has_source") or not template.get("source_nonempty", True):
                failures.append(f"{path}: missing or empty regular SOURCE.txt")
            if slot == "01_Agent_Runtime":
                if not template.get("has_integration_manifest"):
                    failures.append(f"{path}: runtime integration template requires integration.json")
                elif not template.get("integration_manifest_valid", True):
                    failures.append(f"{path}: integration.json must be valid JSON with an object root")
    return failures


def validate_smods_contract(module_entries: list[dict], gitlinks: dict[str, str]) -> list[str]:
    """Require every sMods pin to be a shallow HTTPS submodule and exact gitlink."""
    errors: list[str] = []
    modules: dict[str, dict] = {}
    for index, entry in enumerate(module_entries):
        path = entry.get("path")
        if not isinstance(path, str) or not path.startswith(SMODS_PREFIX):
            continue
        parts = Path(path).parts
        if len(parts) != 3 or ".." in parts:
            errors.append(f".gitmodules entry {index}: sMods path must be one direct child of refTemplates/smods/")
            continue
        if path in modules:
            errors.append(f".gitmodules: duplicate sMods path {path}")
        modules[path] = entry
        url = entry.get("url")
        parsed = urlsplit(url) if isinstance(url, str) else None
        if not parsed or parsed.scheme != "https" or parsed.netloc != "github.com" or parsed.username or parsed.password:
            errors.append(f"{path}: sMods source must be a credential-free HTTPS GitHub URL")
        if entry.get("shallow") is not True:
            errors.append(f"{path}: sMods submodule must set shallow = true")

    module_paths = set(modules)
    gitlink_paths = {path for path in gitlinks if path.startswith(SMODS_PREFIX)}
    for path in sorted(module_paths - gitlink_paths):
        errors.append(f"{path}: .gitmodules entry has no 160000 gitlink")
    for path in sorted(gitlink_paths - module_paths):
        errors.append(f"{path}: 160000 gitlink has no .gitmodules entry")
    for path in sorted(gitlink_paths & module_paths):
        sha = gitlinks[path]
        if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
            errors.append(f"{path}: gitlink must pin an exact 40-character lowercase commit SHA")
    return errors


def validate_smods(root: Path = ROOT) -> list[str]:
    smods_root = root / "refTemplates/smods"
    if smods_root.is_symlink() or not smods_root.is_dir():
        return ["refTemplates/smods: missing regular directory or symlinked root"]
    modules_path = root / ".gitmodules"
    if modules_path.is_symlink() or not modules_path.is_file():
        return [".gitmodules: missing regular file"]
    parser = configparser.ConfigParser(interpolation=None, strict=True)
    try:
        parser.read(modules_path, encoding="utf-8")
        entries = []
        for section in parser.sections():
            if not section.startswith("submodule "):
                continue
            entries.append({
                "path": parser.get(section, "path", fallback=""),
                "url": parser.get(section, "url", fallback=""),
                "shallow": parser.getboolean(section, "shallow", fallback=False),
            })
        result = subprocess.run(
            ["git", "ls-files", "--stage"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
    except (configparser.Error, OSError, subprocess.CalledProcessError) as exc:
        return [f"unable to inspect sMods metadata/gitlinks: {exc}"]
    gitlinks: dict[str, str] = {}
    for line in result.stdout.splitlines():
        if not line.startswith("160000 ") or "\t" not in line:
            continue
        metadata, path = line.split("\t", 1)
        fields = metadata.split()
        if len(fields) >= 3:
            gitlinks[path] = fields[1]
    return validate_smods_contract(entries, gitlinks)


def validate_slot_roots(root: Path = ROOT) -> list[str]:
    ref_root = root / "refTemplates"
    if ref_root.is_symlink() or not ref_root.is_dir():
        return ["refTemplates: missing regular directory or symlinked root"]
    errors = []
    for path in sorted(ref_root.iterdir()):
        if SLOTS_RE.match(path.name) or path.name == "smods":
            if path.is_symlink():
                errors.append(f"{path.relative_to(root)}: template slot root must not be a symlink")
            elif not path.is_dir():
                errors.append(f"{path.relative_to(root)}: template slot root must be a directory")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="JSONL output path")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on contract failures")
    args = parser.parse_args()

    entries = [inventory_entry(slot) for slot in slots()]
    failures = validate_slot_roots(ROOT) + validate(entries) + validate_smods(ROOT)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as handle:
            for entry in entries:
                handle.write(json.dumps(entry, sort_keys=True) + "\n")
        print(f"OK: wrote {len(entries)} slot records → {args.output}")
    else:
        for entry in entries:
            print(json.dumps(entry, sort_keys=True))

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        if args.strict:
            return 1
    else:
        print(f"OK: validated {len(entries)} slots, template metadata, and sMods pins")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
