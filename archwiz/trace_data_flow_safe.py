#!/usr/bin/env python3
"""Scan source files for data-path mentions; matches are candidates, not writer proof."""
import argparse
from collections import defaultdict
import os
from pathlib import Path
import sys
import tempfile

HOME = Path.home()
DEFAULT_SOURCE_DIRS = [
    HOME / "workspace", HOME / "cli-synthegration", HOME / "harmony_hub",
    HOME / "archwiz", HOME / "deepcli", HOME / "deepseek-cli",
    HOME / "termux-multi-agent", HOME / "synthegration-cli",
    HOME / "commingle-swarm", HOME / "_1-Projects",
]
EXCLUDE = {
    ".git", "node_modules", "__pycache__", ".hermes", "browser-data",
    "Cache", "GPUCache", "chunks", ".cache", "storage",
    "synthegration_exports", "sandbox",
}
EXTENSIONS = {".py", ".sh", ".js", ".ts", ".rs", ".toml", ".yaml", ".yml", ".json", ".md", ".txt"}

def scan_sources(data_paths, source_dirs, max_file_bytes):
    flow, source_files = defaultdict(list), []
    for source_dir in source_dirs:
        if not source_dir.is_dir():
            continue
        for root, dirs, files in os.walk(source_dir, followlinks=False):
            root_path = Path(root)
            dirs[:] = [
                name for name in dirs
                if name not in EXCLUDE and not name.startswith(".")
                and not (root_path / name).is_symlink()
            ]
            for filename in files:
                candidate = root_path / filename
                if candidate.is_symlink() or candidate.suffix.lower() not in EXTENSIONS:
                    continue
                try:
                    if candidate.stat().st_size > max_file_bytes:
                        continue
                except OSError:
                    continue
                source_files.append(candidate)
    for source in source_files:
        try:
            content = source.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for data_path in data_paths:
            if data_path in content:
                flow[data_path].append(str(source))
    return {path: sorted(set(sources)) for path, sources in flow.items()}, len(source_files)

def write_map(output, flow):
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=output.parent, delete=False) as stream:
            temporary = stream.name
            for path in sorted(flow):
                stream.write(f"\n=== {path} ===\n")
                for source in flow[path]:
                    stream.write(f"  -> {source}\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, output)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)

def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-files", type=Path, default=HOME / "tmp" / "data_files_list.txt")
    parser.add_argument("--source-dir", type=Path, action="append", dest="source_dirs")
    parser.add_argument("--output", type=Path, default=HOME / "tmp" / "data_flow_map.txt")
    parser.add_argument("--max-file-bytes", type=int, default=500_000)
    return parser.parse_args(argv)

def main(argv=None):
    args = parse_args(argv)
    data_file = args.data_files.expanduser()
    if not data_file.is_file():
        print(f"Data-file list unavailable: {data_file}", file=sys.stderr)
        return 2
    if args.max_file_bytes < 1:
        print("--max-file-bytes must be positive", file=sys.stderr)
        return 2
    try:
        with data_file.open("r", encoding="utf-8") as stream:
            data_paths = [line.strip() for line in stream if line.strip()]
    except OSError as exc:
        print(f"Unable to read data-file list: {exc}", file=sys.stderr)
        return 2
    source_dirs = [path.expanduser() for path in args.source_dirs] if args.source_dirs else DEFAULT_SOURCE_DIRS
    flow, source_count = scan_sources(data_paths, source_dirs, args.max_file_bytes)
    try:
        output = args.output.expanduser()
        write_map(output, flow)
    except OSError as exc:
        print(f"Unable to write flow map: {exc}", file=sys.stderr)
        return 1
    print(f"Scanned {source_count} source files; found {len(flow)} candidate data-path mentions. Output: {output}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
