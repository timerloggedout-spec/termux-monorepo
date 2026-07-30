#!/usr/bin/env python3
import json, subprocess, os, sys, time
from pathlib import Path

ALL_TOOLS = "all_tools.jsonl"
# Git repos to scan for descriptions
GIT_ROOTS = [
    os.path.expanduser("~/workspace"),
    os.path.expanduser("~/refTemplates"),
    # Add top-level dirs under HOME that contain .git (limit to avoid slowness)
]

def load_tools():
    with open(ALL_TOOLS) as f:
        return [json.loads(line) for line in f]

def save_tools(tools):
    with open(ALL_TOOLS, "w") as f:
        for t in tools:
            f.write(json.dumps(t)+"\n")

def run_cmd(cmd, timeout=10):
    """Run command, return stdout, or '' on failure."""
    try:
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True, timeout=timeout)
    except:
        return ""

def fetch_pip_descriptions():
    print("  Fetching pip package list...", end="", flush=True)
    desc = {}
    list_out = run_cmd(["pip", "list", "--format", "json"])
    if not list_out:
        print(" failed")
        return desc
    pkgs = json.loads(list_out)
    print(f" {len(pkgs)} packages")
    for i, p in enumerate(pkgs):
        name = p["name"]
        print(f"\r  pip show [{i+1}/{len(pkgs)}]: {name[:40]:<40}", end="", flush=True)
        info = run_cmd(["pip", "show", name])
        if not info:
            continue
        for line in info.splitlines():
            if line.startswith("Summary:"):
                desc[name] = line.split(":",1)[1].strip()
                break
    print("\n  pip done.")
    return desc

def fetch_npm_descriptions():
    print("  Fetching npm global packages...", end="", flush=True)
    desc = {}
    out = run_cmd(["npm", "ls", "-g", "--depth=0", "--json"])
    if not out:
        print(" none")
        return desc
    data = json.loads(out)
    deps = data.get("dependencies", {})
    for name, info in deps.items():
        desc[name] = info.get("description", "")
    print(f" {len(desc)} packages")
    return desc

def fetch_cargo_descriptions():
    print("  Fetching cargo crates...", end="", flush=True)
    desc = {}
    out = run_cmd(["cargo", "install", "--list"])
    if not out:
        print(" none")
        return desc
    lines = out.splitlines()
    for line in lines:
        if line and not line.startswith(" "):
            name = line.split()[0]
            sr = run_cmd(["cargo", "search", name, "--limit", "1"])
            if sr and "#" in sr:
                desc[name] = sr.split("#",1)[1].strip()
    print(f" {len(desc)} crates")
    return desc

def fetch_git_descriptions():
    desc = {}
    for root in GIT_ROOTS:
        if not os.path.isdir(root):
            continue
        print(f"  Scanning git repos in {root}...")
        for entry in os.listdir(root):
            path = Path(root) / entry
            if not path.is_dir():
                continue
            gitdir = path / ".git"
            if not gitdir.is_dir():
                continue
            # .git/description
            desc_file = gitdir / "description"
            if desc_file.exists():
                text = desc_file.read_text().strip()
                if text and not text.startswith("Unnamed repository"):
                    desc[entry] = f"Git: {text}"
                    continue
            # README.md first heading
            readme = path / "README.md"
            if readme.exists():
                first = readme.read_text().split("\n")[0].strip()
                if first.startswith("# "):
                    desc[entry] = f"Git: {first[2:].strip()}"
                    continue
            desc[entry] = f"Git repo {entry}"
        print(f"    found {len(desc)} repos")
    return desc

def main():
    tools = load_tools()
    print("Fetching descriptions...")
    pip_desc = fetch_pip_descriptions()
    npm_desc = fetch_npm_descriptions()
    cargo_desc = fetch_cargo_descriptions()
    git_desc = fetch_git_descriptions()

    assigned = 0
    total_null = sum(1 for t in tools if not t.get("description"))
    print(f"Null descriptions to fill: {total_null}")
    for i, t in enumerate(tools):
        if t.get("description"):
            continue
        if (i+1) % 200 == 0:
            print(f"  Processed {i+1}/{len(tools)} tools...", flush=True)
        name = t["name"]
        if name in pip_desc:
            t["description"] = pip_desc[name]
            assigned += 1
        elif name in npm_desc:
            t["description"] = npm_desc[name]
            assigned += 1
        elif name in cargo_desc:
            t["description"] = cargo_desc[name]
            assigned += 1
        elif name in git_desc:
            t["description"] = git_desc[name]
            assigned += 1

    save_tools(tools)
    total_with = sum(1 for t in tools if t.get("description"))
    print(f"✅ Assigned {assigned} descriptions. Total with: {total_with}/{len(tools)}")

if __name__ == "__main__":
    main()
