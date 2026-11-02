#!/usr/bin/env python3
"""Tiered export of the Muse VM home/workspace state to the private
`muse-vm-backup` GitHub repo. Stdlib only.

Tiers (see README.md):
  T0  full content: root standing files, ~/memory, and the named
      ~/workspace subtrees (goals, custom-connectors, custom-skills,
      user) plus ~/hooks.
  T1  unique state only: every other top-level ~/workspace entry —
      git clones contribute dirty-tracked + untracked files only;
      plain dirs contribute their files minus regenerable subtrees.
      PHASE 1 (design of record, scoping PR #3522): T1 is
      MANIFEST-ONLY — entries record path + sha256 + size + tier with
      exported=false, reason=phase1-manifest-only; no T1 content is
      staged or published in this build.

Hard rules:
  - Denylisted names (keys/ dirs, *.pem, *.key, *.env, tokens.env,
    client_secret*, *.pyc) are NEVER staged; they are recorded in the
    manifest as excluded entries so the inventory stays honest.
  - Files over 25 MB are manifest-only (tier "<t>-manifest").
  - Three scrub gates run on the staged tree before anything is
    published; any hit aborts with a non-zero exit and nothing pushed.
  - Publishing uses the GitHub Git Data API with the fleet PAT
    helper's surrogate credential mechanism (dynamic_credentials);
    the credential value never appears in argv, env, logs, or files.
    (git-over-https transport cannot use the surrogate: the
    remote-https child cannot complete auth in this sandbox, so the
    API batch-commit path is the publish transport.)
"""
import argparse, base64, fnmatch, hashlib, json, os, re, subprocess, sys, time
import urllib.request, urllib.error
from pathlib import Path

SIZE_GATE = 25 * 1024 * 1024
T0_ROOT_FILES = ["CLAUDE.md", "MEMORY.md", "USER.md", "IDENTITY.md",
                 "SOUL.md", "PROACTIVE_PREFERENCES.md", "AGENTS.md", "TOOLS.md"]
T0_TREES = ["memory", "workspace/goals", "workspace/custom-connectors",
            "workspace/custom-skills", "hooks", "workspace/user"]
T0_WS_DIRS = {"goals", "custom-connectors", "custom-skills", "user"}
SKIP_WS_DIRS = {"scratch", "vm-backup"}
# Objectively regenerable installs/mirrors (same class as node_modules):
# the Go toolchain distribution and the public termux-monorepo mirror.
REGENERABLE_EXACT_WS = {"termux-monorepo", "go"}
REGENERABLE_DIRS = {"node_modules", ".venv", "venv", ".venvs",
                    "__pycache__", ".cache", "dist", "build", "target",
                    ".next", ".git"}
DENY_DIR_NAMES = {"keys"}
DENY_FILE_GLOBS = ["*.pem", "*.key", "*.env", "tokens.env",
                   "client_secret*", "*.pyc"]
SECRET_PATTERNS = [
    # Actual PEM header forms only. The looser fragment
    # "PRIVATE KEY-----" false-positives on the fleet's own
    # sensitivity-policy docs, which quote the pattern spec with an
    # ellipsis ("-----BEGIN … PRIVATE KEY-----"); every real key
    # header (plain/RSA/EC/OPENSSH/ENCRYPTED/PGP) still matches this.
    rb"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----",
    rb"ghp_[A-Za-z0-9]{20,}",
    rb"github_pat_[A-Za-z0-9_]{20,}",
    rb"AKIA[0-9A-Z]{16}",
    rb"sk-[A-Za-z0-9]{20,}",
    rb"Bearer [A-Za-z0-9._-]{24,}",
]

# ---------------------------------------------------------------- inventory

def denied_name(name: str) -> bool:
    low = name.lower()
    return any(fnmatch.fnmatch(low, g.lower()) for g in DENY_FILE_GLOBS)

def _walk_files(root: Path):
    """Yield file Paths under root, pruning regenerable/.git dirs and
    denylisted dirs. Does not follow symlinks."""
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = sorted(d for d in dirnames
                             if d not in REGENERABLE_DIRS
                             and d not in DENY_DIR_NAMES)
        for fn in sorted(filenames):
            yield Path(dirpath) / fn

def _classify(abspath: Path, source: str, tier: str, entries: list):
    """Append a manifest entry for one candidate file (or an excluded /
    manifest-only record). Returns nothing; staging happens later."""
    name = abspath.name
    parts = Path(source).parts
    if any(p in DENY_DIR_NAMES for p in parts):
        entries.append(dict(source=source, tier=tier, exported=False,
                            reason="excluded:keys-dir", sha256=None,
                            size=None))
        return
    if denied_name(name):
        entries.append(dict(source=source, tier=tier, exported=False,
                            reason="excluded:denylist-name", sha256=None,
                            size=None))
        return
    if abspath.is_symlink():
        entries.append(dict(source=source, tier=tier, exported=False,
                            reason="excluded:symlink", sha256=None,
                            size=None))
        return
    if not abspath.is_file():
        # Sockets, fifos, devices: no content to back up, and opening
        # them can block or fail (ENXIO on sockets).
        entries.append(dict(source=source, tier=tier, exported=False,
                            reason="excluded:non-regular", sha256=None,
                            size=None))
        return
    size = abspath.stat().st_size
    if size > SIZE_GATE:
        entries.append(dict(source=source, tier=tier + "-manifest",
                            exported=False, reason="size", sha256=None,
                            size=size))
        return
    if tier == "t1":
        # Phase 1: manifest-only. Hash the source, stage nothing.
        entries.append(dict(source=source, tier=tier, exported=False,
                            reason="phase1-manifest-only", sha256=None,
                            size=size, _abs=str(abspath), _hash=True))
        return
    entries.append(dict(source=source, tier=tier, exported=True,
                        reason=None, sha256=None, size=size,
                        _abs=str(abspath)))

def iter_t0_sources(home: Path):
    """(abspath, home-relative source) pairs for the T0 set, with the
    always-exclusions already applied by _classify downstream. Used by
    state_hash.py (stat-only) as well."""
    out = []
    for rel in T0_ROOT_FILES:
        p = home / rel
        if p.is_file():
            out.append((p, rel))
    for tree in T0_TREES:
        root = home / tree
        if root.is_dir():
            for f in _walk_files(root):
                out.append((f, str(Path(tree) / f.relative_to(root))))
    return out

def _git_dirty_files(repo: Path):
    """Dirty-tracked + untracked files of a clone, repo-relative."""
    r = subprocess.run(["git", "-C", str(repo), "status",
                        "--porcelain=v1", "-z", "--untracked-files=all"],
                       capture_output=True, timeout=120)
    if r.returncode != 0:
        return []
    toks = r.stdout.decode("utf-8", "surrogateescape").split("\0")
    paths = []
    i = 0
    while i < len(toks):
        tok = toks[i]
        i += 1
        if len(tok) < 4 or tok[2] != " ":
            continue
        status, path = tok[:2], tok[3:]
        if "R" in status or "C" in status:
            i += 1  # rename/copy: next token is the source path; skip it
        p = repo / path
        if p.is_file():
            paths.append(path)
    return paths

def build_inventory(home: Path):
    entries = []
    for abspath, source in iter_t0_sources(home):
        _classify(abspath, source, "t0", entries)
    ws = home / "workspace"
    if ws.is_dir():
        for child in sorted(ws.iterdir(), key=lambda p: p.name):
            name = child.name
            if child.is_file() and not child.is_dir():
                _classify(child, f"workspace/{name}", "t1", entries)
                continue
            if not child.is_dir():
                continue
            if name in SKIP_WS_DIRS:
                entries.append(dict(source=f"workspace/{name}", tier="t1",
                                    exported=False,
                                    reason=f"excluded:{name}",
                                    sha256=None, size=None))
                continue
            if name in T0_WS_DIRS:
                continue
            if name in REGENERABLE_EXACT_WS:
                entries.append(dict(source=f"workspace/{name}", tier="t1",
                                    exported=False,
                                    reason="excluded:regenerable-mirror",
                                    sha256=None, size=None))
                continue
            if (child / ".git").exists():
                for rel in _git_dirty_files(child):
                    _classify(child / rel, f"workspace/{name}/{rel}",
                              "t1", entries)
                continue
            # Plain dir: walk; nested clones switch to clone semantics.
            for dirpath, dirnames, filenames in os.walk(child,
                                                        followlinks=False):
                dp = Path(dirpath)
                keep = []
                for d in sorted(dirnames):
                    sub = dp / d
                    if d in REGENERABLE_DIRS or d in DENY_DIR_NAMES:
                        continue
                    if (sub / ".git").exists():
                        for rel in _git_dirty_files(sub):
                            src = str((sub / rel).relative_to(home))
                            _classify(sub / rel, src, "t1", entries)
                        continue
                    keep.append(d)
                dirnames[:] = keep
                for fn in sorted(filenames):
                    f = dp / fn
                    _classify(f, str(f.relative_to(home)), "t1", entries)
    return entries

# ---------------------------------------------------------------- staging

def stage(entries, staging: Path):
    if staging.exists():
        subprocess.run(["rm", "-rf", str(staging)], check=True)
    staging.mkdir(parents=True)
    total_bytes = 0
    for e in entries:
        if e.get("_hash"):
            # Manifest-only entry: hash the source, stage nothing.
            src = Path(e.pop("_abs"))
            h = hashlib.sha256()
            with open(src, "rb") as fin:
                while True:
                    chunk = fin.read(1 << 20)
                    if not chunk:
                        break
                    h.update(chunk)
            e["sha256"] = h.hexdigest()
            e["path"] = "t1/" + e["source"]
            e.pop("_hash", None)
            continue
        if not e["exported"]:
            continue
        src = Path(e.pop("_abs"))
        rel = ("t0" if e["tier"] == "t0" else "t1") + "/" + e["source"]
        dst = staging / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        h = hashlib.sha256()
        with open(src, "rb") as fin, open(dst, "wb") as fout:
            while True:
                chunk = fin.read(1 << 20)
                if not chunk:
                    break
                h.update(chunk)
                fout.write(chunk)
        e["path"] = rel
        e["sha256"] = h.hexdigest()
        total_bytes += e["size"]
    for e in entries:
        e.pop("_abs", None)
        if e["exported"]:
            e.setdefault("path", None)
    return total_bytes

# ---------------------------------------------------------------- gates

def run_gates(entries, staging: Path):
    gates = {}
    expected = sorted(e["path"] for e in entries if e["exported"])
    actual = sorted(str(p.relative_to(staging))
                    for p in staging.rglob("*")
                    if p.is_file()
                    and p.name not in ("MANIFEST.json", "EXPORT.json"))
    gates["inventory_match"] = (expected == actual)
    if not gates["inventory_match"]:
        gates["inventory_diff"] = {
            "missing": sorted(set(expected) - set(actual))[:20],
            "extra": sorted(set(actual) - set(expected))[:20]}
    deny_hits = []
    for rel in actual:
        parts = Path(rel).parts
        if any(p in DENY_DIR_NAMES for p in parts) or denied_name(parts[-1]):
            deny_hits.append(rel)
    gates["denylist_clean"] = not deny_hits
    if deny_hits:
        gates["denylist_hits"] = deny_hits[:20]
    pats = [re.compile(p) for p in SECRET_PATTERNS]
    scrub_hits = []
    for rel in actual:
        data = (staging / rel).read_bytes()
        if any(p.search(data) for p in pats):
            scrub_hits.append(rel)  # paths only; matched content never logged
    gates["content_scrub"] = "fail" if scrub_hits else "pass"
    if scrub_hits:
        gates["content_scrub_hit_paths"] = scrub_hits[:20]
    gates["pass"] = bool(gates["inventory_match"]
                         and gates["denylist_clean"]
                         and gates["content_scrub"] == "pass")
    return gates

# ---------------------------------------------------------------- publish

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request  # noqa: E402

API = "https://api.github.com"

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a):
        raise RuntimeError("redirect refused")

def gh(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if data:
        req.add_header("Content-Type", "application/json")
    add_surrogate_to_request(req, "custom.github-pat",
                             allowed_hosts=["api.github.com"])
    try:
        with urllib.request.build_opener(_NoRedirect()).open(req,
                                                             timeout=120) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            return e.code, {}

def _git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0"
                        + data).hexdigest()

def publish(staging: Path, repo: str, message: str):
    """Batch-commit the staging tree via the Git Data API. Returns the
    commit SHA. Unchanged blobs (same git blob SHA already in the repo)
    are not re-uploaded."""
    files = sorted(str(p.relative_to(staging))
                   for p in staging.rglob("*") if p.is_file())
    st, ref = gh("GET", f"/repos/{repo}/git/ref/heads/main")
    parent = ref.get("object", {}).get("sha") if st == 200 else None
    existing_blobs = set()
    if parent:
        st, commit = gh("GET", f"/repos/{repo}/git/commits/{parent}")
        tree_sha = commit.get("tree", {}).get("sha")
        if tree_sha:
            st, tree = gh("GET",
                          f"/repos/{repo}/git/trees/{tree_sha}?recursive=1")
            for t in tree.get("tree", []):
                if t.get("type") == "blob":
                    existing_blobs.add(t["sha"])
    blob_sha = {}
    for rel in files:
        data = (staging / rel).read_bytes()
        sha = _git_blob_sha(data)
        if sha not in existing_blobs:
            st, blob = gh("POST", f"/repos/{repo}/git/blobs",
                          {"content": base64.b64encode(data).decode(),
                           "encoding": "base64"})
            if st not in (200, 201):
                raise RuntimeError(f"blob create failed for {rel}: {st}")
            sha = blob["sha"]
        blob_sha[rel] = sha
    # Hierarchical tree build, deepest first.
    dirs = set()
    for rel in files:
        parts = rel.split("/")[:-1]
        for i in range(1, len(parts) + 1):
            dirs.add("/".join(parts[:i]))
    tree_sha_by_dir = {}
    for d in sorted(dirs, key=lambda x: -x.count("/")):
        entries = []
        for rel in files:
            if os.path.dirname(rel) == d:
                entries.append({"path": os.path.basename(rel),
                                "mode": "100644", "type": "blob",
                                "sha": blob_sha[rel]})
        for sub in dirs:
            if os.path.dirname(sub) == d:
                entries.append({"path": os.path.basename(sub),
                                "mode": "040000", "type": "tree",
                                "sha": tree_sha_by_dir[sub]})
        st, t = gh("POST", f"/repos/{repo}/git/trees", {"tree": entries})
        if st not in (200, 201):
            raise RuntimeError(f"tree create failed for {d}: {st}")
        tree_sha_by_dir[d] = t["sha"]
    root_entries = []
    for rel in files:
        if "/" not in rel:
            root_entries.append({"path": rel, "mode": "100644",
                                 "type": "blob", "sha": blob_sha[rel]})
    for d in dirs:
        if "/" not in d:
            root_entries.append({"path": d, "mode": "040000",
                                 "type": "tree", "sha": tree_sha_by_dir[d]})
    st, root_tree = gh("POST", f"/repos/{repo}/git/trees",
                       {"tree": root_entries})
    if st not in (200, 201):
        raise RuntimeError(f"root tree create failed: {st}")
    body = {"message": message, "tree": root_tree["sha"]}
    if parent:
        body["parents"] = [parent]
    st, commit = gh("POST", f"/repos/{repo}/git/commits", body)
    if st not in (200, 201):
        raise RuntimeError(f"commit create failed: {st}")
    sha = commit["sha"]
    if parent:
        st, _ = gh("PATCH", f"/repos/{repo}/git/refs/heads/main",
                   {"sha": sha})
    else:
        st, _ = gh("POST", f"/repos/{repo}/git/refs",
                   {"ref": "refs/heads/main", "sha": sha})
    if st not in (200, 201):
        raise RuntimeError(f"ref update failed: {st}")
    return sha

def append_file_commit(repo: str, path: str, data: bytes, message: str):
    """Second-commit helper: add/replace one file on top of main
    (used for drill reports under reports/). Returns commit SHA."""
    st, ref = gh("GET", f"/repos/{repo}/git/ref/heads/main")
    parent = ref["object"]["sha"]
    st, commit = gh("GET", f"/repos/{repo}/git/commits/{parent}")
    base_tree = commit["tree"]["sha"]
    st, blob = gh("POST", f"/repos/{repo}/git/blobs",
                  {"content": base64.b64encode(data).decode(),
                   "encoding": "base64"})
    blob_sha = blob["sha"]
    st, tree = gh("POST", f"/repos/{repo}/git/trees",
                  {"base_tree": base_tree,
                   "tree": [{"path": path, "mode": "100644",
                             "type": "blob", "sha": blob_sha}]})
    st, commit = gh("POST", f"/repos/{repo}/git/commits",
                    {"message": message, "tree": tree["sha"],
                     "parents": [parent]})
    sha = commit["sha"]
    gh("PATCH", f"/repos/{repo}/git/refs/heads/main", {"sha": sha})
    return sha

# ---------------------------------------------------------------- state

def t0_state_lines(home: Path):
    lines = []
    for abspath, source in iter_t0_sources(home):
        if any(p in DENY_DIR_NAMES for p in Path(source).parts):
            continue
        if denied_name(abspath.name) or abspath.is_symlink():
            continue
        try:
            st = abspath.stat()
        except OSError:
            continue
        lines.append(f"{source}\t{st.st_size}\t{st.st_mtime_ns}")
    return sorted(lines)

def t0_state_hash(home: Path) -> str:
    payload = "\n".join(t0_state_lines(home)) + "\n"
    return hashlib.sha256(payload.encode()).hexdigest()

# ---------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--home", default=str(Path.home()))
    ap.add_argument("--staging",
                    default=None,
                    help="default <home>/workspace/scratch/vm-backup-export")
    ap.add_argument("--repo",
                    default="timerloggedout-spec/muse-vm-workspace-backup")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--marker", default=None,
                    help="default <home>/workspace/vm-backup/.last-export-state")
    args = ap.parse_args(argv)
    home = Path(args.home)
    staging = Path(args.staging) if args.staging else \
        home / "workspace/scratch/vm-backup-export"
    marker = Path(args.marker) if args.marker else \
        home / "workspace/vm-backup/.last-export-state"

    export_id = "exp-" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) \
        + "-" + hashlib.sha256(os.urandom(16)).hexdigest()[:6]
    entries = build_inventory(home)
    total_bytes = stage(entries, staging)
    manifest = {"export_id": export_id,
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                              time.gmtime()),
                "files": sorted(entries,
                                key=lambda e: (e["tier"], e["source"]))}
    (staging / "MANIFEST.json").write_text(json.dumps(manifest, indent=1))
    gates = run_gates(entries, staging)
    counts = {
        "t0": sum(1 for e in entries if e["exported"] and e["tier"] == "t0"),
        "t1": sum(1 for e in entries
                  if e["reason"] == "phase1-manifest-only"),
        "manifest_only": sum(1 for e in entries
                             if e["reason"] == "size"),
        "excluded": sum(1 for e in entries
                        if (e["reason"] or "").startswith("excluded")),
        "bytes": total_bytes,
    }
    export_doc = {"export_id": export_id,
                  "exported_at": manifest["generated_at"],
                  "home": str(home), "counts": counts, "gates": gates,
                  "publish": None}
    (staging / "EXPORT.json").write_text(json.dumps(export_doc, indent=1))
    if not gates["pass"]:
        print(json.dumps({"export_id": export_id, "gates": gates,
                          "verdict": "ABORT-scrub-gate"}, indent=1))
        return 2
    result = {"export_id": export_id, "counts": counts,
              "gates": "pass", "commit": None}
    if args.publish:
        msg = (f"export {export_id} t0={counts['t0']} "
               f"t1={counts['t1']} gates=pass")
        sha = publish(staging, args.repo, msg)
        result["commit"] = sha
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(t0_state_hash(home) + "\n")
        export_doc["publish"] = {"repo": args.repo, "commit": sha}
        (staging / "EXPORT.json").write_text(json.dumps(export_doc,
                                                        indent=1))
    print(json.dumps(result, indent=1))
    return 0

if __name__ == "__main__":
    sys.exit(main())
