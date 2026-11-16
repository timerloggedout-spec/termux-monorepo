#!/usr/bin/env python3
"""Publish a local tree into termux-monorepo via git-data API (blobs),
reusing the PAT helper's call() in-process (no argv size cap, no token
ever materialises — surrogate exchange inside the helper)."""
import base64, importlib.util, json, sys
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "gh", str(Path.home() / "workspace/custom-connectors/custom.github-pat/bin/github_pat.py"))
gh = importlib.util.module_from_spec(spec); spec.loader.exec_module(gh)
REPO = "timerloggedout-spec/termux-monorepo"
ROOT = Path(sys.argv[1]); BRANCH = sys.argv[2]; TITLE = sys.argv[3]; BODY = sys.argv[4]

master = gh.call("GET", f"/repos/{REPO}/git/ref/heads/master")["object"]["sha"]
base_tree = gh.call("GET", f"/repos/{REPO}/git/commits/{master}")["tree"]["sha"]
print("master", master[:10], "base_tree", base_tree[:10])
entries = []
for p in sorted(ROOT.rglob("*")):
    if p.is_file():
        rel = p.relative_to(ROOT).as_posix()
        blob = gh.call("POST", f"/repos/{REPO}/git/blobs",
                       {"content": base64.b64encode(p.read_bytes()).decode(),
                        "encoding": "base64"})
        entries.append({"path": rel, "mode": "100644", "type": "blob",
                        "sha": blob["sha"]})
        print(" blob", rel, p.stat().st_size, blob["sha"][:10])
tree = gh.call("POST", f"/repos/{REPO}/git/trees",
               {"base_tree": base_tree, "tree": entries})
commit = gh.call("POST", f"/repos/{REPO}/git/commits",
                 {"message": TITLE, "tree": tree["sha"], "parents": [master]})
gh.call("POST", f"/repos/{REPO}/git/refs",
        {"ref": f"refs/heads/{BRANCH}", "sha": commit["sha"]})
pr = gh.call("POST", f"/repos/{REPO}/pulls",
             {"title": TITLE, "head": BRANCH, "base": "master", "body": BODY})
print("PR:", pr.get("html_url"), "commit", commit["sha"][:10])
