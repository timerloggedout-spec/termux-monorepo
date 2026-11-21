#!/usr/bin/env python3
"""Build a provenance-bearing ArchWiz data-flow manifest from local JSONL inputs."""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

VERSION = "2.0.0"
HOME = Path.home()
DEFAULT_INDEX = HOME / "central_index.jsonl"
DEFAULT_FLOW_MAP = HOME / "tmp" / "data_flow_map.txt"
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "DATA_FLOW_MANIFEST.md"
DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[1]
EXTRA_DIRS = [
    ("deepcli/browser-data", "Chromium cache for deepcli"),
    ("deepseek-cli/browser-data", "Chromium cache for deepseek-cli"),
    ("deepseek-cli/browser-data-account2", "Duplicate browser cache"),
    ("deepseek-cli/browser-data-account2-clean", "Duplicate browser cache"),
    ("deepseek-cli/browser-data-account2-fresh", "Duplicate browser cache"),
    ("deepseek-cli/browser-data-account2-v2", "Duplicate browser cache"),
    ("storage/downloads/synthegration_exports", "UUID-based export blobs"),
    ("storage/downloads/synthegration_batch_export", "Named export subset"),
    ("storage/downloads/_doing/Tallah", "Mixed content"),
    ("storage/downloads/_doing/__1-resources", "Mixed content"),
    ("storage/downloads/_doing/downloads2sort", "Mixed content"),
    ("storage/downloads/_doing/referenceTemplates", "Reference templates"),
    ("cli-synthegration/conv_repo/sessions", "Content-addressed session store"),
]

def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def git_value(root, *args):
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", *args],
            capture_output=True, text=True, check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return result.stdout.strip() or "unknown"

def load_index(path):
    records, invalid = {}, 0
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                invalid += 1
                continue
            item_path = record.get("path") if isinstance(record, dict) else None
            if isinstance(item_path, str) and item_path.strip():
                records[item_path.strip()] = record
            else:
                invalid += 1
    return records, invalid

def load_flow_map(path):
    mapping = defaultdict(list)
    if not path.is_file():
        return mapping, False
    current = None
    with path.open("r", encoding="utf-8", errors="replace") as stream:
        for raw in stream:
            line = raw.rstrip()
            if line.startswith("=== ") and line.endswith(" ==="):
                current = line[4:-4].strip()
            elif line.startswith("  -> ") and current:
                source = line[4:].strip()
                if source and source not in mapping[current]:
                    mapping[current].append(source)
    return mapping, True

def project_of(path):
    prefixes = (
        ("workspace/llm_map", "llm_map"),
        ("cli-synthegration", "synthegration"),
        ("harmony_hub", "harmony_hub"),
        ("archwiz", "archwiz"),
        ("deepcli", "deepcli"),
        ("deepseek-cli", "deepseek_cli"),
        ("termux-multi-agent", "termux_multi_agent"),
        ("synthegration-cli", "synthegration_cli"),
        ("synthegration_exports", "exports"),
        ("storage/downloads/synthegration", "downloads_exports"),
        ("storage/downloads/_doing", "downloads_doing"),
        ("commingle-swarm", "commingle"),
        ("_1-Projects", "legacy_projects"),
    )
    for prefix, name in prefixes:
        if path.startswith(prefix):
            return name
    return "other"

def display_source(source, home_root):
    path = Path(source)
    if not path.is_absolute():
        return path.as_posix()
    try:
        return "~/" + path.resolve().relative_to(home_root.resolve()).as_posix()
    except (OSError, ValueError):
        return "external/" + path.name

def format_size(size):
    if isinstance(size, bool) or not isinstance(size, int):
        return str(size)
    if size > 1024 * 1024:
        return f"{size / 1024 / 1024:.1f} MB"
    if size > 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size} B"

def directory_size(path):
    total = 0
    for root, dirs, files in os.walk(path, followlinks=False):
        dirs[:] = [name for name in dirs if not (Path(root) / name).is_symlink()]
        for name in files:
            candidate = Path(root) / name
            try:
                if candidate.is_file() and not candidate.is_symlink():
                    total += candidate.stat().st_size
            except OSError:
                continue
    return total

def build_manifest(records, flow_map, meta):
    indexed = len(records)
    mapped_paths = {path for path in records if flow_map.get(path)}
    mapped = len(mapped_paths)
    unmapped = indexed - mapped
    if meta["source_sha"] == "unknown" or meta["tree_sha"] == "unknown":
        coverage = "UNVERIFIED"
    elif not meta["flow_present"] or meta["invalid_rows"] or unmapped:
        coverage = "PARTIAL"
    else:
        coverage = "COMPLETE"

    lines = [
        "# ArchWiz Data-Flow Manifest", "",
        f"**Generated at (UTC):** {meta['generated_at']}",
        f"**Source ref:** {meta['source_ref']}",
        f"**Source SHA:** {meta['source_sha']}",
        f"**Tree SHA:** {meta['tree_sha']}",
        f"**Generator version:** {VERSION}",
        f"**Input manifest SHA-256:** {meta['index_sha256']}",
        f"**Flow map SHA-256:** {meta['flow_sha256']}",
        f"**Coverage status:** {coverage}",
        f"**Indexed files:** {indexed}",
        f"**Mapped files:** {mapped}",
        f"**Unmapped files:** {unmapped}",
        f"**Invalid index rows:** {meta['invalid_rows']}", "",
        "> A candidate mention records a lexical path reference. It does not prove that the source writes or owns the data file.", "",
    ]
    groups, basenames = defaultdict(list), defaultdict(list)
    for path in records:
        groups[project_of(path)].append(path)
        basenames[Path(path).name].append(path)
    tick = chr(96)
    for project in sorted(groups):
        lines.extend([
            f"## {project}", "",
            "| File | Size | Candidate mentions | Duplicates / Notes |",
            "|---|---:|---|---|",
        ])
        for path in sorted(groups[project]):
            mentions = flow_map.get(path, [])
            if mentions:
                rendered = "; ".join(sorted({display_source(src, meta["home_root"]) for src in mentions}))[:200]
                mention_text = "candidate mention: " + rendered
            else:
                mention_text = "*unknown*"
            duplicates = [other for other in basenames[Path(path).name] if other != path]
            duplicate_note = f"Duplicate(s): {', '.join(duplicates[:3])}"[:150] if duplicates else ""
            lines.append(
                f"| {tick}{path}{tick} | {format_size(records[path].get('size', '?'))} | {mention_text} | {duplicate_note} |"
            )
        lines.append("")
    lines.extend(["## Large Directories (not fully indexed)", ""])
    for relative, note in EXTRA_DIRS:
        path = meta["home_root"] / relative
        if path.is_dir():
            lines.append(f"- {tick}{relative}{tick} — {format_size(directory_size(path))} — {note}")
        else:
            lines.append(f"- {tick}{relative}{tick} — (not present) — {note}")
    return "\n".join(lines) + "\n"

def write_atomic(output, content):
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=output.parent, delete=False) as stream:
            temporary = stream.name
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, output)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)

def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX, help="Central JSONL index")
    parser.add_argument("--flow-map", type=Path, default=DEFAULT_FLOW_MAP, help="Candidate mention map")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Manifest output path")
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT, help="Git checkout root")
    parser.add_argument("--home-root", type=Path, default=HOME, help="Root for local source paths")
    return parser.parse_args(argv)

def main(argv=None):
    args = parse_args(argv)
    index_path = args.index.expanduser()
    if not index_path.is_file():
        print(f"Central index unavailable: {index_path}", file=sys.stderr)
        return 2
    flow_path, output = args.flow_map.expanduser(), args.output.expanduser()
    try:
        records, invalid_rows = load_index(index_path)
    except OSError as exc:
        print(f"Unable to read central index: {exc}", file=sys.stderr)
        return 2
    flow_map, flow_present = load_flow_map(flow_path)
    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "source_ref": git_value(args.repo_root, "--abbrev-ref", "HEAD"),
        "source_sha": git_value(args.repo_root, "HEAD"),
        "tree_sha": git_value(args.repo_root, "HEAD^{tree}"),
        "index_sha256": file_sha256(index_path),
        "flow_sha256": file_sha256(flow_path) if flow_present else "missing",
        "flow_present": flow_present,
        "invalid_rows": invalid_rows,
        "home_root": args.home_root.expanduser(),
    }
    try:
        write_atomic(output, build_manifest(records, flow_map, meta))
    except OSError as exc:
        print(f"Unable to publish manifest: {exc}", file=sys.stderr)
        return 1
    unmapped = len(records) - sum(bool(flow_map.get(path)) for path in records)
    print(f"Manifest written to {output} ({len(records)} indexed, {unmapped} unmapped; {meta['source_sha']})")
    return 0

if __name__ == "__main__":
    sys.exit(main())
