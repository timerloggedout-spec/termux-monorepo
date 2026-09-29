#!/usr/bin/env python3
"""Push ~/.deepcli/logs/* to termux-monorepo/.deepseek-logs/<date>/ via Git tree API."""
import base64, json, os, subprocess, sys, time
from pathlib import Path

REPO   = os.environ.get("LOGS_REPO", "timerloggedout-spec/termux-monorepo")
BRANCH = os.environ.get("LOGS_BRANCH", "logs/history")
PREFIX = ".deepseek-logs"
LOGDIR = Path.home() / ".deepcli" / "logs"
MAX_FILE = 4 * 1024 * 1024      # 4 MB per file cap
MAX_TOTAL = 40 * 1024 * 1024    # 40 MB total per sync


def gh(args, input_data=None):
    cmd = ["gh", "api"] + args
    if input_data is not None:
        cmd += ["--input", "-"]
    r = subprocess.run(cmd, input=input_data, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"gh api {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def gh_json(args, input_data=None):
    return json.loads(gh(args, input_data))


def main():
    # 1. HEAD
    ref = gh_json([f"repos/{REPO}/git/refs/heads/{BRANCH}"])
    head_sha = ref["object"]["sha"]
    commit = gh_json([f"repos/{REPO}/git/commits/{head_sha}"])
    base_tree = commit["tree"]["sha"]

    # 2. gather files
    date_prefix = time.strftime("%Y-%m-%d")
    files, total = [], 0
    for f in sorted(LOGDIR.iterdir()):
        if not f.is_file():
            continue
        if f.suffix not in (".log", ".jsonl") and not f.name.startswith("agent_"):
            continue
        sz = f.stat().st_size
        if sz == 0 or sz > MAX_FILE:
            continue
        if total + sz > MAX_TOTAL:
            break
        files.append((f, sz))
        total += sz

    if not files:
        print(json.dumps({"status": "no_op", "reason": "no files"}))
        return

    # 3. blobs
    entries = []
    for f, _ in files:
        content = base64.b64encode(f.read_bytes()).decode()
        body = json.dumps({"content": content, "encoding": "base64"})
        blob = gh_json([f"repos/{REPO}/git/blobs"], body)
        entries.append({
            "path": f"{PREFIX}/{date_prefix}/{f.name}",
            "mode": "100644",
            "type": "blob",
            "sha": blob["sha"],
        })

    # 4. tree
    tree_body = json.dumps({"base_tree": base_tree, "tree": entries})
    new_tree = gh_json([f"repos/{REPO}/git/trees"], tree_body)

    # 5. commit
    commit_body = json.dumps({
        "message": f"chore(logs): sync {len(entries)} files — {date_prefix}",
        "tree": new_tree["sha"],
        "parents": [head_sha],
    })
    new_commit = gh_json([f"repos/{REPO}/git/commits"], commit_body)

    # 6. update ref
    ref_body = json.dumps({"sha": new_commit["sha"], "force": True})  # orphan logs branch, force OK
    gh([f"repos/{REPO}/git/refs/heads/{BRANCH}", "-X", "PATCH"], ref_body)

    print(json.dumps({
        "status": "synced",
        "files": len(entries),
        "bytes": total,
        "commit": new_commit["sha"][:12],
        "prefix": f"{PREFIX}/{date_prefix}",
    }))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(json.dumps({"status": "error", "error": str(e)}))
        sys.exit(1)
