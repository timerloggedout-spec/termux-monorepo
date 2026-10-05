#!/usr/bin/env python3
"""Local repository hygiene for termux-monorepo.

Read-only by default.  --apply runs aggressive gc and repack.
Identifies bloat paths, counts refs, measures .git size.
"""
from __future__ import annotations
import argparse, os, pathlib, shutil, subprocess, sys

HOME = pathlib.Path.home()
REPO = HOME
BLOAT_HINTS = (
    ".cpan", ".deepcli/session_store", "node_modules",
    ".deepseek-logs", "workspace/llm_map/context_relationships/temporal",
    ".cache", "target", "dist", "build",
)


def sh(args, timeout=120):
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout or "", r.stderr or ""
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


def du_mb(p):
    total = 0
    for f in p.rglob("*"):
        try:
            if f.is_file():
                total += f.stat().st_size
        except OSError:
            pass
    return total / (1024 * 1024)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="run git gc --aggressive --prune=now and repack")
    a = ap.parse_args()

    git_dir = REPO / ".git"
    if not git_dir.exists():
        print("hygiene: no .git at " + str(REPO))
        return 1

    print("repo          " + str(REPO))
    print(".git size     " + format(du_mb(git_dir), ".1f") + " MB")

    rc, out, _ = sh(["git", "-C", str(REPO), "rev-list", "--all", "--count"])
    print("objects       " + (out.strip() or "?") + " commits reachable")

    rc, out, _ = sh(["git", "-C", str(REPO), "for-each-ref", "--format=%(refname)"])
    refs = [l for l in out.splitlines() if l.strip()]
    print("refs          " + str(len(refs)))

    rc, out, _ = sh(["git", "-C", str(REPO), "count-objects", "-v"])
    for line in out.splitlines():
        if line.startswith(("count:", "size:", "in-pack:", "packs:", "size-pack:")):
            print("  " + line)

    print("\nbloat candidates (top 12 by MB):")
    rows = []
    for hint in BLOAT_HINTS:
        p = REPO / hint
        if p.exists():
            rows.append((hint, du_mb(p)))
    rows.sort(key=lambda kv: kv[1], reverse=True)
    for name, mb in rows[:12]:
        print("  " + format(mb, "8.1f") + " MB  " + name)

    rc, out, _ = sh(["git", "-C", str(REPO), "status", "--porcelain"])
    dirty = len(out.splitlines()) if out else 0
    print("\ndirty files   " + str(dirty))

    total_mb = du_mb(REPO)
    print("worktree MB   " + format(total_mb, ".1f"))

    if a.apply:
        print("\n--apply: running aggressive gc")
        sh(["git", "-C", str(REPO), "gc", "--aggressive", "--prune=now"], timeout=900)
        sh(["git", "-C", str(REPO), "repack", "-adf"], timeout=900)
        sh(["git", "-C", str(REPO), "prune-packed"], timeout=300)
        print(".git after    " + format(du_mb(git_dir), ".1f") + " MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
