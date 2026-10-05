#!/usr/bin/env python3
"""Metadata-only repository recon.  Runs before any clone.

Reports size, default branch, activity, license, languages, and a
PROCEED/ABORT verdict against a size cap.  Zero bytes cloned.
"""
from __future__ import annotations
import argparse, json, subprocess, sys

CAP_MB = 200


def gh(path):
    try:
        r = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=20)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("owner_repo")
    ap.add_argument("--cap-mb", type=float, default=CAP_MB)
    a = ap.parse_args()

    meta = gh("repos/" + a.owner_repo)
    if not meta:
        print("recon: fail  cannot query " + a.owner_repo)
        return 1

    size_mb = meta.get("size", 0) / 1024
    langs = gh("repos/" + a.owner_repo + "/languages") or {}

    print("repo         " + meta["full_name"])
    print("size         " + format(size_mb, ".1f") + " MB")
    print("default      " + meta.get("default_branch", "main"))
    print("clone_url    " + meta["clone_url"])
    print("ssh_url      " + meta.get("ssh_url", "-"))
    print("license      " + (meta.get("license") or {}).get("spdx_id", "none"))
    print("private      " + str(meta.get("private")))
    print("archived     " + str(meta.get("archived")))
    print("pushed_at    " + meta.get("pushed_at", "-"))
    print("stars        " + str(meta.get("stargazers_count", 0)))
    print("forks        " + str(meta.get("forks_count", 0)))
    print("open_issues  " + str(meta.get("open_issues_count", 0)))
    if langs:
        top = sorted(langs.items(), key=lambda kv: kv[1], reverse=True)[:5]
        print("languages    " + ", ".join(k for k, _ in top))

    verdict = "ABORT" if size_mb > a.cap_mb else "PROCEED"
    print("cap          " + format(a.cap_mb, ".1f") + " MB")
    print("verdict      " + verdict)
    return 0 if verdict == "PROCEED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
