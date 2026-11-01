#!/usr/bin/env python3
"""Commit Replay — extract() v1 (commit-store/v1, compact delta format).

[MUSEai]@{role:{commit-replay}} — git-plane indexer. Walks a local git
checkout (in CI: the workflow's own checkout) and emits/updates the gindex
JSONL: header{checkpoints} + commit records (forward) + entry records.

COMPACT (v1, owner: Compactify + LLMToken-down): entries are DELTAS vs the
first parent only — {commit,path,op:A|M|D,blob,mode} — never a full tree
per commit (v0 emitted 10.36M entries / 2.2GB for 1,000 commits and the
push was rejected over GitHub's 100MB file limit, run 41283146476).
State at any commit = root full-set + deltas applied along ancestry;
path_history IS the entry stream; reverse 1:N derives at query time (P2)
by resolving state. Pointers/oids/metadata ONLY — no blob bytes.

Incremental: prior index records are carried forward; only commits absent
from the prior index are walked, newest-first, capped by --max-commits
per run (older history backfills on later runs). Output is deterministic
(sorted records, sorted keys) and written atomically.

Usage:
  extract.py --repo-root . --repo-name owner/name \
             --index ops/commit-replay/index/owner--name.jsonl \
             [--max-commits 1000]
"""
import argparse, json, os, subprocess, sys, tempfile
from datetime import datetime, timezone

SPEC = "commit-store/v1"


def git(root, *args):
    out = subprocess.run(["git", "-C", root, *args],
                         capture_output=True, text=True, check=True)
    return out.stdout


def iso(ts, tz):
    try:
        dt = datetime.fromtimestamp(int(ts), timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return None


def load_prior(path):
    commits, entries, header = {}, {}, None
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                if r.get("kind") == "header":
                    header = r
                elif r.get("kind") == "commit":
                    commits[r["oid"]] = r
                elif r.get("kind") == "entry":
                    entries[(r["commit"], r["path"])] = r
    return commits, entries, header


def parse_commit(root, oid):
    raw = git(root, "cat-file", "commit", oid)
    tree, parents, author, ts = None, [], None, None
    for line in raw.splitlines():
        if line.startswith("tree "):
            tree = line[5:].strip()
        elif line.startswith("parent "):
            parents.append(line[7:].strip())
        elif line.startswith("author "):
            # author Name <email> ts tz
            body = line[7:]
            lt, gt = body.rfind("<"), body.rfind(">")
            author = body[:lt].strip() if 0 <= lt < gt else body
            parts = body[gt + 1:].split() if gt >= 0 else []
            ts = iso(parts[0], parts[1] if len(parts) > 1 else "+0000") \
                if parts else None
        elif line == "":
            break
    return {"kind": "commit", "oid": oid, "tree": tree,
            "parents": parents, "author": author, "ts": ts, "refs": []}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--repo-name", required=True)
    ap.add_argument("--index", required=True)
    ap.add_argument("--max-commits", type=int, default=1000)
    a = ap.parse_args()
    root = a.repo_root

    # Ref census: every branch + tag, local + remote-tracking (a CI
    # checkout carries remote branches under refs/remotes only — v0 saw
    # just master+tag). History mass lives in backup refs.
    refs = {}
    for line in git(root, "for-each-ref",
                    "--format=%(refname) %(objectname)",
                    "refs/heads", "refs/tags", "refs/remotes").splitlines():
        if line.strip():
            name, tip = line.rsplit(" ", 1)
            refs[name] = tip
    tip_refs = {}
    for name, tip in refs.items():
        tip_refs.setdefault(tip, []).append(name)

    commits, entries, _prior = load_prior(a.index)
    known = set(commits)

    # Candidate commits across all refs, newest-first (commit-date order).
    cand = []
    raw = git(root, "rev-list", "--all", "--date-order")
    for oid in raw.split():
        if oid not in known:
            cand.append(oid)
        if len(cand) >= a.max_commits:
            break
    truncated = len(cand) >= a.max_commits

    new = 0
    for oid in cand:
        rec = parse_commit(root, oid)
        rec["refs"] = sorted(tip_refs.get(oid, []))
        commits[oid] = rec
        if rec["parents"]:
            # Delta vs first parent: name-status + raw modes/oids.
            raw = git(root, "diff-tree", "-r", "--no-commit-id",
                      "-z", "--raw", rec["parents"][0], oid)
            toks = [t for t in raw.split("\0") if t]
            i = 0
            while i < len(toks):
                meta = toks[i]; i += 1
                parts = meta[1:].split()  # strip leading ':'
                omode, nmode, oblob, nblob, status = parts[:5]
                path = toks[i]; i += 1
                if status.startswith(("R", "C")):
                    i += 1  # skip source path; record target as A
                    status = "A"
                op = {"A": "A", "M": "M", "D": "D", "T": "M"}.get(status, "M")
                entries[(oid, path)] = {
                    "kind": "entry", "commit": oid, "path": path, "op": op,
                    "blob": None if op == "D" else nblob,
                    "mode": None if op == "D" else nmode}
        else:
            # Root commit: full set, all A.
            for line in git(root, "ls-tree", "-r", "-z", oid).split("\0"):
                if not line:
                    continue
                meta, path = line.split("\t", 1)
                mode, typ, blob = meta.split(" ")
                entries[(oid, path)] = {"kind": "entry", "commit": oid,
                                        "path": path, "op": "A",
                                        "blob": blob, "mode": mode}
        new += 1

    header = {"kind": "header", "spec": SPEC, "repo": a.repo_name,
              "generated_at": datetime.now(timezone.utc)
              .strftime("%Y-%m-%dT%H:%M:%SZ"),
              "checkpoints": dict(sorted(refs.items())),
              "commits_indexed": len(commits),
              "entries_indexed": len(entries),
              "last_run_new": new, "last_run_truncated": truncated}

    records = [header]
    records += [commits[k] for k in sorted(commits)]
    records += [entries[k] for k in sorted(entries)]
    os.makedirs(os.path.dirname(os.path.abspath(a.index)), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(
        os.path.abspath(a.index)), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")
    os.replace(tmp, a.index)
    print(json.dumps({"repo": a.repo_name, "refs": len(refs), "new": new,
                      "commits": len(commits), "entries": len(entries),
                      "truncated": truncated}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
