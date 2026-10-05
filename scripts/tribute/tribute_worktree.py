#!/usr/bin/env python3
"""Tribute-lane worktree manager for constrained devices.

Pre-check is metadata-only (no clone).  Clone uses
depth=1 + blob:none filter + sparse cone.
"""
from __future__ import annotations
import argparse, json, pathlib, shutil, subprocess, sys, time

HOME = pathlib.Path.home()
CACHE = HOME / ".cache" / "tribute"
LOG = HOME / ".deepcli" / "logs" / "tribute"
MAX_MB = 200
TTL_HOURS = 6
DEFAULT_SPARSE = ("README.md", "docs", "scripts", "templates")


def run(args, timeout=300):
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout or "", r.stderr or ""
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


def gh_api(path):
    rc, out, _ = run(["gh", "api", path])
    if rc != 0:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return None


def slug(s):
    return s.replace("/", "__")


def worktree(s):
    return CACHE / slug(s)


def du_mb(p):
    total = 0
    for f in p.rglob("*"):
        try:
            if f.is_file():
                total += f.stat().st_size
        except OSError:
            pass
    return total / (1024 * 1024)


def log_ev(ev):
    LOG.mkdir(parents=True, exist_ok=True)
    with (LOG / "tribute.jsonl").open("a") as f:
        f.write(json.dumps(ev) + "\n")


def cmd_check(a):
    meta = gh_api("repos/" + a.owner_repo)
    if not meta:
        print("check: fail")
        return 1
    size_mb = meta.get("size", 0) / 1024
    print("repo         " + meta["full_name"])
    print("size         " + format(size_mb, ".1f") + " MB")
    print("default      " + meta.get("default_branch", "main"))
    print("clone_url    " + meta["clone_url"])
    print("abort_at     " + str(MAX_MB) + " MB  ->  " + ("ABORT" if size_mb > MAX_MB else "PROCEED"))
    return 0 if size_mb <= MAX_MB else 2


def cmd_prepare(a):
    CACHE.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    wt = worktree(a.owner_repo)
    meta = gh_api("repos/" + a.owner_repo)
    if not meta:
        print("prepare: fail  (cannot query repo)")
        return 1
    size_mb = meta.get("size", 0) / 1024
    if size_mb > MAX_MB:
        print("prepare: abort  " + format(size_mb, ".1f") + " MB exceeds " + str(MAX_MB) + " MB cap")
        log_ev({"op": "prepare", "repo": a.owner_repo, "result": "abort-size", "size_mb": size_mb})
        return 2
    url = meta["clone_url"]
    branch = meta.get("default_branch", "main")
    sparse = a.paths if a.paths else list(DEFAULT_SPARSE)
    if wt.exists() and (wt / ".git").exists():
        print("prepare: reuse  existing partial clone")
        run(["git", "-C", str(wt), "pull", "--depth=1", "--ff-only"])
        run(["git", "-C", str(wt), "sparse-checkout", "set", "--cone", *sparse])
        log_ev({"op": "prepare", "repo": a.owner_repo, "result": "reuse"})
        print("worktree  " + str(wt))
        return 0
    if wt.exists():
        shutil.rmtree(wt, ignore_errors=True)
    t0 = time.time()
    rc, _, err = run(["git", "clone", "--depth=1", "--filter=blob:none",
                      "--sparse", "--branch", branch, url, str(wt)], timeout=600)
    dur = time.time() - t0
    if rc != 0:
        print("prepare: clone fail rc=" + str(rc))
        print(err.strip()[:400])
        log_ev({"op": "prepare", "repo": a.owner_repo, "result": "fail-clone", "seconds": round(dur, 1)})
        return 3
    run(["git", "-C", str(wt), "sparse-checkout", "set", "--cone", *sparse])
    used = du_mb(wt)
    print("prepare: ok  " + format(dur, ".1f") + "s  disk " + format(used, ".1f") + " MB")
    print("sparse  " + str(sparse))
    print("worktree  " + str(wt))
    log_ev({"op": "prepare", "repo": a.owner_repo, "result": "fresh",
            "seconds": round(dur, 1), "disk_mb": round(used, 1), "sparse": sparse})
    return 0


def cmd_size(a):
    wt = worktree(a.owner_repo)
    if not wt.exists():
        print("size: absent")
        return 1
    print("worktree  " + str(wt))
    print("disk      " + format(du_mb(wt), ".1f") + " MB")
    return 0


def cmd_sweep(a):
    if not CACHE.exists():
        print("sweep: no cache")
        return 0
    cutoff = time.time() - a.ttl_hours * 3600
    removed = 0
    for wt in CACHE.iterdir():
        if wt.is_dir() and wt.stat().st_mtime < cutoff:
            shutil.rmtree(wt, ignore_errors=True)
            removed += 1
            print("removed  " + wt.name)
    print("sweep: " + str(removed) + " removed  ttl=" + str(a.ttl_hours) + "h")
    return 0


def cmd_list(a):
    if not CACHE.exists():
        print("(no worktrees)")
        return 0
    now = time.time()
    print("repo".ljust(40) + " " + "age_h".rjust(7) + " " + "MB".rjust(8))
    for wt in sorted(CACHE.iterdir()):
        if wt.is_dir():
            age = (now - wt.stat().st_mtime) / 3600
            print(wt.name.ljust(40) + " " + format(age, ".1f").rjust(7) + " " + format(du_mb(wt), ".1f").rjust(8))
    return 0


def main():
    p = argparse.ArgumentParser(prog="tribute_worktree.py")
    s = p.add_subparsers(dest="cmd", required=True)
    c = s.add_parser("check"); c.add_argument("owner_repo"); c.set_defaults(fn=cmd_check)
    c = s.add_parser("prepare"); c.add_argument("owner_repo"); c.add_argument("paths", nargs="*"); c.set_defaults(fn=cmd_prepare)
    c = s.add_parser("size"); c.add_argument("owner_repo"); c.set_defaults(fn=cmd_size)
    c = s.add_parser("sweep"); c.add_argument("--ttl-hours", type=float, default=TTL_HOURS); c.set_defaults(fn=cmd_sweep)
    c = s.add_parser("list"); c.set_defaults(fn=cmd_list)
    a = p.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())
