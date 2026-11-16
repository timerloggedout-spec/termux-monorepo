#!/usr/bin/env python3
"""Commit Replay — P2 fragment index (commit-store/v1).

[MUSEai]@{role:{commit-replay}} — the pointer unit is the FRAGMENT
(function|class|method|snippet), not the file (owner scope, 2026-11-01).
Reads the gindex header for the master checkpoint, resolves that commit's
tree in the local checkout (git is the byte source; the index points),
parses each Python blob with ast, and emits fragments JSONL:
  header {spec: fragment-index/v1, repo, commit, files, fragments}
  {path, blob, symbol, kind, start_line, end_line}
These records are what gpointer{v1} addresses (symbol + range).
v0 scope: .py only, master tip state only, caps --max-files/--max-blob.
"""
import argparse, ast, json, os, subprocess, sys, tempfile
from datetime import datetime, timezone


def git(root, *args, binary=False):
    out = subprocess.run(["git", "-C", root, *args],
                         capture_output=True, check=True)
    return out.stdout if binary else out.stdout.decode(
        "utf-8", "replace")


def fragments_of(src):
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    out = []

    def walk(body, prefix=""):
        for n in body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                kind = "method" if prefix else "function"
                out.append({"symbol": prefix + n.name, "kind": kind,
                            "start_line": n.lineno,
                            "end_line": n.end_lineno})
            elif isinstance(n, ast.ClassDef):
                out.append({"symbol": prefix + n.name, "kind": "class",
                            "start_line": n.lineno,
                            "end_line": n.end_lineno})
                walk(n.body, prefix + n.name + ".")
    walk(tree.body)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--repo-name", required=True)
    ap.add_argument("--index", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ref", default="refs/heads/master")
    ap.add_argument("--max-files", type=int, default=3000)
    ap.add_argument("--max-blob", type=int, default=200000)
    a = ap.parse_args()

    tip = None
    with open(a.index, encoding="utf-8") as f:
        hdr = json.loads(f.readline())
    tip = hdr["checkpoints"][a.ref]
    records, files, frags, skipped = [], 0, 0, 0
    for line in git(a.repo_root, "ls-tree", "-r", "-z", tip).split("\0"):
        if not line:
            continue
        meta, path = line.split("\t", 1)
        mode, typ, blob = meta.split(" ")
        if typ != "blob" or not path.endswith(".py"):
            continue
        if files >= a.max_files:
            skipped += 1
            continue
        raw = git(a.repo_root, "cat-file", "blob", blob, binary=True)
        if len(raw) > a.max_blob:
            skipped += 1
            continue
        files += 1
        for fr in fragments_of(raw.decode("utf-8", "replace")):
            records.append({"path": path, "blob": blob, **fr})
            frags += 1
    header = {"kind": "header", "spec": "fragment-index/v1",
              "repo": a.repo_name, "commit": tip,
              "generated_at": datetime.now(timezone.utc)
              .strftime("%Y-%m-%dT%H:%M:%SZ"),
              "files": files, "fragments": frags, "skipped": skipped}
    records.sort(key=lambda r: (r["path"], r["start_line"], r["symbol"]))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(
        os.path.abspath(a.out)), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps(header, sort_keys=True) + "\n")
        for r in records:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    os.replace(tmp, a.out)
    print(json.dumps({"commit": tip[:12], "files": files,
                      "fragments": frags, "skipped": skipped},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
