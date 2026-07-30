#!/usr/bin/env python3
"""
build_correlation.py – Build a time-correlation index between source files
and cache/export/search artifacts.

Saves correlation_index.json into the workspace.
"""
import os
import json
import sys
from pathlib import Path
from collections import defaultdict

# ---------- CONFIG ----------
WORKSPACE = Path.home() / "caveman_time_correlation"
BASE_DIRS = [
    "deepcli", "deepcli-tui", "deepseek-cli", "cli-synthegration",
    "termux-multi-agent", "synthegration-cli", "harmonizer-prod_cli",
    "chronos_checkout", "synthegration_exports"
]
CACHE_GLOB_PATTERNS = [
    "**/.cache/**",
    "**/__pycache__/**",
    "**/codex/blobs/**",
    "**/dist/**",
    "**/build/**",
    "**/node_modules/**",   # though generally excluded, include if present
    "**/.git/**",
]
EXPORT_DIRS = ["synthegration_exports"]
SEARCH_CACHE_GLOB = "**/.conv_search_cache/**"   # hypothetical, adjust if needed
TIME_WINDOW = 5  # seconds – files modified within ± this window are correlated
# ------------------------------

# Ensure workspace exists
WORKSPACE.mkdir(parents=True, exist_ok=True)

# Collect source files (everything non-bloat)
source_files = []
for base in BASE_DIRS:
    base_path = Path(base)
    if not base_path.is_dir():
        continue
    for f in base_path.rglob("*"):
        if f.is_file() and not any(pat in f.parts for pat in [
            "node_modules", "__pycache__", ".cache", ".git", "dist",
            "codex/blobs", "browser-data", ".blob"
        ]):
            source_files.append(f)

# Collect cache/export/search files
artifact_files = []
for pat in CACHE_GLOB_PATTERNS:
    for d in BASE_DIRS:
        p = Path(d)
        if p.is_dir():
            for f in p.glob(pat):
                if f.is_file():
                    artifact_files.append(f)
for d in EXPORT_DIRS:
    p = Path(d)
    if p.is_dir():
        for f in p.rglob("*"):
            if f.is_file():
                artifact_files.append(f)
# add any search cache if present
for base in BASE_DIRS:
    for f in Path(base).glob(SEARCH_CACHE_GLOB):
        if f.is_file():
            artifact_files.append(f)

# Build source mtime lookup
source_mtimes = {}
for f in source_files:
    try:
        mtime = os.path.getmtime(f)
    except OSError:
        continue
    source_mtimes[str(f)] = mtime

# Build artifact mtime lookup
artifact_mtimes = {}
for f in artifact_files:
    try:
        mtime = os.path.getmtime(f)
    except OSError:
        continue
    artifact_mtimes[str(f)] = mtime

# Correlate: for each source file, find artifacts within TIME_WINDOW seconds
correlations = defaultdict(list)
for spath, smtime in source_mtimes.items():
    close_artifacts = []
    for apath, amtime in artifact_mtimes.items():
        if abs(smtime - amtime) <= TIME_WINDOW:
            close_artifacts.append(apath)
    if close_artifacts:
        correlations[spath] = close_artifacts

# Prepare index
index = {
    "meta": {
        "time_window_seconds": TIME_WINDOW,
        "total_source_files_scanned": len(source_mtimes),
        "total_artifact_files_scanned": len(artifact_mtimes),
        "source_files_with_correlations": len(correlations)
    },
    "correlations": dict(correlations)
}

# Write index file
output_path = WORKSPACE / "correlation_index.json"
with open(output_path, "w") as f:
    json.dump(index, f, indent=2)

print(f"Correlation index written to {output_path}")
print(f"Sources with correlating artifacts: {len(correlations)}/{len(source_mtimes)}")
