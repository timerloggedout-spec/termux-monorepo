#!/usr/bin/env python3
"""Validate the imported Claude skill mirror, registry, and discovery links."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / ".skills/index.json"
TAGS = ROOT / ".skills/tags.json"
AGENTS = ROOT / ".agents/skills"

def sha1(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

if not INDEX.is_file() or not TAGS.is_file():
    raise SystemExit("Registry files are missing; run import_claude_export.py first")

index = json.loads(INDEX.read_text(encoding="utf-8"))
tags = json.loads(TAGS.read_text(encoding="utf-8"))
entries = index.get("skills", [])
if index.get("skill_count") != len(entries) or len(entries) != 1299:
    raise SystemExit(f"Expected 1,299 indexed skills; found {len(entries)}")

ids = set()
for item in entries:
    sid = item["id"]
    if sid in ids:
        raise SystemExit(f"Duplicate skill ID: {sid}")
    ids.add(sid)
    source = ROOT / item["path"]
    if not source.is_file():
        raise SystemExit(f"Missing skill source: {item['path']}")
    if source.stat().st_size != item["bytes"]:
        raise SystemExit(f"Byte-size mismatch: {item['path']}")
    if sha1(source) != item["sha1"]:
        raise SystemExit(f"SHA-1 mismatch: {item['path']}")

    matches = [
        p for p in AGENTS.iterdir()
        if p.is_symlink() and p.resolve() == source.parent.resolve()
        and p.name.startswith("claude-")
    ]
    if not matches:
        raise SystemExit(f"No repo-local discovery symlink for {sid}")

for tag, tagged_ids in tags.get("tags", {}).items():
    if not isinstance(tag, str) or not set(tagged_ids).issubset(ids):
        raise SystemExit(f"Invalid tag mapping: {tag}")

print(f"PASS: {len(entries)} skills, hashes, registry tags, and discovery links verified")
