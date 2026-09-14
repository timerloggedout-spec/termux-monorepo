#!/usr/bin/env python3
"""
ML Ingestion Crawler for termux-monorepo.
Crawls Git history, branches, and session metadata to build a dataset for the specialized ML pipeline.
"""
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "data" / "ml_ingestion"
METADATA_DIR = REPO_ROOT / "docs" / "evaluations" / "manus" / "session_metadata"

def run_git(args, cwd=REPO_ROOT):
    return subprocess.check_output(["git"] + args, cwd=cwd, text=True).strip()

def ingest_git_history():
    print("Ingesting Git history...")
    history = []
    log_raw = run_git(["log", "--all", "--pretty=format:%H|%an|%ad|%s", "--date=iso"])
    for line in log_raw.splitlines():
        if not line: continue
        parts = line.split("|", 3)
        if len(parts) == 4:
            history.append({
                "hash": parts[0],
                "author": parts[1],
                "date": parts[2],
                "subject": parts[3]
            })
    return history

def ingest_branches():
    print("Ingesting branches...")
    branches = []
    branch_raw = run_git(["branch", "-a", "--format=%(refname:short)|%(objectname)|%(authordate:iso)"])
    for line in branch_raw.splitlines():
        parts = line.split("|")
        if len(parts) == 3:
            branches.append({
                "name": parts[0],
                "head": parts[1],
                "last_modified": parts[2]
            })
    return branches

def ingest_session_metadata():
    print("Ingesting session metadata...")
    metadata = {}
    if METADATA_DIR.exists():
        for f in METADATA_DIR.glob("*"):
            if f.is_file():
                try:
                    if f.suffix == ".json":
                        with open(f, "r") as jf:
                            metadata[f.name] = json.load(jf)
                    else:
                        metadata[f.name] = f.read_text()
                except Exception as e:
                    print(f"Error reading {f.name}: {e}")
    return metadata

def main():
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    payload = {
        "timestamp": timestamp,
        "repo": "termux-monorepo",
        "git_history": ingest_git_history(),
        "branches": ingest_branches(),
        "session_metadata": ingest_session_metadata()
    }

    output_file = OUTPUT_DIR / f"ingestion_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"Ingestion complete. Dataset saved to: {output_file}")
    
    # Update a symlink for the latest ingestion
    latest_link = OUTPUT_DIR / "latest.json"
    if latest_link.exists():
        latest_link.unlink()
    latest_link.symlink_to(output_file.name)

if __name__ == "__main__":
    main()
