#!/usr/bin/env python3
import os
import json
import fnmatch
import sys

EXCLUDE_FILE = os.path.expanduser("~/.monorepo/exclude_patterns.txt")
WHITELIST_FILE = os.path.expanduser("~/.monorepo/whitelist.txt")
OUTPUT_FILE = os.path.expanduser("~/.monorepo/projects.json")

def load_patterns(filepath):
    patterns = []
    if os.path.exists(filepath):
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    return patterns

def is_excluded(path, patterns):
    # Check exact path match and any parent component
    parts = path.split(os.sep)
    for pat in patterns:
        if fnmatch.fnmatch(path, pat) or fnmatch.fnmatch(os.path.basename(path), pat):
            return True
        for p in parts:
            if fnmatch.fnmatch(p, pat):
                return True
    return False

def discover():
    exclude = load_patterns(EXCLUDE_FILE)
    whitelist = load_patterns(WHITELIST_FILE)
    projects = []
    root = os.path.expanduser("~")

    for dirpath, dirnames, filenames in os.walk(root):
        # 1. Always skip node_modules (regardless of exclude list)
        if 'node_modules' in dirpath.split(os.sep):
            dirnames[:] = []
            continue

        # 2. Skip if excluded
        if is_excluded(dirpath, exclude):
            dirnames[:] = []
            continue

        # 3. Skip hidden directories (optional)
        # if os.path.basename(dirpath).startswith('.'):
        #     dirnames[:] = []
        #     continue

        # Check for manifests
        manifests = []
        if "package.json" in filenames:
            manifests.append(("npm", os.path.join(dirpath, "package.json")))
        if "Cargo.toml" in filenames:
            manifests.append(("cargo", os.path.join(dirpath, "Cargo.toml")))
        if "go.mod" in filenames:
            manifests.append(("go", os.path.join(dirpath, "go.mod")))
        if "setup.py" in filenames or "pyproject.toml" in filenames:
            manifests.append(("python", dirpath))
        if "Gemfile" in filenames:
            manifests.append(("ruby", os.path.join(dirpath, "Gemfile")))

        if manifests:
            # If whitelist is empty, include everything; else check
            if not whitelist or any(w in dirpath for w in whitelist):
                for lang, manifest in manifests:
                    projects.append({
                        "path": dirpath,
                        "language": lang,
                        "manifest": manifest,
                        "name": os.path.basename(dirpath)
                    })

    with open(OUTPUT_FILE, "w") as f:
        json.dump(projects, f, indent=2)
    print(f"Discovered {len(projects)} projects -> {OUTPUT_FILE}")

if __name__ == "__main__":
    discover()
