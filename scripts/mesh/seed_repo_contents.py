#!/usr/bin/env python3
"""DO seed a clf-lab repo with the common harness ∧ one family's design via the contents API (create-only).

Usage: seed_repo_contents.py OWNER/REPO FAMILY [TEMPLATE_ROOT]
Auth: `gh api` with GH_TOKEN. Files that already exist stay untouched (additive). README.md renders from
README.md.tmpl; `__FAMILY__` in iterate.yml renders to the family. Prints a names-only summary.
"""
import base64
import json
import subprocess
import sys
from pathlib import Path


def gh(*args, data=None):
    p = subprocess.run(["gh", "api", *args], input=data, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def main():
    repo, family = sys.argv[1], sys.argv[2]
    root = Path(sys.argv[3] if len(sys.argv) > 3 else "templates/clf-lab")
    fam_dir = root / "families" / family
    manifest = json.loads((fam_dir / "data" / "manifest.json").read_text(encoding="utf-8"))
    files = {}
    for base in (root / "common", fam_dir):
        for p in sorted(base.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts:
                files[p.relative_to(base).as_posix()] = p.read_text(encoding="utf-8")
    tmpl = files.pop("README.md.tmpl")
    files["README.md"] = (tmpl.replace("__FAMILY__", family).replace("__TASK__", manifest["task"])
                          .replace("__LABEL_NOTE__", manifest["label_note"]))
    files[".github/workflows/iterate.yml"] = files[".github/workflows/iterate.yml"].replace("__FAMILY__", family)
    files["results/.keep"] = ""
    # workflow last ⇒ the first scheduled/dispatched run sees the full tree
    order = sorted(files, key=lambda k: (k.startswith(".github/"), k))
    created, kept, failed = [], [], []
    for path in order:
        rc, out, err = gh(f"repos/{repo}/contents/{path}")
        if rc == 0:
            kept.append(path)
            continue
        payload = {"message": f"feat(lab): add {path} seed [skip render]",
                   "content": base64.b64encode(files[path].encode()).decode()}
        rc, out, err = gh("-X", "PUT", f"repos/{repo}/contents/{path}", "--input", "-", data=json.dumps(payload))
        if rc == 0:
            created.append(path)
        else:
            failed.append(path)
            print(f"::error title=seed::{path} refused: {(out + err).strip()[:200]}")
    print(f"::notice title=seed::{repo} created={len(created)} kept={len(kept)} failed={len(failed)}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
