#!/usr/bin/env python3
"""
Multi‑source description backfill.
Priority: apt (already done) → pip → npm → cargo → git repo (future) → --help (future) → manual (never auto).
"""
import json, subprocess, sys, os, re
from pathlib import Path

ALL_TOOLS = "all_tools.jsonl"

def load_tools():
    with open(ALL_TOOLS) as f:
        return [json.loads(line) for line in f]

def save_tools(tools):
    with open(ALL_TOOLS, "w") as f:
        for t in tools:
            f.write(json.dumps(t) + "\n")

def get_pip_description(pkg_name):
    """Return description from pip show, or None."""
    try:
        out = subprocess.check_output(["pip", "show", pkg_name], stderr=subprocess.DEVNULL, text=True)
        for line in out.splitlines():
            if line.startswith("Summary:"):
                return line.split(":",1)[1].strip()
        # Fallback: use line starting with "Description:"
        for line in out.splitlines():
            if line.startswith("Description:"):
                return line.split(":",1)[1].strip()
    except Exception:
        pass
    return None

def get_npm_description(pkg_name):
    """Return description from npm info, or None."""
    try:
        out = subprocess.check_output(["npm", "info", pkg_name, "description"], stderr=subprocess.DEVNULL, text=True)
        return out.strip()
    except Exception:
        pass
    return None

def get_cargo_description(crate_name):
    """Return description from cargo metadata, or None."""
    try:
        out = subprocess.check_output(["cargo", "search", crate_name, "--limit", "1"], stderr=subprocess.DEVNULL, text=True)
        # cargo search output: "crate_name = \"version\"  # description"
        parts = out.split("#", 1)
        if len(parts) > 1:
            return parts[1].strip()
    except Exception:
        pass
    return None

def main():
    tools = load_tools()
    assigned = 0
    # Map from package name to description for each source
    pip_cache = {}
    npm_cache = {}
    cargo_cache = {}

    for t in tools:
        if t.get("description") and t["description"] != "null":
            continue  # already has description
        source = t.get("source")
        pkg = t.get("package", "")
        name = t.get("name")

        # Determine the package name to query
        if source == "apt":
            # Already handled by Phase A; skip
            continue
        elif source == "pip" or (source == "custom" and name in pip_cache):
            # Custom tools may be from pip; try the tool name as package name
            query = pkg if pkg and pkg != "custom" else name
            if query not in pip_cache:
                pip_cache[query] = get_pip_description(query)
            desc = pip_cache[query]
            if desc:
                t["description"] = desc
                assigned += 1
        elif source == "npm":
            query = pkg if pkg and pkg != "npm-global" else name
            if query not in npm_cache:
                npm_cache[query] = get_npm_description(query)
            desc = npm_cache[query]
            if desc:
                t["description"] = desc
                assigned += 1
        elif source == "cargo":
            query = pkg if pkg and pkg != "cargo" else name
            if query not in cargo_cache:
                cargo_cache[query] = get_cargo_description(query)
            desc = cargo_cache[query]
            if desc:
                t["description"] = desc
                assigned += 1
        # Future: source == "custom" from git repos -> will be handled by repo research script

    save_tools(tools)
    print(f"✅ Phase B: Assigned {assigned} descriptions (pip/npm/cargo)")

if __name__ == "__main__":
    main()
