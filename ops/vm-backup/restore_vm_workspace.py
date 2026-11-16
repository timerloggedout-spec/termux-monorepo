#!/usr/bin/env python3
"""Restore drill for muse-vm-workspace-backup exports. Stdlib only.

Given a local copy of the backup repo (clone or extracted tarball) and
a target root:

  1. Restores every exported (T0, phase 1) file to its source-relative
     location under the target.
  2. Verifies each restored file's sha256 against MANIFEST.json.
  3. Asserts NO excluded path exists in the restored tree (keys/ dirs,
     *.pem, *.key, *.env, tokens.env, client_secret*, scratch/).
  4. T1 consistency check: every manifest-only T1 entry's source file
     is re-hashed at --source-home and compared with the hash recorded
     at export time (phase 1 carries no T1 content, so consistency is
     asserted against the live source).

Emits DRILL.json {verdict, checked, mismatched, excluded_absent,
t1_checked, t1_consistent, t1_missing}.
"""
import argparse, fnmatch, hashlib, json, shutil, sys
from pathlib import Path

DENY_DIR_NAMES = {"keys"}
DENY_FILE_GLOBS = ["*.pem", "*.key", "*.env", "tokens.env",
                   "client_secret*", "*.pyc"]


def _sha256(p: Path):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while True:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _denied(rel: Path) -> bool:
    if any(part in DENY_DIR_NAMES for part in rel.parts):
        return True
    if rel.parts and rel.parts[0] == "scratch":
        return True
    low = rel.name.lower()
    return any(fnmatch.fnmatch(low, g.lower()) for g in DENY_FILE_GLOBS)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--backup", required=True,
                    help="local copy of the backup repo")
    ap.add_argument("--target", required=True, help="restore target root")
    ap.add_argument("--source-home", default=str(Path.home()),
                    help="home the export was taken from (T1 check)")
    ap.add_argument("--report", default=None,
                    help="DRILL.json path (default <target>/DRILL.json)")
    args = ap.parse_args(argv)
    backup = Path(args.backup)
    target = Path(args.target)
    source_home = Path(args.source_home)
    manifest = json.loads((backup / "MANIFEST.json").read_text())
    entries = manifest["files"]

    checked = mismatched = 0
    for e in entries:
        if not e.get("exported"):
            continue
        dst = target / e["source"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        if e.get("split"):
            # Reassemble byte-bounded parts in order; the sidecar is
            # metadata only and is never restored as a file.
            with open(dst, "wb") as fout:
                for pr in e["split"]["parts"]:
                    with open(backup / pr, "rb") as fin:
                        shutil.copyfileobj(fin, fout)
        else:
            shutil.copyfile(backup / e["path"], dst)
        checked += 1
        if _sha256(dst) != e["sha256"]:
            mismatched += 1

    excluded_absent = True
    for p in target.rglob("*"):
        rel = p.relative_to(target)
        if _denied(rel):
            excluded_absent = False
            break

    t1_checked = t1_consistent = t1_missing = 0
    for e in entries:
        if e.get("reason") != "phase1-manifest-only":
            continue
        t1_checked += 1
        src = source_home / e["source"]
        if not src.is_file():
            t1_missing += 1
        elif _sha256(src) == e["sha256"]:
            t1_consistent += 1

    verdict = "pass" if (mismatched == 0 and excluded_absent
                         and t1_missing == 0
                         and t1_consistent == t1_checked) else "fail"
    drill = {"verdict": verdict, "checked": checked,
             "mismatched": mismatched,
             "excluded_absent": excluded_absent,
             "t1_checked": t1_checked, "t1_consistent": t1_consistent,
             "t1_missing": t1_missing,
             "export_id": manifest.get("export_id")}
    report = Path(args.report) if args.report else target / "DRILL.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(drill, indent=1))
    print(json.dumps(drill, indent=1))
    return 0 if verdict == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
