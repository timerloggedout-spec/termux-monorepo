#!/usr/bin/env python3
"""Commit Replay — compose() v0: materialize a NEW file from pointers.

[MUSEai]@{role:{commit-replay}} — a grecipe is an ordered segment list;
each segment is a gpointer {path, blob, start_line, end_line[, symbol]}
into existing git history, or a {"literal": "..."} glue segment (kept
explicit in the recipe, never hidden). compose resolves pointer segments
from the local checkout's object store (git cat-file), slices the line
range, concatenates, and writes the target. The recipe is the authored
artifact (tokens ~ pointer list); the file is its materialization.

Usage:
  compose.py --repo-root . --recipe recipe.json [--out PATH] [--check]
--check: materialize in memory, verify target file bytes match, print
sha256 + per-segment provenance either way.
"""
import argparse, hashlib, json, subprocess, sys


def blob_lines(root, blob):
    out = subprocess.run(["git", "-C", root, "cat-file", "blob", blob],
                         capture_output=True, check=True).stdout
    return out.decode("utf-8").splitlines(keepends=True)


def materialize(root, recipe):
    parts, prov = [], []
    for i, seg in enumerate(recipe["segments"]):
        if "literal" in seg:
            parts.append(seg["literal"])
            prov.append({"seg": i, "kind": "literal",
                         "bytes": len(seg["literal"].encode())})
        else:
            lines = blob_lines(root, seg["blob"])
            s, e = seg["start_line"], seg["end_line"]
            chunk = "".join(lines[s - 1:e])
            if not chunk.endswith("\n"):
                chunk += "\n"
            parts.append(chunk)
            prov.append({"seg": i, "kind": "pointer",
                         "path": seg.get("path"),
                         "blob": seg["blob"][:12],
                         "symbol": seg.get("symbol"),
                         "range": [s, e],
                         "bytes": len(chunk.encode())})
    return "".join(parts), prov


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--recipe", required=True)
    ap.add_argument("--out")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    recipe = json.load(open(a.recipe, encoding="utf-8"))
    target = a.out or recipe["path"]
    content, prov = materialize(a.repo_root, recipe)
    digest = hashlib.sha256(content.encode()).hexdigest()
    if a.check:
        try:
            existing = open(target, encoding="utf-8").read()
            ok = existing == content
        except OSError:
            ok = False
        print(json.dumps({"target": target, "sha256": digest,
                          "matches_file": ok, "segments": prov},
                         indent=1, sort_keys=True))
        return 0 if ok else 1
    with open(target, "w", encoding="utf-8") as f:
        f.write(content)
    print(json.dumps({"target": target, "sha256": digest,
                      "bytes": len(content.encode()), "segments": prov},
                     indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
