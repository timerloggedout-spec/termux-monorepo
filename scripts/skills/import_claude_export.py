#!/usr/bin/env python3
"""Import Claude's SKILL.md archive into the canonical Termux monorepo mirror.

Usage:
  python scripts/skills/import_claude_export.py --downloads "$HOME/storage/downloads"

The archive remains in Downloads. Extraction uses a temporary directory.
Existing .agents/skills entries are preserved; generated links use collision-safe names.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import tarfile
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
MIRROR = ROOT / "vendor/skills-mirror"
SOURCE = ROOT / "docs/ops/skills/source"
REGISTRY = ROOT / ".skills"
AGENTS = ROOT / ".agents/skills"


def digest(path: Path, algorithm: str = "sha1") -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError(f"CSV header missing: {path}")
        return list(reader.fieldnames), list(reader)


def normalized_member(name: str) -> PurePosixPath:
    p = PurePosixPath(name)
    parts = tuple(x for x in p.parts if x not in ("", ".", "./"))
    if p.is_absolute() or any(x == ".." for x in parts):
        raise ValueError(f"Unsafe archive path: {name}")
    return PurePosixPath(*parts)


def extract_safely(archive: Path, destination: Path) -> None:
    with tarfile.open(archive, "r:gz") as tar:
        for member in tar.getmembers():
            rel = normalized_member(member.name)
            if not rel.parts:
                continue
            if not (member.isfile() or member.isdir()):
                raise ValueError(f"Unsupported archive member type: {member.name}")
            target = destination.joinpath(*rel.parts)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                source = tar.extractfile(member)
                if source is None:
                    raise ValueError(f"Cannot read archive member: {member.name}")
                with source, target.open("wb") as out:
                    shutil.copyfileobj(source, out)
                os.chmod(target, member.mode & 0o755)


def stable_link_name(skill_id: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", skill_id.lower()).strip("-")[:64] or "skill"
    suffix = hashlib.sha256(skill_id.encode()).hexdigest()[:12]
    return f"claude-{slug}-{suffix}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--downloads", type=Path, required=True)
    args = parser.parse_args()
    downloads = args.downloads.expanduser().resolve()

    archive = downloads / "skills-SKILL-md-all.tar.gz"
    skills_csv = downloads / "skills-inventory.csv"
    skills_jsonl = downloads / "skills-inventory.jsonl"
    plugins_csv = downloads / "plugins-inventory.csv"
    checksums = downloads / "SHA256SUMS.txt"
    for path in (archive, skills_csv, skills_jsonl, plugins_csv, checksums):
        if not path.is_file():
            raise SystemExit(f"Required export file missing: {path}")

    _, rows = read_csv(skills_csv)
    plugin_fields, plugin_rows = read_csv(plugins_csv)
    required = {"namespace", "plugin_dir", "skill_path", "name", "description", "bytes", "sha1"}
    if not rows or not required.issubset(rows[0]):
        raise SystemExit("Skills inventory schema mismatch")

    with skills_jsonl.open(encoding="utf-8-sig") as stream:
        jsonl_rows = [json.loads(line) for line in stream if line.strip()]
    if len(rows) != 1299 or len(jsonl_rows) != len(rows):
        raise SystemExit(f"Inventory counts mismatch: CSV={len(rows)}, JSONL={len(jsonl_rows)}")

    MIRROR.mkdir(parents=True, exist_ok=True)
    SOURCE.mkdir(parents=True, exist_ok=True)
    REGISTRY.mkdir(parents=True, exist_ok=True)
    AGENTS.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="claude-skills-") as temp:
        extracted = Path(temp)
        extract_safely(archive, extracted)

        by_path: dict[str, tuple[dict[str, str], Path]] = {}
        for row in rows:
            raw = row["skill_path"].replace("\\", "/").lstrip("./")
            rel = normalized_member(raw)
            source = extracted.joinpath(*rel.parts)
            key = rel.as_posix()
            if key in by_path or not source.is_file() or source.name != "SKILL.md":
                raise SystemExit(f"Missing, duplicate, or invalid archive path: {raw}")
            if source.stat().st_size != int(row["bytes"]):
                raise SystemExit(f"Byte count mismatch: {raw}")
            if digest(source) != row["sha1"].strip().lower():
                raise SystemExit(f"SHA-1 mismatch: {raw}")
            by_path[key] = (row, source)

        archive_skills = {
            p.relative_to(extracted).as_posix()
            for p in extracted.rglob("SKILL.md")
        }
        if archive_skills != set(by_path):
            missing = sorted(archive_skills - set(by_path))
            absent = sorted(set(by_path) - archive_skills)
            raise SystemExit(f"Archive/inventory path mismatch; unindexed={missing[:5]}, absent={absent[:5]}")

        # Validate the complete source set before writing any canonical files.
        for key, (row, source) in by_path.items():
            target = MIRROR / key
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and digest(target) != row["sha1"].strip().lower():
                raise SystemExit(f"Existing mirror file differs; review before overwrite: {target}")
            if not target.exists():
                shutil.copy2(source, target)

    # Preserve source inventories byte-for-byte.
    for src in (skills_csv, skills_jsonl, plugins_csv, checksums):
        dst = SOURCE / src.name
        if dst.exists() and digest(dst, "sha256") != digest(src, "sha256"):
            raise SystemExit(f"Existing source inventory differs; review before overwrite: {dst}")
        if not dst.exists():
            shutil.copy2(src, dst)

    entries = []
    tags: dict[str, set[str]] = defaultdict(set)
    used_link_names = set()
    for row in rows:
        rel = normalized_member(row["skill_path"].replace("\\", "/").lstrip("./"))
        skill_id = f'{row["namespace"]}:{row["plugin_dir"]}/{row["name"]}'
        target_dir = MIRROR.joinpath(*rel.parts).parent
        entries.append({
            "id": skill_id,
            "namespace": row["namespace"],
            "plugin_dir": row["plugin_dir"],
            "name": row["name"],
            "description": row["description"],
            "path": (Path("vendor/skills-mirror") / rel).as_posix(),
            "bytes": int(row["bytes"]),
            "sha1": row["sha1"].lower(),
        })
        terms = set(re.findall(r"[a-z0-9][a-z0-9+.#_-]{1,}", " ".join(
            (row["namespace"], row["plugin_dir"], row["name"], row["description"])
        ).lower()))
        for term in terms:
            tags[term].add(skill_id)

        base = stable_link_name(skill_id)
        link_name = base
        suffix = 1
        while link_name in used_link_names:
            suffix += 1
            link_name = f"{base}-{suffix}"
        used_link_names.add(link_name)
        link = AGENTS / link_name
        relative_target = os.path.relpath(target_dir, AGENTS)
        if link.is_symlink():
            if link.resolve() != target_dir.resolve():
                raise SystemExit(f"Existing generated link points elsewhere: {link}")
        elif link.exists():
            # Preserve existing user/repo content; select a deterministic alternate name.
            link_name = f"{base}-imported"
            link = AGENTS / link_name
            n = 1
            while link.exists() or link.is_symlink():
                n += 1
                link = AGENTS / f"{link_name}-{n}"
            link.symlink_to(relative_target, target_is_directory=True)
        else:
            link.symlink_to(relative_target, target_is_directory=True)

    entries.sort(key=lambda x: (x["namespace"], x["plugin_dir"], x["name"]))
    stamp = datetime.now(timezone.utc).isoformat()
    archive_sha = digest(archive, "sha256")
    (REGISTRY / "index.json").write_text(json.dumps({
        "schema_version": "1.0.0",
        "generated_at": stamp,
        "source": {"archive": archive.name, "archive_sha256": archive_sha},
        "skill_count": len(entries),
        "skills": entries,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (REGISTRY / "tags.json").write_text(json.dumps({
        "schema_version": "1.0.0",
        "tags": {k: sorted(v) for k, v in sorted(tags.items())},
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    skill_dirs = {r["plugin_dir"] for r in rows}
    plugin_dirs = {r["plugin_dir"] for r in plugin_rows}
    (SOURCE / "inventory-reconciliation.json").write_text(json.dumps({
        "skills_rows": len(rows),
        "jsonl_rows": len(jsonl_rows),
        "plugin_inventory_rows": len(plugin_rows),
        "unique_skill_plugin_dir_values": len(skill_dirs),
        "unique_plugin_inventory_dir_values": len(plugin_dirs),
        "skill_dirs_missing_from_plugin_inventory": sorted(skill_dirs - plugin_dirs),
        "plugin_inventory_dirs_without_skill_rows": sorted(plugin_dirs - skill_dirs),
        "plugin_inventory_columns": plugin_fields,
    }, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "schema_version": "1.0.0",
        "archive": archive.name,
        "archive_sha256": archive_sha,
        "skills": len(entries),
        "plugin_inventory_rows": len(plugin_rows),
        "canonical_root": "vendor/skills-mirror",
        "discovery_root": ".agents/skills",
        "registry": ".skills/index.json",
        "tags": ".skills/tags.json",
        "generated_at": stamp,
    }
    (SOURCE / "source-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "IMPORTED",
        "skills": len(entries),
        "plugin_inventory_rows": len(plugin_rows),
        "unique_skill_plugin_dirs": len(skill_dirs),
        "unique_plugin_inventory_dirs": len(plugin_dirs),
        "search_tags": len(tags),
        "archive_sha256": archive_sha,
        "mirror": str(MIRROR),
        "registry": str(REGISTRY / "index.json"),
        "discovery_links": len(entries),
        "existing_agent_entries_preserved": True,
    }, indent=2))


if __name__ == "__main__":
    main()
