#!/usr/bin/env python3
import json, subprocess, os, re
from pathlib import Path

ALL_TOOLS = "all_tools.jsonl"
REPO_ROOTS = ["/refTemplates", os.path.expanduser("~/DeepTerm"), os.path.expanduser("~/workspace")]

def load_tools():
    with open(ALL_TOOLS) as f:
        return [json.loads(line) for line in f]

def save_tools(tools):
    with open(ALL_TOOLS, "w") as f:
        for t in tools:
            f.write(json.dumps(t)+"\n")

def get_pip_desc(name):
    try:
        out = subprocess.check_output(["pip", "show", name], stderr=subprocess.DEVNULL, text=True)
        for line in out.splitlines():
            if line.startswith("Summary:"):
                return line.split(":",1)[1].strip()
    except: pass
    return None

def get_npm_desc(name):
    try:
        out = subprocess.check_output(["npm", "info", name, "description"], stderr=subprocess.DEVNULL, text=True)
        return out.strip()
    except: pass
    return None

def get_cargo_desc(name):
    try:
        out = subprocess.check_output(["cargo", "search", name, "--limit", "1"], stderr=subprocess.DEVNULL, text=True)
        if "#" in out:
            return out.split("#",1)[1].strip()
    except: pass
    return None

def get_git_desc(name):
    """Look for a directory matching name under REPO_ROOTS and extract description."""
    for root in REPO_ROOTS:
        candidate = Path(root) / name
        if candidate.is_dir():
            # Check .git/description
            desc_file = candidate / ".git" / "description"
            if desc_file.exists():
                desc = desc_file.read_text().strip()
                if desc and not desc.startswith("Unnamed repository"):
                    return f"Git: {desc}"
            # Check README.md heading
            readme = candidate / "README.md"
            if readme.exists():
                first_line = readme.read_text().split("\n")[0]
                if first_line.startswith("# "):
                    return f"Git: {first_line[2:].strip()}"
            return f"Git repository {name}"
    return None

def main():
    tools = load_tools()
    assigned = 0
    for t in tools:
        if t.get("description"):
            continue
        name = t["name"]
        # Try package managers first
        desc = get_pip_desc(name) or get_npm_desc(name) or get_cargo_desc(name)
        if desc:
            t["description"] = desc
            assigned += 1
            continue
        # Try git repos
        desc = get_git_desc(name)
        if desc:
            t["description"] = desc
            assigned += 1
    save_tools(tools)
    print(f"✅ Assigned {assigned} descriptions (pip/npm/cargo/git)")

if __name__ == "__main__":
    main()
