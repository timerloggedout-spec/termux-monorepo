#!/usr/bin/env python3
"""dangle_check.py — repo-side adaptive variant of archwiz/dangle_detector.py.

Original (archwiz/dangle_detector.py @2ca24a24): device-home universe only
(run_history/master_tasks/llm_map files under $HOME), SyntaxError at L64/65
(does not compile), interactive input() auto-prune that MUTATES
task_files_index.json. This variant keeps the concept — dangling-reference
detection — and rebuilds it for the repo universe:

  * input  = a checked-out git tree (CI checkout or local clone), never
             device state;
  * checks = workflow trigger surfaces, internal links/anchors, committed
             JSON feed path references, symlink resolution, and (rename
             mode) residual references to a given old-identifier set;
  * output = machine-readable JSON report + exit code;
  * strictly read-only and non-interactive: no prune, no mutation class.

Stdlib only, per the repo-gate pattern (scripts/ci/repo_gate.py): the YAML
handling is a targeted indentation extractor for the trigger-surface keys,
not a full YAML parser.

Modes:
  census (default)  all reference checks; findings compared against an
                    optional --baseline file (ratchet: gate on NEW only).
  rename            --old-ids FILE.json [{old, new?, kind?}, ...]: report
                    every residual reference to each old identifier across
                    workflow surfaces + scripts/docs/apps pointers.

Exit codes: 0 = no (new) findings, 1 = (new) findings, 2 = usage/io error.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

TEXT_EXTS = {".py", ".sh", ".md", ".yml", ".yaml", ".json", ".html", ".js",
             ".ts", ".txt", ".toml", ".cfg", ".ini"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}
# Pointer roots for rename mode: every root where a residual old identifier
# was observed in the Bundle A qualification run (2026-11-01, vs Docs sweep
# of record) — the original four plus the log/evidence/skill/test roots the
# run proved residual-bearing. The differ classifies hits; coverage first.
POINTER_ROOTS = ("scripts/", "docs/", "apps/", ".github/", ".agents/",
                 "tests/", "ops/", "archwiz/", "workspace/",
                 ".deepseek-logs/")
FEED_PREFIXES = ("apps/", "docs/", "scripts/", "ops/", ".github/",
                 "workspace/", "tests/")
MAX_FILE_BYTES = 2_000_000


def finding(kind, path, line, ref, surface=""):
    return {"kind": kind, "path": path, "line": line, "ref": ref,
            "surface": surface}


def iter_files(root, sub=""):
    base = root / sub if sub else root
    if not base.exists():
        return
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in sorted(filenames):
            yield Path(dirpath) / name


def rel(root, p):
    return str(p.relative_to(root))


def read_text(p):
    try:
        if p.stat().st_size > MAX_FILE_BYTES:
            return None
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


# ---------------------------------------------------------------- workflows
def workflow_surfaces(text):
    """Targeted extractor: yields (surface, value, lineno) for the trigger
    surfaces a rename can silently break. Indentation-tracked, stdlib only.
    Surfaces: name, repository_dispatch types, workflow_run workflows,
    paths entries, local uses, concurrency groups."""
    out = []
    lines = text.splitlines()
    # context stack: list of (indent, key) for mapping keys on the path
    stack = []
    list_ctx = None  # (key_indent, key) when inside a block sequence
    for i, raw in enumerate(lines, 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        stripped = raw.strip()
        # pop stack to current indent
        while stack and stack[-1][0] >= indent and not stripped.startswith("- "):
            stack.pop()
        if list_ctx and indent <= list_ctx[0] and not stripped.startswith("- "):
            list_ctx = None
        m = re.match(r"^-\s+(.*)$", stripped)
        if m and list_ctx:
            val = m.group(1).strip().strip("'\"")
            key, ctx = list_ctx[1], list_ctx[2]
            if key == "types":
                out.append((f"{ctx}.types" if ctx else "types", val, i))
            elif key == "workflows":
                out.append(("workflow_run.workflows", val, i))
            elif key == "paths":
                out.append(("paths", val, i))
            continue
        if m and re.match(r"^[A-Za-z_][\w-]*:", m.group(1)):
            # sequence item that opens a mapping, e.g. "- uses: ./x" or
            # "- run: ..." under steps: — re-parse as a key at deeper indent
            stripped = m.group(1)
            indent += 2
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", stripped)
        if m:
            key, val = m.group(1), m.group(2).strip()
            keys = [k for _, k in stack]
            ctx = next((k for k in reversed(keys)
                        if k in ("repository_dispatch", "workflow_run")), "")
            if key == "name" and not stack:
                out.append(("name", val.strip("'\""), i))
            if key in ("types", "workflows", "paths") and not val:
                list_ctx = (indent, key, ctx)
            elif key in ("types", "workflows") and val.startswith("["):
                for v in val.strip("[]").split(","):
                    v = v.strip().strip("'\"")
                    if v:
                        surf = (f"{ctx}.types" if key == "types"
                                else "workflow_run.workflows")
                        out.append((surf, v, i))
            if key == "uses" and val.startswith("./"):
                out.append(("uses.local", val, i))
            if key == "group" and "concurrency" in keys:
                out.append(("concurrency.group", val, i))
            if key == "run":
                for sm in re.finditer(r"(scripts/[\w./-]+)", val):
                    out.append(("run.script", sm.group(1), i))
            stack.append((indent, key))
    return out


def check_workflows(root, old_ids=None):
    findings = []
    wf_dir = root / ".github" / "workflows"
    for p in iter_files(root, ".github/workflows"):
        if p.suffix not in (".yml", ".yaml"):
            continue
        rp = rel(root, p)
        text = read_text(p)
        if text is None:
            continue
        surfaces = workflow_surfaces(text)
        for surface, val, line in surfaces:
            if surface == "uses.local":
                target = val.split("@")[0].strip()
                if target.startswith("./") and not (root / target[2:]).exists():
                    findings.append(finding("dangling-local-uses", rp, line,
                                            target, surface))
            if surface == "run.script" and not (root / val).exists():
                findings.append(finding("dangling-run-script", rp, line,
                                        val, surface))
            if surface == "paths" and old_ids is None:
                # path filters pointing at nothing are advisory in census
                pat = val.rstrip("/")
                if pat and "*" not in pat and not (root / pat).exists():
                    findings.append(finding("dangling-path-filter", rp, line,
                                            val, surface))
        if old_ids:
            for entry in old_ids:
                old = entry["old"]
                if old in p.name:
                    findings.append(finding("residual-old-id", rp, 0, old,
                                            "filename"))
                for surface, val, line in surfaces:
                    if old in val:
                        findings.append(finding("residual-old-id", rp, line,
                                                old, surface))
    return findings


# -------------------------------------------------------------------- links
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HTML_REF = re.compile(r"(?:href|src)\s*=\s*\"([^\"]+)\"")
HTML_ID = re.compile(r"id\s*=\s*\"([^\"]+)\"")


def is_dynamic_reference(value):
    """Return true when a captured attribute is assembled at runtime.

    The census validates literal repository paths only. JavaScript template
    expressions, concatenations and interpolation helpers are not paths and
    must not be resolved against the checkout.
    """
    return bool(re.search(
        r"\$\{|\$\(|(?:^|\s)\+|\+|\b(?:esc|safeHref)\s*\(",
        value,
    ))


def slugify(heading):
    s = heading.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    return re.sub(r"\s+", "-", s)


def check_links(root):
    findings = []
    ids_cache = {}

    def html_ids(p):
        if p not in ids_cache:
            text = read_text(p) or ""
            ids_cache[p] = set(HTML_ID.findall(text))
        return ids_cache[p]

    def md_slugs(p):
        if p not in ids_cache:
            text = read_text(p) or ""
            slugs = set()
            for line in text.splitlines():
                m = re.match(r"^#{1,6}\s+(.*)$", line)
                if m:
                    slugs.add(slugify(m.group(1)))
            ids_cache[p] = slugs
        return ids_cache[p]

    for p in iter_files(root):
        if p.suffix not in (".md", ".html"):
            continue
        rp = rel(root, p)
        text = read_text(p)
        if text is None:
            continue
        refs = []
        if p.suffix == ".md":
            refs = [(m.group(1), text[:m.start()].count("\n") + 1)
                    for m in MD_LINK.finditer(text)]
        else:
            refs = [(m.group(1), text[:m.start()].count("\n") + 1)
                    for m in HTML_REF.finditer(text)]
        for refv, line in refs:
            if is_dynamic_reference(refv):
                continue
            if re.match(r"^(https?:|mailto:|tel:|data:|#)", refv):
                if refv.startswith("#") and len(refv) > 1:
                    anchors = (html_ids(p) if p.suffix == ".html"
                               else md_slugs(p))
                    if refv[1:] not in anchors:
                        findings.append(finding("dangling-anchor", rp, line,
                                                refv, "link"))
                continue
            target, _, anchor = refv.partition("#")
            target = target.split("?")[0]
            if not target:
                continue
            tp = (p.parent / target).resolve()
            try:
                tp.relative_to(root.resolve())
            except ValueError:
                continue  # outside tree: not this checker's universe
            if not tp.exists():
                findings.append(finding("dangling-link", rp, line, refv,
                                        "link"))
            elif anchor:
                anchors = None
                if tp.suffix == ".html":
                    anchors = html_ids(tp)
                elif tp.suffix == ".md":
                    anchors = md_slugs(tp)
                if anchors is not None and anchor not in anchors:
                    findings.append(finding("dangling-anchor", rp, line,
                                            refv, "link"))
    return findings


# -------------------------------------------------------------------- feeds
def feed_refs(obj, out):
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            feed_refs(v, out)
    elif isinstance(obj, list):
        for v in obj:
            feed_refs(v, out)


def check_feeds(root):
    findings = []
    for p in iter_files(root):
        if p.suffix != ".json":
            continue
        rp = rel(root, p)
        if not (rp.startswith("apps/") or rp.startswith("ops/")
                or rp.startswith("docs/ops/generated/")):
            continue
        text = read_text(p)
        if text is None:
            continue
        try:
            data = json.loads(text)
        except (ValueError, UnicodeDecodeError):
            continue
        strings = []
        feed_refs(data, strings)
        seen = set()
        for s in strings:
            # Feed descriptions often combine several paths into prose
            # (for example "a.md + b.py"). Only a single literal path is
            # eligible for filesystem resolution.
            if is_dynamic_reference(s) or re.search(r"\s", s.strip()):
                continue
            cand = s.split("#")[0].split("?")[0]
            if cand in seen:
                continue
            seen.add(cand)
            if (cand.startswith(FEED_PREFIXES) and "/" in cand
                    and re.search(r"\.[\w]{1,6}$", cand)
                    and not (root / cand).exists()):
                findings.append(finding("dangling-feed-ref", rp, 0, cand,
                                        "feed"))
    return findings


# ----------------------------------------------------------------- symlinks
def check_symlinks(root):
    findings = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames + dirnames:
            p = Path(dirpath) / name
            if p.is_symlink() and not p.exists():
                findings.append(finding("dangling-symlink", rel(root, p), 0,
                                        os.readlink(p), "symlink"))
    return findings


# ------------------------------------------------------------------ rename
def check_pointers(root, old_ids, self_exclude):
    findings = []
    for sub in POINTER_ROOTS:
        for p in iter_files(root, sub.rstrip("/")):
            rp = rel(root, p)
            if rp in self_exclude or p.suffix not in TEXT_EXTS:
                continue
            text = read_text(p)
            if text is None:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                for entry in old_ids:
                    old = entry["old"]
                    if old in line:
                        findings.append(finding("residual-old-id", rp, i,
                                                old, "pointer"))
                    elif old.lower() in line.lower():
                        findings.append(finding("residual-old-id-case", rp, i,
                                                old, "pointer"))
    return findings


# --------------------------------------------------------------------- main
def key(f):
    return (f["kind"], f["path"], f["ref"], f["surface"])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="tree root (default: cwd)")
    ap.add_argument("--mode", choices=("census", "rename"), default="census")
    ap.add_argument("--old-ids", help="JSON file: [{old, new?, kind?}]")
    ap.add_argument("--baseline", help="JSON report whose findings are known")
    ap.add_argument("--scope", action="append", default=[],
                    help="restrict findings to this path prefix (repeatable)")
    ap.add_argument("--write-baseline", help="write findings as baseline JSON")
    ap.add_argument("--out", help="write JSON report here")
    ap.add_argument("--report-only", action="store_true",
                    help="exit 0 regardless of findings")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"error: root not a directory: {root}", file=sys.stderr)
        return 2

    old_ids = None
    self_exclude = set()
    if args.mode == "rename":
        if not args.old_ids:
            print("error: rename mode requires --old-ids", file=sys.stderr)
            return 2
        try:
            old_ids = json.loads(Path(args.old_ids).read_text())
        except (OSError, ValueError) as e:
            print(f"error: cannot read old-ids: {e}", file=sys.stderr)
            return 2
        self_exclude.add(rel(root, Path(args.old_ids).resolve())
                         if Path(args.old_ids).resolve().is_relative_to(root)
                         else "")

    findings = []
    findings += check_workflows(root, old_ids)
    findings += check_symlinks(root)
    if args.mode == "rename":
        findings += check_pointers(root, old_ids, self_exclude)
    else:
        findings += check_links(root)
        findings += check_feeds(root)
    if args.scope:
        findings = [f for f in findings
                    if any(f["path"].startswith(s) for s in args.scope)]
    findings.sort(key=lambda f: (f["kind"], f["path"], f["line"], f["ref"]))

    known = set()
    if args.baseline:
        try:
            base = json.loads(Path(args.baseline).read_text())
            known = {tuple(x) for x in
                     (key(f) for f in base.get("findings", []))}
        except (OSError, ValueError) as e:
            print(f"error: cannot read baseline: {e}", file=sys.stderr)
            return 2
    new = [f for f in findings if key(f) not in known]

    report = {
        "tool": "dangle_check",
        "mode": args.mode,
        "root": str(root),
        "findings": findings,
        "counts": {
            "total": len(findings),
            "new": len(new),
            "known": len(findings) - len(new),
            "by_kind": {},
        },
    }
    for f in findings:
        by = report["counts"]["by_kind"]
        by[f["kind"]] = by.get(f["kind"], 0) + 1

    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(payload + "\n")
    if args.write_baseline:
        base = dict(report)
        base["root"] = "."
        base["scope"] = args.scope
        Path(args.write_baseline).write_text(
            json.dumps(base, indent=2, ensure_ascii=False) + "\n")
    print(payload)
    if args.report_only:
        return 0
    return 1 if new else 0


if __name__ == "__main__":
    sys.exit(main())
